#!/usr/bin/env python3
"""Compare the committed universal resolution against current PyPI metadata."""

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dev/log/issues/30/pulls/31"


def main():
    previous = {
        row["name"].lower().replace("_", "-").replace(".", "-"): row["previous"]
        for row in json.loads((OUT / "raw/pypi-direct.json").read_text())
    }
    records = []
    for name, version in re.findall(
        r"^([\w-]+)==([^\s;]+)", (ROOT / "scripts/constraints.txt").read_text(), re.M
    ):
        with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json") as response:
            info = json.load(response)["info"]
        records.append({"name": name, "before": previous.get(name, "unlocked"),
                        "resolved": version, "latest": info["version"],
                        "requires_dist": info["requires_dist"],
                        "requires_python": info["requires_python"]})
    (OUT / "raw/pypi-lock.json").write_text(json.dumps(records, indent=2) + "\n")
    lines = ["# Complete Python registry comparison", "",
             "Queried from PyPI on 2026-11-14 UTC. Before refers to the original direct manifests;",
             "transitives had no committed resolution. All rows now have exact constraints.", "",
             "| Dependency | Before | Resolved | Latest stable on PyPI |",
             "| --- | --- | --- | --- |"]
    for row in records:
        lines.append(f"| [{row['name']}](https://pypi.org/project/{row['name']}/) | "
                     f"{row['before']} | {row['resolved']} | {row['latest']} |")
    mismatches = [row for row in records if row["resolved"] != row["latest"]]
    lines.extend(["", f"Packages: {len(records)}. Versions below latest: {len(mismatches)}.", ""])
    (OUT / "PYTHON-LOCK.md").write_text("\n".join(lines))
    print(f"Compared {len(records)} packages; {len(mismatches)} versions below latest")
    for row in mismatches:
        print(row["name"], row["resolved"], "latest", row["latest"])


if __name__ == "__main__":
    main()
