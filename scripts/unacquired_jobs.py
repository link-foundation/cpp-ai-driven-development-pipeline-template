#!/usr/bin/env python3
"""Find, report and re-run the jobs of a run that GitHub never started.

When hosted capacity runs out (macOS arm64 is the usual case), GitHub gives up
on a queued job with the annotation "The job was not acquired by Runner of
type hosted even after multiple attempts". The job ends `cancelled` (sometimes
`failure`) with no steps and no runner. No code ran, yet the build gate, the
release and the Pipeline Status gate treat it like a test failure, and nothing
retried it (issue #19).

A job counts as *unacquired* only when all of these hold:

* its conclusion is `cancelled` or `failure`;
* it has no steps and no runner (`runner_name` is empty);
* one of its check-run annotations says it "was not acquired by Runner".

The annotation is what separates an infrastructure failure from a queued job
that a newer push or a person cancelled: both of those also end without a
runner and without steps, and neither should be re-run. A job that ran steps
and failed is never unacquired.

Subcommands:

``report``
    Used by scripts/check-pipeline-status.sh while the run is in progress.
    Prints one ``::error`` annotation naming the unacquired jobs of the current
    attempt (``GITHUB_REPOSITORY``, ``GITHUB_RUN_ID``, ``GITHUB_RUN_ATTEMPT``),
    so the gate states the cause. It never changes the exit status of the
    gate: nothing was tested, so the gate stays red. API errors only warn.

``rerun``
    Used by .github/workflows/rerun-infrastructure-failures.yml after a run
    completed. Runs ``gh run rerun --failed`` when the given attempt has an
    unacquired job and fewer than ``--max-attempts`` attempts were made;
    ``--failed`` also re-runs the jobs that depend on it, so the build,
    release and status gates are evaluated again. When the attempts are used
    up it exits 1 with the command a maintainer can run later.

Set ``CI_VERBOSE=true`` to print every candidate job and its annotations.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Callable, Dict, Iterable, List, Mapping

NOT_ACQUIRED = "was not acquired by Runner"
FAILED_CONCLUSIONS = {"cancelled", "failure"}
MAX_ATTEMPTS = 3

Gh = Callable[..., str]


def verbose() -> bool:
    return os.environ.get("CI_VERBOSE", "").lower() == "true"


def never_started(job: Mapping) -> bool:
    """A failed or cancelled job that has neither steps nor a runner."""
    return (
        job.get("conclusion") in FAILED_CONCLUSIONS
        and not job.get("steps")
        and not (job.get("runner_name") or "")
    )


def unacquired(jobs: Iterable[Mapping], annotations: Mapping[int, List[str]]) -> List[str]:
    """Names of the jobs GitHub could not hand to a hosted runner.

    ``annotations`` maps a job id to the messages of its check-run annotations.
    """
    return [
        job["name"]
        for job in jobs
        if never_started(job)
        and any(NOT_ACQUIRED in message for message in annotations.get(job["id"], []))
    ]


def decide(names: List[str], attempt: int, max_attempts: int = MAX_ATTEMPTS) -> str:
    """Return ``rerun``, ``give-up`` or ``nothing`` for a completed attempt."""
    if not names:
        return "nothing"
    return "rerun" if attempt < max_attempts else "give-up"


def gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"gh {' '.join(args[:2])}: {result.stderr.strip()}")
    return result.stdout


def find_unacquired(repository: str, run_id: str, attempt: str, run_gh: Gh = gh) -> List[str]:
    """Read the attempt's jobs and the annotations of the jobs that never started."""
    pages = json.loads(
        run_gh(
            "api",
            "--paginate",
            "--slurp",
            f"repos/{repository}/actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100",
        )
    )
    jobs = [job for page in pages for job in page.get("jobs", [])]
    annotations: Dict[int, List[str]] = {}
    for job in jobs:
        if not never_started(job):
            continue
        found = json.loads(
            run_gh("api", f"repos/{repository}/check-runs/{job['id']}/annotations?per_page=100")
        )
        annotations[job["id"]] = [item.get("message", "") for item in found]
        if verbose():
            print(f"{job['name']} ({job.get('conclusion')}, no runner): {annotations[job['id']]}")
    return unacquired(jobs, annotations)


def report(options: argparse.Namespace, run_gh: Gh = gh) -> int:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    if not (repository and run_id and os.environ.get("GH_TOKEN")):
        if verbose():
            print("No GH_TOKEN or run context; skipping the runner-acquisition check.")
        return 0
    try:
        names = find_unacquired(repository, run_id, attempt, run_gh)
    except (RuntimeError, ValueError, KeyError) as error:
        print(f"::warning title=Runner acquisition not checked::{error}")
        return 0
    if names:
        print(
            f"::error title=Hosted runner not acquired::{', '.join(names)}. "
            "GitHub could not provide a runner, so no code ran in "
            f"{'this job' if len(names) == 1 else 'these jobs'}; this is an infrastructure "
            "failure, not a test failure. rerun-infrastructure-failures.yml re-runs it "
            f"automatically (up to {options.max_attempts} attempts); otherwise run "
            f"`gh run rerun {run_id} --failed --repo {repository}`."
        )
    return 0


def rerun(options: argparse.Namespace, run_gh: Gh = gh) -> int:
    names = find_unacquired(options.repository, options.run_id, str(options.attempt), run_gh)
    verdict = decide(names, options.attempt, options.max_attempts)
    listed = ", ".join(names)
    command = f"gh run rerun {options.run_id} --failed --repo {options.repository}"
    if verdict == "nothing":
        print(
            f"No runner-acquisition failures in attempt {options.attempt}; "
            "leaving the run as it is."
        )
        return 0
    if verdict == "give-up":
        print(
            f"::error title=Hosted runner not acquired::{listed} found no hosted runner "
            f"in {options.attempt} attempts. GitHub's runner capacity is outside this "
            f"repository: re-run it later with `{command}`."
        )
        return 1
    print(
        f"::warning title=Hosted runner not acquired::{listed} (attempt {options.attempt}); "
        "re-running the failed jobs and the jobs that depend on them."
    )
    if options.dry_run:
        print(f"Dry run: would run `{command}`.")
    else:
        run_gh("run", "rerun", str(options.run_id), "--failed", "--repo", options.repository)
    return 0


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--max-attempts", type=int, default=MAX_ATTEMPTS)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("report", help="annotate the unacquired jobs of the current run")
    rerun_parser = commands.add_parser("rerun", help="re-run a completed run's unacquired jobs")
    rerun_parser.add_argument("--repository", required=True)
    rerun_parser.add_argument("--run-id", required=True, type=int)
    rerun_parser.add_argument("--attempt", required=True, type=int)
    rerun_parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    options = parse_args(sys.argv[1:] if argv is None else argv)
    return report(options) if options.command == "report" else rerun(options)


if __name__ == "__main__":
    sys.exit(main())
