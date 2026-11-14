#!/usr/bin/env python3
"""Inventory the secret scanner's complete lock against npm's stable dist-tag."""

import concurrent.futures
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dev/log/issues/30/pulls/31"


def latest(name):
    url = "https://registry.npmjs.org/" + urllib.parse.quote(name, safe="") + "/latest"
    with urllib.request.urlopen(url) as response:
        info = json.load(response)
    return name, {"latest": info["version"], "engines": info.get("engines"),
                  "dependencies": info.get("dependencies", {})}


def main():
    lock = json.loads((ROOT / "package-lock.json").read_text())
    packages = {(path.rsplit("node_modules/", 1)[1], entry["version"])
                for path, entry in lock["packages"].items() if path}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        registry = dict(pool.map(latest, sorted({name for name, _ in packages})))
    records = [{"name": name, "resolved": version, **registry[name]}
               for name, version in sorted(packages)]
    (OUT / "raw/npm-lock.json").write_text(json.dumps(records, indent=2) + "\n")
    lines = ["# Complete npm registry comparison", "",
             "Queried 2026-11-14 UTC. All dependencies were previously unpinned npx inputs.",
             "The npm CLI's own bundled tree is separately inventoried in `raw/npm-cli-audit.json`.", "",
             "| Dependency | Before | Locked | Latest stable npm dist-tag |",
             "| --- | --- | --- | --- |"]
    for row in records:
        lines.append(f"| [{row['name']}](https://registry.npmjs.org/{row['name']}) | "
                     f"unlocked | {row['resolved']} | {row['latest']} |")
    (OUT / "NPM-LOCK.md").write_text("\n".join(lines) + "\n")
    mismatches = [row for row in records if row["resolved"] != row["latest"]]
    print(f"Compared {len(records)} resolved packages; {len(mismatches)} below latest")
    for row in mismatches:
        print(row["name"], row["resolved"], "->", row["latest"])


if __name__ == "__main__":
    main()
