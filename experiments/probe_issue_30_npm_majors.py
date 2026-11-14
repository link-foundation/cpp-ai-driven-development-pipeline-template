#!/usr/bin/env python3
"""Bounded API compatibility probe for latest secretlint transitive majors.

Run with Node 26.13.1/npm on PATH. Installs only the 83-package scanner tree
under ignored build/, never alters the real lock, and never runs stress inputs.
"""

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dev/log/issues/30/pulls/31/raw"


def main():
    project = json.loads((ROOT / "package.json").read_text())
    records = json.loads((OUT / "npm-lock.json").read_text())
    project.setdefault("overrides", {}).update({
        row["name"]: row["latest"] for row in records
        if row["resolved"] != row["latest"]
    })
    scratch = ROOT / "build/npm-major-probe"
    scratch.mkdir(parents=True, exist_ok=True)
    (scratch / "package.json").write_text(json.dumps(project, indent=2) + "\n")
    shutil.copyfile(ROOT / ".secretlintrc.json", scratch / ".secretlintrc.json")
    (scratch / "clean.txt").write_text("This bounded fixture contains no credentials.\n")
    # Deliberately synthetic scanner fixture; contains no usable key material.
    (scratch / "finding.txt").write_text(
        "-----BEGIN " + "PRIVATE KEY-----\n" + "MI" + "a" * 118
        + "\n-----END " + "PRIVATE KEY-----\n"
    )
    with (OUT / "npm-major-probe.log").open("w") as log:
        install = subprocess.run(
            ["npm", "install", "--ignore-scripts", "--no-fund", "--no-audit"],
            cwd=scratch, stdout=log, stderr=subprocess.STDOUT, check=False,
        )
        log.write(f"\ninstall exit: {install.returncode}\n")
        log.flush()
        if install.returncode == 0:
            scan = subprocess.run(
                ["node", "node_modules/secretlint/bin/secretlint.js", "clean.txt"],
                cwd=scratch, stdout=log, stderr=subprocess.STDOUT, check=False,
            )
            log.write(f"\nclean-file scan exit: {scan.returncode}\n")
            print(f"Latest-major probe scan exit: {scan.returncode}")
            for formatter in ("stylish", "table", "pretty-error", "json", "github"):
                log.write(f"\nFormatter: {formatter}\n")
                log.flush()
                result = subprocess.run(
                    ["node", "node_modules/secretlint/bin/secretlint.js",
                     "finding.txt", "--format", formatter],
                    cwd=scratch, stdout=log, stderr=subprocess.STDOUT, check=False,
                )
                log.write(f"finding scan exit: {result.returncode} (expected 1)\n")
                print(f"{formatter}: {result.returncode} (expected 1)")


if __name__ == "__main__":
    main()
