# Verification evidence

## Local checks

Pinned Python 3.15.2, Node 26.13.1 and npm 12.2.2 were installed in ignored,
isolated directories. Commands ran sequentially where memory intensive. Full
cross-platform compilation is delegated to the existing CI matrix, avoiding a
duplicate local build under the 2.92 GiB container limit.

| Check | Result | Evidence in research/ |
| --- | --- | --- |
| Reproducing new ESM / TypeScript config tests with old loader | 18 passed, 2 failed | rc-loader-before.log |
| npm ci --ignore-scripts; npm test with loader 5 | 20 passed; repository scan passed | npm-install-upgrade.log, npm-test-after.log |
| Python script suite | 509 passed in 111.48 seconds | python-tests.log |
| All pre-commit hooks, including script suite and clang-format | Passed | pre-commit.log |
| Universal Python resolution and three generated requirement manifests | Regenerated; versions already current | python-lock-regeneration.log |
| npm-check-updates --upgrade | Direct dependencies already current | npm-check-updates.log |
| Full scanner npm audit | Zero findings | npm-project-audit.json |
| Strict audit of all Python requirement groups and coverage validation | No findings or coverage gaps | pip-audit.json, pip-audit.log |
| Published npm 12.2.2 bundle audit | 21 moderate entries, two advisory families; externally unresolved | npm-cli-audit.json, npm-cli-probe.log |
| File-size and whitespace checks | Passed | file-size.log; git diff --check |
| Latest main ancestry | origin/main is an ancestor of this branch | git merge-base --is-ancestor origin/main HEAD |

The old-loader probe is deliberately a failing regression demonstration, not a
passing check. No tests were skipped to accept a dependency major. CI's native
provider audit may pass a PR with an explicit incomplete warning; this is not a
clean native advisory verdict.

## CI

Current-commit results will be recorded after push. Default-branch Security's
credential failure is preserved in `ci-logs/security-main-43623795378.log` and
explained in [ANALYSIS.md](ANALYSIS.md). Main-green and complete native auditing
remain blocked pending the registered provider secret.
