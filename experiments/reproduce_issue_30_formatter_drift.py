#!/usr/bin/env python3
"""Run the formatter regression against the original baseline, then this checkout."""

import importlib.util
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    spec = importlib.util.spec_from_file_location(
        "dependency_tests", ROOT / "scripts/tests/test_dependency_pins.py"
    )
    tests = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tests)
    with tempfile.TemporaryDirectory(prefix="issue-30-") as directory:
        baseline = Path(directory)
        for name in (".pre-commit-config.yaml", "scripts/requirements-ci.txt"):
            path = baseline / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(subprocess.check_output([
                "git", "show", f"256589058fd5cdc1659391be4011b506f62d657b:{name}"
            ], cwd=ROOT))
        tests.ROOT = baseline
        try:
            tests.test_hook_formatter_matches_ci()
        except AssertionError:
            print("PASS: regression detects baseline formatter mismatch (20.1.8 vs 23.1.5)")
        else:
            raise AssertionError("Regression must fail against the original baseline")
    tests.ROOT = ROOT
    tests.test_hook_formatter_matches_ci()
    print("PASS: regression accepts the updated matching formatter versions")


if __name__ == "__main__":
    main()
