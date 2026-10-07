"""Policy tests for .github/workflows: the invariants that docs/ci-cd.md
promises and that actionlint and zizmor do not check.

The workflows are parsed as text (jobs at two spaces, steps at six), like the
Python template does, so the tests need no YAML library.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

import pytest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = sorted(path for path in (ROOT / ".github" / "workflows").iterdir()
                   if path.suffix in {".yml", ".yaml"})
WRITE_GROUP = "group: ${{ github.workflow }}-main-write"
# Jobs that push the release commit and tag keep the checkout credentials.
PUSHING_JOBS = {"auto-release", "manual-release"}


def jobs(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8")
    body = text.split("\njobs:\n", 1)[1]
    parts = re.split(r"^  ([A-Za-z0-9_-]+):\n", body, flags=re.MULTILINE)
    return dict(zip(parts[1::2], parts[2::2]))


def steps(job: str) -> List[str]:
    # Comments before the next job would otherwise end up in the last step.
    code = re.sub(r"^\s*#.*\n", "", job, flags=re.MULTILINE)
    return re.split(r"^      - ", code, flags=re.MULTILINE)[1:]


def all_steps():
    for path in WORKFLOWS:
        for name, job in jobs(path).items():
            for step in steps(job):
                yield path.name, name, step


def test_workflows_are_found() -> None:
    names = {path.name for path in WORKFLOWS}
    assert {"release.yml", "docs.yml", "security.yml", "links.yml", "workflows.yml"} <= names


def floating_runner_labels(text: str) -> list[str]:
    fields = re.findall(r"^\s*(?:- )?(?:runs-on|os):[^\n]*(?:\n[ \t]+-[^\n]*)*",
                        text, re.MULTILINE)
    return [field for field in fields
            if re.search(r"[a-z]+-latest\b", re.sub(r"#[^\n]*", "", field))]


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_runner_images_are_explicit(path: Path) -> None:
    assert not floating_runner_labels(path.read_text()), path.name


@pytest.mark.parametrize("field", ["runs-on: ubuntu-latest", "os: macos-latest",
                                  "os: [ubuntu-24.04, windows-latest]",
                                  "runs-on:\n      - ubuntu-latest"])
def test_floating_runner_policy_catches_scalar_and_list_labels(field: str) -> None:
    assert floating_runner_labels(field)


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_git_initial_branch_is_set_before_checkout(path: Path) -> None:
    global_config = path.read_text().split("\njobs:\n", 1)[0]
    assert "\nenv:\n" in global_config, path.name
    assert "GIT_CONFIG_COUNT: '1'" in global_config, path.name
    assert "GIT_CONFIG_KEY_0: init.defaultBranch" in global_config, path.name
    assert "GIT_CONFIG_VALUE_0: main" in global_config, path.name


def test_sensitive_action_namespaces_require_hash_pins() -> None:
    policy = (ROOT / ".github/zizmor.yml").read_text()
    for namespace in ("lycheeverse", "zizmorcore", "NuGet"):
        assert f"{namespace}/*: ref-pin" not in policy
    assert "'*': hash-pin" in policy


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_least_privilege_default(path: Path) -> None:
    assert "\npermissions:\n  contents: read\n" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_every_job_has_a_timeout(path: Path) -> None:
    for name, job in jobs(path).items():
        assert re.search(r"^    timeout-minutes: \d+$", job, re.MULTILINE), f"{path.name}:{name}"


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_pipeline_status_needs_every_other_job(path: Path) -> None:
    workflow = jobs(path)
    status = workflow.pop("pipeline-status")
    needs = set(re.findall(r"^      - ([a-z0-9-]+)$", status.split("    steps:")[0], re.MULTILINE))
    needs |= set(re.findall(r"[\[ ,]([a-z0-9-]+)(?=[,\]])", status.split("\n    needs:")[1].split("\n")[0]))
    assert needs == set(workflow), f"{path.name}: pipeline-status misses {set(workflow) - needs}"
    assert "    if: always()" in status


def test_checkouts_drop_credentials_except_in_pushing_jobs() -> None:
    for workflow, job, step in all_steps():
        if not step.startswith("uses: actions/checkout@"):
            continue
        if job in PUSHING_JOBS:
            assert "persist-credentials: true" in step, f"{workflow}:{job}"
        else:
            assert "persist-credentials: false" in step, f"{workflow}:{job}"


def test_jobs_that_write_share_the_main_write_group() -> None:
    for name, job in jobs(ROOT / ".github/workflows/release.yml").items():
        # The preflight only probes (an invalid ref: 422) and never writes.
        if "contents: write" in job and name != "release-preflight":
            assert WRITE_GROUP in job and "cancel-in-progress: false" in job, name


def test_third_party_actions_are_pinned_by_hash() -> None:
    trusted = tuple(f"{namespace}/" for namespace in re.findall(
        r"^        ([a-z0-9-]+)/\*: ref-pin$",
        (ROOT / ".github/zizmor.yml").read_text(encoding="utf-8"), re.MULTILINE))
    for path in WORKFLOWS:
        for action in re.findall(r"^ +(?:- )?uses: (\S+)", path.read_text(encoding="utf-8"),
                                 re.MULTILINE):
            if action.startswith("docker://"):
                assert "@sha256:" in action, f"{path.name}: {action}"
            elif not action.startswith(trusted):
                assert re.search(r"@[0-9a-f]{40}$", action), f"{path.name}: {action}"


def test_run_blocks_do_not_interpolate_untrusted_input() -> None:
    unsafe = re.compile(r"\$\{\{\s*(?:inputs\.|github\.event\.|github\.(?:base|head)_ref)")
    for workflow, job, step in all_steps():
        run = step.split("run:", 1)[1] if "run:" in step else ""
        assert not unsafe.search(run), f"{workflow}:{job} interpolates untrusted input:\n{run}"


def test_packaging_steps_get_the_release_naming() -> None:
    """Every step that packs release assets packs them under the configured
    names, so the build job, the publish steps, the preflight and the release
    check agree on the NuGet id and the archive name."""
    packaging = [(job, step) for workflow, job, step in all_steps()
                 if re.search(r"package_release\.py|publish-release\.sh", step)]
    assert len(packaging) == 3
    for job, step in packaging:
        assert "NUGET_PACKAGE_ID: ${{ vars.NUGET_PACKAGE_ID }}" in step, job
        assert "RELEASE_ARCHIVE_BASENAME: ${{ vars.RELEASE_ARCHIVE_BASENAME }}" in step, job
    for workflow, job, step in all_steps():
        if re.search(r"preflight-credentials\.sh|check_release_needed\.py", step):
            assert "NUGET_PACKAGE_ID: ${{ vars.NUGET_PACKAGE_ID }}" in step, job


def test_publishing_secrets_are_step_scoped() -> None:
    for path in WORKFLOWS:
        text = path.read_text(encoding="utf-8")
        assert "secrets." not in text.split("\njobs:\n", 1)[0], path.name
        for name, job in jobs(path).items():
            job_env = re.search(r"^    env:\n((?:      .*\n)+)", job, re.MULTILINE)
            if job_env:
                secrets = set(re.findall(r"secrets\.([A-Z_]+)", job_env.group(1)))
                # Codecov's token is harmless (upload only) and gates a step.
                assert secrets <= {"CODECOV_TOKEN"}, f"{path.name}:{name} {secrets}"


@pytest.mark.parametrize("name", sorted(PUSHING_JOBS))
def test_both_publish_jobs_support_trusted_nuget_and_secret_fallback(name: str) -> None:
    job = jobs(ROOT / ".github/workflows/release.yml")[name]
    assert "      id-token: write" in job.split("    steps:", 1)[0]
    login = [step for step in steps(job) if "uses: NuGet/login@" in step]
    assert len(login) == 1
    assert "id: nuget-login" in login[0]
    assert "vars.NUGET_PUBLISH == 'true'" in login[0]
    assert "vars.NUGET_USER != ''" in login[0]
    assert "user: ${{ vars.NUGET_USER }}" in login[0]
    publish = next(step for step in steps(job) if "run: bash scripts/publish-release.sh" in step)
    assert "NUGET_API_KEY: ${{ steps.nuget-login.outputs.NUGET_API_KEY || secrets.NUGET_API_KEY }}" in publish
    assert job.index("uses: NuGet/login@") < job.index("run: bash scripts/publish-release.sh")
    if name == "auto-release":
        assert "steps.check.outputs.should_release == 'true'" in login[0]
        assert "steps.check.outputs.nuget_published != 'true'" in login[0]
    else:
        assert "steps.version.outputs.version_committed == 'true'" in login[0]
        assert "steps.version.outputs.already_released == 'true'" in login[0]


def test_oidc_permission_is_limited_to_publishing_jobs() -> None:
    for path in WORKFLOWS:
        assert "id-token: write" not in path.read_text().split("\njobs:\n", 1)[0]
        for name, job in jobs(path).items():
            if "id-token: write" in job:
                # GitHub Pages already uses OIDC independently of NuGet.
                assert (path.name == "release.yml" and name in PUSHING_JOBS) or (
                    path.name == "docs.yml" and name == "deploy")
    preflight = jobs(ROOT / ".github/workflows/release.yml")["release-preflight"]
    assert "NUGET_USER: ${{ vars.NUGET_USER }}" in preflight
