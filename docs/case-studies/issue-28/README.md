# Dependabot CI and health checks (issue #28)

Work plan and acceptance evidence for
[issue #28](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/issues/28),
implemented in [PR #29](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/pull/29).
The issue has no comments or required sub-issues; #26 and #27 are reproducing
Dependabot PRs, and the hive-mind links supply background and a reference design.

## Requirements and verification plan

- [x] Exempt PRs authored by `dependabot[bot]` from changelog fragments using
  `github.event.pull_request.user.login`. Keep human PRs subject to the check,
  including human PRs with a `dependabot/` branch or a bot-triggered rerun.
  Verify both repository layouts and dependency manifest/action changes.
- [x] Read zizmor's version from `scripts/requirements-security.txt` in both
  workflow audit passes and local reproduction instructions. Preserve both
  audit policies and make requirements updates trigger workflow auditing.
  Execute the workflow commands with a fake pipx and changed requirements.
- [x] Report open Dependabot PRs older than 14 days in a daily/manual,
  read-only workflow. Allow a positive configurable day limit; paginate all
  PRs, ignore human/closed PRs, and fail visibly on API/configuration errors.
  Verify the age boundary, pagination, diagnostics and a live read-only check.
- [x] Add a patch changelog fragment for the existing automatic release flow;
  document the exception, single pin and health configuration.

Final review checks the complete PR diff, that main is included and the working
tree is clean, and all CI checks for the final commit before marking it ready.
The PR description records the final CI results and commit; this document
records the implementation and reproducible local checks.

## Root cause evidence

Downloaded the original workflow logs locally under `ci-logs/`:

- Run [43402801047](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/runs/43402801047),
  log line 2995: missing changelog fragment; lines 2231–2238:
  `Unaudited workflow tool: zizmor==1.31.1`; line 5718: failed jobs
  `changelog, script-tests`.
- Run [43402827872](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/runs/43402827872),
  log line 2014: missing changelog fragment; line 5802: failed job `changelog`.

The first PR changes the audited requirement to zizmor 1.32.0 but leaves
the workflow's two executable pins and reproduction comment at 1.31.1.
The audit coverage test correctly detects this drift. The changelog checker
only exempts release branch prefixes, so ordinary Dependabot updates fail it.
The existing workflows do not monitor the age of open bot PRs.

## Verification

The nine new changelog/workflow regression cases failed on the original
implementation (`ci-logs/issue-28-before.log`). With the fix, the focused suite
passes **134 tests**:

```bash
.venv/bin/python -m pytest -q \
  scripts/tests/test_changelog.py \
  scripts/tests/test_workflows.py \
  scripts/tests/test_check_dependabot_health.py \
  scripts/tests/test_check_workflow_concurrency.py
python3 scripts/check_workflow_concurrency.py
bash scripts/check-required-docs.sh
CI_VERBOSE=true python3 scripts/check_dependabot_health.py \
  --repository link-foundation/cpp-ai-driven-development-pipeline-template
```

The live read-only check enumerates #26 and #27 and passes because both are
younger than 14 days. Offline tests freeze the clock and verify overdue PRs,
the exact 14-day boundary, fresh rebases of old PRs, a match on the second API
page, custom limits, API errors, malformed responses and annotation escaping.
The workflow-command tests use a fake pipx to verify 1.32.0 and a future version
are selected in both audit passes; a missing pin fails before pipx executes.

The full C++ matrix, packaging and security scans run in CI instead of
duplicating CPU-intensive builds locally. The existing patch-fragment release
flow performs the version bump after merge. The new scheduled workflow becomes
available from the default branch after merge; its script, shell integration
and workflow policies are verified before merge.
