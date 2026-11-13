#!/usr/bin/env python3
"""Run focused new tests against the original implementation, then restore it.

Run from the repository root with the test environment's Python. No large
payload, network request, or compiler is used. Results go to experiments/.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ["detect_code_changes.py", "pack_nuget.py", "publish-release.sh", "check-nuget-package.sh"]
TESTS = [
    "scripts/tests/test_pr_checks.py::test_shared_requirements_enable_every_validation_gate",
    "scripts/tests/test_pr_checks.py::test_requirements_only_pull_request_outputs",
    "scripts/tests/test_check_nuget_size.py::test_pack_rejects_over_budget_package",
    "scripts/tests/test_check_nuget_size.py::test_restore_check_rejects_before_any_dotnet_call",
    "scripts/tests/test_publish_release.py::test_413_is_non_retryable_and_stops_publication",
    "scripts/tests/test_publish_release.py::test_pre_push_gate_checks_packages_from_an_alternate_packer",
]


def main():
    saved = {ROOT / "scripts" / name: (ROOT / "scripts" / name).read_bytes() for name in FILES}
    try:
        for path in saved:
            path.write_bytes(subprocess.check_output(
                ["git", "show", f"29d8cf2:scripts/{path.name}"], cwd=ROOT))
        with (ROOT / "experiments" / "before-fix.log").open("w") as log:
            result = subprocess.run([sys.executable, "-m", "pytest", "-q", *TESTS], cwd=ROOT,
                                    stdout=log, stderr=subprocess.STDOUT)
        if result.returncode != 1:
            raise RuntimeError(f"Expected regression failures; pytest exited {result.returncode}")
    finally:
        for path, contents in saved.items():
            path.write_bytes(contents)
    print("Original implementation fails the regression cases; working files restored.")


if __name__ == "__main__":
    main()
