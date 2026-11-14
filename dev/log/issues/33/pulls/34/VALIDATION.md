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
| File-size and active-source whitespace checks (raw evidence excluded) | Passed | file-size.log; git diff --check |
| Latest main ancestry | origin/main is an ancestor of this branch | git merge-base --is-ancestor origin/main HEAD |

The old-loader probe is deliberately a failing regression demonstration, not a
passing check. No tests were skipped to accept a dependency major. CI's native
provider audit may pass a PR with an explicit incomplete warning; this is not a
clean native advisory verdict.

## CI

All five workflows passed at implementation/evidence commit
`46dfbdb158f43239f87ad87d46c27401e5cfcbe2`; each run was created on
2026-11-14 at 18:20:24 UTC, after that push. The full result snapshot is
`research/branch-runs-verified-46dfbdb.json`; all 32 applicable PR checks passed,
with four release/deployment checks skipped by their normal PR conditions.

| Workflow | Passing run |
| --- | --- |
| CI/CD Pipeline | [43626041805](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/runs/43626041805) |
| Security | [43626041895](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/runs/43626041895) |
| Workflows | [43626041771](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/runs/43626041771) |
| Docs | [43626041779](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/runs/43626041779) |
| Broken Link Checker | [43626041746](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/runs/43626041746) |

Linux GCC, Linux Clang, Windows MSVC and macOS AppleClang all passed Debug,
Release with benchmarks, and supported consumer checks. Sanitizers, coverage,
fresh merge, formatting/static analysis, all 509 script tests and secrets scan
passed. Build Packages passed real NuGet restore, Conan create/test_package and
vcpkg install/consumer checks. Pipeline log line 8208 confirms the new vcpkg-tool
2026-10-29, rather than only trusting a manifest change. No deprecation warnings
or errors were found in the build log.

The initial Security run's native status artifact is explicitly `incomplete`;
its complete resolved coordinates are saved in `research/ci-native-46dfbdb/`.
Its differential dependency review was initially skipped because the graph was
disabled; the setting has since been enabled, and the final evidence commit's
Security run must exercise the review. Final-commit CI status is linked in the
PR description; this evidence-only follow-up changes no build inputs. Default-branch Security's
credential failure is preserved in `ci-logs/security-main-43623795378.log` and
explained in [ANALYSIS.md](ANALYSIS.md). Main-green and complete native auditing
remain blocked pending the registered provider secret.
