#!/usr/bin/env python3
"""Bounded smoke test: the queue exception preserves unrelated lint failures.

Run with actionlint 1.7.12 and shellcheck on PATH. Uses only temporary files.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = """name: Queue fixture
on: push
jobs:
  example:
    runs-on: ubuntu-24.04
    concurrency:
      group: repository-main-write
      cancel-in-progress: false
      queue: max
    steps:
      - run: echo ok
"""


def main():
    assert shutil.which("actionlint") and shutil.which("shellcheck"), "Install both linters"
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "fixture.yml"
        for name, text, expected in [
            ("valid queue", WORKFLOW, 0),
            ("invalid queue", WORKFLOW.replace("queue: max", "queue: typo"), 1),
            ("unrelated syntax", WORKFLOW.replace("runs-on:", "runs-typo:"), 1),
            ("shellcheck", WORKFLOW.replace("echo ok", "echo $undefined"), 1),
            ("inline queue", WORKFLOW.replace("      queue: max", "      queue: {invalid: value}"), 1),
            ("quoted queue", WORKFLOW.replace("queue: max", "'queue': typo"), 1),
            ("mismatched quotes", WORKFLOW.replace("queue: max", "queue: \"max'"), 1),
            ("missing separator", WORKFLOW.replace("queue: max", "queue:max"), 1),
        ]:
            path.write_text(text)
            queue = subprocess.run([sys.executable, str(ROOT / "scripts/check_workflow_concurrency.py"),
                                    "--actionlint-compat", str(path)], capture_output=True, text=True)
            lint = subprocess.run(["actionlint", str(path)],
                                  capture_output=True, text=True)
            actual = int(bool(queue.returncode or lint.returncode))
            assert actual == expected, (name, queue.stdout, lint.stdout, lint.stderr)
            if name == "unrelated syntax":
                assert "runs-typo" in lint.stdout
            if name == "shellcheck":
                assert "shellcheck" in lint.stdout
            print(f"{name}: {'rejected' if actual else 'accepted'} as expected")
        workflows = []
        for source in sorted((ROOT / ".github/workflows").glob("*.yml")):
            target = Path(directory) / source.name
            shutil.copyfile(source, target)
            workflows.append(str(target))
        subprocess.run([sys.executable, str(ROOT / "scripts/check_workflow_concurrency.py"),
                        "--actionlint-compat", *workflows], check=True)
        subprocess.run(["actionlint", *workflows], check=True)
        print("All repository workflows: actionlint and shellcheck passed")


if __name__ == "__main__":
    main()
