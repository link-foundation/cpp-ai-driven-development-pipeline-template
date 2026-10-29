#!/usr/bin/env python3
"""Resolve existing workflow action tags and retain upstream manifests for review.

Run from the repository root. Does not edit workflows or execute upstream code.
The generated pin inventory is committed with the issue 16 case study.
"""

import base64
import json
import re
import subprocess
from pathlib import Path


def api(endpoint):
    return json.loads(subprocess.check_output(["gh", "api", endpoint], text=True))


def main():
    actions = set()
    for workflow in Path(".github/workflows").glob("*.yml"):
        actions.update(re.findall(r"^\s*(?:- )?uses: (\S+)", workflow.read_text(), re.M))
    rows = []
    output = Path("ci-logs/action-manifests")
    output.mkdir(parents=True, exist_ok=True)
    for action in sorted(actions):
        if action.startswith(("./", "docker://")):
            continue
        path, ref = action.split("@")
        # This action publishes v5.0.0 without a moving v5 tag.
        ref = {"actions/dependency-review-action@v5": "v5.0.0"}.get(action, ref)
        owner, repo, *subpath = path.split("/")
        repository = f"{owner}/{repo}"
        if re.fullmatch(r"[a-f0-9]{40}", ref):
            sha = ref
        else:
            tag = api(f"repos/{repository}/git/ref/tags/{ref}")["object"]
            while tag["type"] == "tag":
                tag = api(f"repos/{repository}/git/tags/{tag['sha']}")["object"]
            assert tag["type"] == "commit", action
            sha = tag["sha"]
        manifest = "/".join([*subpath, "action.yml"])
        response = api(f"repos/{repository}/contents/{manifest}?ref={sha}")
        content = base64.b64decode(response["content"]).decode()
        (output / f"{path.replace('/', '-')}.yml").write_text(content)
        rows.append({"action": path, "previous_ref": ref, "sha": sha,
                     "manifest": f"https://github.com/{repository}/blob/{sha}/{manifest}"})
        print(f"{action} -> {sha}", flush=True)
    destination = Path("docs/case-studies/issue-16/action-pins.json")
    destination.write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()
