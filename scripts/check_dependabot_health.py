#!/usr/bin/env python3
"""Fail when an open Dependabot PR exceeds its review age budget.

Uses only the standard library and the authenticated gh CLI. All API calls are
read-only and paginated. GITHUB_REPOSITORY selects the repository;
DEPENDABOT_MAX_OPEN_DAYS defaults to 14. CI_VERBOSE=true logs candidate ages.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

DEPENDABOT_LOGIN = "dependabot[bot]"


def annotation(message: str) -> None:
    """Escape API-sourced text so it stays within one workflow annotation."""
    escaped = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::error title=Dependabot health::{escaped}")


def fetch_open_pulls(repository: str) -> list[dict]:
    result = subprocess.run(
        ["gh", "api", "--paginate", "--slurp",
         f"repos/{repository}/pulls?state=open&per_page=100"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(f"Could not list open pull requests: {result.stderr.strip()}")
    pages = json.loads(result.stdout)
    if not isinstance(pages, list) or any(not isinstance(page, list) for page in pages):
        raise ValueError("Expected paginated arrays of open pull requests")
    pulls = [pull for page in pages for pull in page]
    if any(not isinstance(pull, dict) for pull in pulls):
        raise ValueError("Expected pull request objects")
    return pulls


def stale_pulls(pulls: list[dict], now: datetime, max_open_days: int) -> list[tuple[dict, float]]:
    stale = []
    for pull in pulls:
        if pull.get("state") != "open" or (pull.get("user") or {}).get("login") != DEPENDABOT_LOGIN:
            continue
        created = datetime.fromisoformat(pull["created_at"].replace("Z", "+00:00"))
        if created.tzinfo is None:
            raise ValueError(f"PR #{pull['number']} has no creation timezone")
        age = now - created
        if os.environ.get("CI_VERBOSE", "").lower() == "true":
            print(f"Dependabot PR #{pull['number']}: {age.total_seconds() / 86400:.2f} days open")
        if age > timedelta(days=max_open_days):
            stale.append((pull, age.total_seconds() / 86400))
    return stale


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--max-open-days", default=os.environ.get("DEPENDABOT_MAX_OPEN_DAYS", "14"))
    args = parser.parse_args(argv)
    try:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
            raise ValueError("Set GITHUB_REPOSITORY or --repository to owner/repo")
        max_days = int(args.max_open_days)
        if max_days <= 0:
            raise ValueError("DEPENDABOT_MAX_OPEN_DAYS must be a positive integer")
        pulls = fetch_open_pulls(args.repository)
        stale = stale_pulls(pulls, datetime.now(timezone.utc), max_days)
        for pull, age in stale:
            annotation(
                f"#{pull['number']} {pull['title']} has been open for {age:.2f} days "
                f"(limit {max_days}): {pull['html_url']}. "
                "Review and merge it if current, or close it if obsolete so Dependabot can propose fresh updates."
            )
    except (OSError, RuntimeError, ValueError, KeyError, TypeError, OverflowError) as error:
        annotation(f"Health check could not complete: {error}")
        return 1
    if stale:
        print(f"{len(stale)} stale Dependabot pull request(s).")
        return 1
    print(f"No open Dependabot pull requests older than {max_days} days.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
