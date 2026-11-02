"""Regression tests for jobs that never got a hosted runner (issue #19).

A fake ``gh`` on PATH serves the jobs and annotations of a run from JSON
fixtures and records ``gh run rerun``, so the script and the status gate run
end to end without the network. The unacquired job mirrors the real one from
link-foundation/links-notation run 41477660740 (`kotlin / ios`).
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

import pytest

import unacquired_jobs as uj

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "unacquired_jobs.py"
GATE = ROOT / "scripts" / "check-pipeline-status.sh"
NOT_ACQUIRED = (
    "The job was not acquired by Runner of type hosted even after multiple attempts"
)

FAKE_GH = """#!/usr/bin/env python3
import json, os, re, sys
data = os.environ["FAKE_GH_DIR"]
args = sys.argv[1:]
with open(os.path.join(data, "calls.log"), "a") as log:
    log.write(" ".join(args) + "\\n")
if args[:2] == ["run", "rerun"]:
    sys.exit(0)
path = next(arg for arg in args if arg.startswith("repos/"))
if os.path.exists(os.path.join(data, "fail")):
    sys.stderr.write("HTTP 403: Resource not accessible by integration")
    sys.exit(1)
if "/jobs" in path:
    with open(os.path.join(data, "jobs.json")) as handle:
        print(json.dumps([{"jobs": json.load(handle)}]))
else:
    job = re.search(r"check-runs/(\\d+)/annotations", path).group(1)
    name = os.path.join(data, f"annotations-{job}.json")
    print(open(name).read() if os.path.exists(name) else "[]")
