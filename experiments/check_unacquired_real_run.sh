#!/usr/bin/env bash
# Issue #19: run scripts/unacquired_jobs.py against a real run in which a
# macOS job never got a hosted runner, without re-running anything.
# links-notation run 41477660740: `kotlin / ios` was cancelled after 37 min
# with "The job was not acquired by Runner of type hosted ...".
# Expected: one "Hosted runner not acquired::kotlin / ios" warning and a
# "Dry run: would run `gh run rerun 41477660740 --failed ...`" line.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CI_VERBOSE=true python3 "$ROOT/scripts/unacquired_jobs.py" rerun \
  --repository "${1:-link-foundation/links-notation}" \
  --run-id "${2:-41477660740}" --attempt "${3:-1}" --dry-run