"""


def job(job_id: int, name: str, conclusion: str, ran: bool) -> Dict:
    return {
        "id": job_id,
        "name": name,
        "conclusion": conclusion,
        "steps": [{"name": "Set up job", "conclusion": conclusion}] if ran else [],
        "runner_name": "GitHub Actions 1000" if ran else "",
    }


UNACQUIRED = job(1, "Test (macos-appleclang)", "cancelled", ran=False)
REAL_FAILURE = job(2, "Test (linux-gcc)", "failure", ran=True)
QUEUED_AND_SUPERSEDED = job(3, "Test (windows-msvc)", "cancelled", ran=False)
PASSED = job(4, "Lint and Format Check", "success", ran=True)


@pytest.fixture
def fake_gh(tmp_path: Path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH.replace("python3", sys.executable, 1), encoding="utf-8")
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    data = tmp_path / "data"
    data.mkdir()

    def serve(jobs: List[Dict], annotated: Dict[int, str]) -> Path:
        (data / "jobs.json").write_text(json.dumps(jobs), encoding="utf-8")
        for job_id, message in annotated.items():
            (data / f"annotations-{job_id}.json").write_text(
                json.dumps([{"message": message, "annotation_level": "failure"}]),
                encoding="utf-8",
            )
        return data

    env = {
        **os.environ,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "FAKE_GH_DIR": str(data),
    }
    return serve, env, data


def calls(data: Path) -> List[str]:
    log = data / "calls.log"
    return log.read_text(encoding="utf-8").splitlines() if log.exists() else []


def test_only_unstarted_jobs_with_the_annotation_are_unacquired() -> None:
    annotations = {1: [NOT_ACQUIRED], 2: [NOT_ACQUIRED], 3: ["The operation was canceled."]}
    jobs = [UNACQUIRED, REAL_FAILURE, QUEUED_AND_SUPERSEDED, PASSED]

    assert uj.unacquired(jobs, annotations) == ["Test (macos-appleclang)"]


def test_a_failure_conclusion_without_a_runner_also_counts() -> None:
    failed = {**UNACQUIRED, "conclusion": "failure"}

    assert uj.unacquired([failed], {1: [NOT_ACQUIRED]}) == [failed["name"]]


@pytest.mark.parametrize(
    ("names", "attempt", "expected"),
    [([], 1, "nothing"), (["a"], 1, "rerun"), (["a"], 2, "rerun"), (["a"], 3, "give-up")],
)
def test_decide_reruns_at_most_twice(names: List[str], attempt: int, expected: str) -> None:
    assert uj.decide(names, attempt) == expected


def run_rerun(env: Dict[str, str], attempt: int = 1) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "rerun", "--repository", "owner/repo",
         "--run-id", "42", "--attempt", str(attempt)],
        env=env, capture_output=True, text=True, check=False,
    )


def test_rerun_reruns_failed_jobs_when_a_runner_was_not_acquired(fake_gh) -> None:
    serve, env, data = fake_gh
    serve([UNACQUIRED, REAL_FAILURE, PASSED], {1: NOT_ACQUIRED})

    completed = run_rerun(env)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Hosted runner not acquired::Test (macos-appleclang) (attempt 1)" in completed.stdout
    assert "run rerun 42 --failed --repo owner/repo" in calls(data)
    # Only jobs without steps are inspected for annotations.
    assert [call for call in calls(data) if "annotations" in call] == [
        "api repos/owner/repo/check-runs/1/annotations?per_page=100"
    ]


def test_rerun_leaves_real_failures_and_supersedes_alone(fake_gh) -> None:
    serve, env, data = fake_gh
    serve([REAL_FAILURE, QUEUED_AND_SUPERSEDED], {2: NOT_ACQUIRED})

    completed = run_rerun(env)

    assert completed.returncode == 0, completed.stderr
    assert "No runner-acquisition failures in attempt 1" in completed.stdout
    assert not [call for call in calls(data) if call.startswith("run rerun")]


def test_rerun_gives_up_on_the_third_attempt_with_the_manual_command(fake_gh) -> None:
    serve, env, data = fake_gh
    serve([UNACQUIRED], {1: NOT_ACQUIRED})

    completed = run_rerun(env, attempt=3)

    assert completed.returncode == 1
    assert "found no hosted runner in 3 attempts" in completed.stdout
    assert "`gh run rerun 42 --failed --repo owner/repo`" in completed.stdout
    assert not [call for call in calls(data) if call.startswith("run rerun")]


def run_gate(env: Dict[str, str], needs: Dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(GATE)],
        cwd=ROOT,
        env={
            **{key: value for key, value in env.items() if key != "GITHUB_REF"},
            "NEEDS_JSON": json.dumps({name: {"result": r} for name, r in needs.items()}),
            "RUN_SHA": "1" * 40,
            "BRANCH_HEAD_SHA": "1" * 40,
            "BRANCH_NAME": "main",
            "WORKFLOW_FILE": str(ROOT / ".github/workflows/release.yml"),
            "GH_TOKEN": "token",
            "GITHUB_REPOSITORY": "owner/repo",
            "GITHUB_RUN_ID": "42",
            "GITHUB_RUN_ATTEMPT": "2",
        },
        capture_output=True,
        text=True,
        check=False,
    )


def test_status_gate_stays_red_and_names_the_infrastructure_cause(fake_gh) -> None:
    serve, env, data = fake_gh
    serve([UNACQUIRED, PASSED], {1: NOT_ACQUIRED})

    completed = run_gate(env, {"lint": "success", "test": "cancelled", "build": "skipped"})

    assert completed.returncode == 1, completed.stdout
    assert "Pipeline has cancelled jobs::test" in completed.stdout
    assert (
        "::error title=Hosted runner not acquired::Test (macos-appleclang). "
        "GitHub could not provide a runner" in completed.stdout
    )
    assert "api --paginate --slurp repos/owner/repo/actions/runs/42/attempts/2/jobs?per_page=100" in calls(data)


def test_status_gate_does_not_blame_infrastructure_for_a_real_failure(fake_gh) -> None:
    serve, env, _ = fake_gh
    serve([REAL_FAILURE, PASSED], {})

    completed = run_gate(env, {"lint": "success", "test": "failure"})

    assert completed.returncode == 1
    assert "Pipeline failed::Failed jobs: test" in completed.stdout
    assert "Hosted runner not acquired" not in completed.stdout


def test_status_gate_skips_the_api_when_the_pipeline_passed(fake_gh) -> None:
    _, env, data = fake_gh

    completed = run_gate(env, {"lint": "success", "test": "success"})

    assert completed.returncode == 0, completed.stdout
    assert calls(data) == []


def test_status_gate_survives_an_unreadable_job_list(fake_gh) -> None:
    serve, env, data = fake_gh
    serve([UNACQUIRED], {1: NOT_ACQUIRED})
    (data / "fail").write_text("", encoding="utf-8")

    completed = run_gate(env, {"test": "cancelled"})

    assert completed.returncode == 1
    assert "Pipeline has cancelled jobs::test" in completed.stdout
    assert "::warning title=Runner acquisition not checked::" in completed.stdout


def test_status_gate_without_a_token_does_not_call_the_api(fake_gh) -> None:
    _, env, data = fake_gh
    env = {key: value for key, value in env.items() if key != "GH_TOKEN"}
    completed = subprocess.run(
        ["bash", str(GATE)],
        cwd=ROOT,
        env={**env, "NEEDS_JSON": '{"test":{"result":"failure"}}', "GITHUB_RUN_ID": "42"},
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    assert calls(data) == []
