# Verification evidence

Runs are sequential for native builds, with one compiler process and vcpkg
concurrency one. No stack/memory stress payload was executed. Raw registry and
coordinate reports are preserved alongside selected command logs.

| Check | Result | Evidence |
| --- | --- | --- |
| Full script tests, Python 3.15.2 | 508 passed after final feature regression | `raw/pre-commit-review.log` |
| Full pre-commit hooks, current formatter/hooks | Passed | `raw/pre-commit-final.log` |
| Formatter version regression | Fails on original baseline, passes after fix | `raw/formatter-regression.log`; `experiments/reproduce_issue_30_formatter_drift.py` |
| Dependency policy/workflow tests | 65 passed; five final pin/feature tests passed | `raw/dependency-policy-tests.log` |
| CMake 4.5 Release build and C++ tests | 10 tests passed, benchmarks built | `raw/cmake-release.log` |
| All five consumer mechanisms | Passed, including CPM 0.43.2 | `raw/consumers.log` |
| C++ formatting/static analysis | clang-format 23.1.5, clang-tidy 23.1.4, Cppcheck 2.22.0 passed | `raw/cpp-lint.log` |
| Conan create and installed consumer | Passed, Fibonacci 55 | `raw/conan-create.log` |
| vcpkg tests + benchmarks | Passed with Benchmark overlay 1.10.0 | `raw/vcpkg-build.log` |
| Doxygen 1.18.0 | Generated HTML/XML, no warnings | `raw/doxygen.log` |
| actionlint regular syntax | Passed with only queue adapter and Ubuntu label extension | `raw/actionlint.log` |
| zizmor regular + high severity/confidence pedantic | Passed | `raw/zizmor.log`, `raw/zizmor-pedantic.log` |
| All Python direct/transitive registry versions | 60 of 60 latest | `PYTHON-LOCK.md`, `raw/pypi-lock.json` |
| All scanner npm registry versions | 76 of 76 latest after tested major overrides | `NPM-LOCK.md`, `raw/npm-lock.json` |
| Scanner detection, formatters, YAML and error semantics | 17 tests plus full repository credential scan pass | `raw/npm-test.log`; `scripts/test_secretlint.mjs` |
| Python strict audit | No known vulnerabilities or coverage gaps | `raw/pip-audit.json` |
| Project npm audit | Zero findings | `raw/npm-audit.json` |
| npm CLI's separate bundled tree audit | **Unfinished: 2 advisory families, 21 propagated moderate findings** | `raw/npm-cli-audit.json`; upstream report in UPSTREAM.md |
| Native coordinate resolution | Both Conan and vcpkg select Benchmark 1.10.0 | `raw/native/resolved.cdx.json`, `raw/native/vcpkg-plan.txt` |
| Complete native vulnerability verdict | **Unfinished: provider account token unavailable** | `raw/native/status.json` |
| Default branch Security | **Unfinished: missing repository secret; main is not merged by this PR** | `ci-logs/main-security-43575793401.log:595` and `:4952` |

Current-head hosted CI is checked after pushing the implementation. The initial
research head 8b34073 passed CI/CD, Docs and Security; its link checker found only
foreign relative links in downloaded Markdown, now preserved as text snapshots.
Final run IDs, timestamps, exact head SHA and any failures are recorded below
after the implementation runs complete. Passing PR checks do not supersede the
explicit unfinished security criteria above.

## Implementation CI (2d96810, 2026-11-14 09:39 UTC)

Workflows (43581561709), Docs (43581561680) and Security (43581561699)
passed. CI/CD (43581561795) completed its Linux, Windows and macOS matrix,
sanitizers, coverage, lint, secret scan and script tests; package build was still
running at this evidence snapshot. Final-head results are recorded in the PR.

Broken Link Checker (43581561688) failed because npm's website returned HTTP 403
for all 76 package documentation URLs, plus an incorrect Cppcheck repository
link (lines 285–460 and aggregate 1192). Evidence links now use npm's public
registry endpoint (HTTP 200 confirmed) and the actual msclock/cppcheck-wheel repo.
No live-link checker rule was relaxed. Full failure log is retained in `ci-logs/`.

The copied vcpkg port also passed `${FEATURES}` instead of `${FEATURE_OPTIONS}`
to CMake. A small CMake boundary test verifies tools OFF/ON, without a download or
compile. The regression fails on the copied upstream port and passes on the fixed
port (`raw/vcpkg-feature-regression.log`). A real default installation previously
set BENCHMARK_INSTALL_TOOLS=ON despite omitting the tools feature; the corrected
install's cache and log are retained in `raw/vcpkg-core-after.log`.

The final local native install succeeded with one compiler process and the cache
now records `BENCHMARK_INSTALL_TOOLS:BOOL=OFF`; the old tools-enabled install also
succeeded. The focused regression exercises both OFF/ON without a native rebuild.
The first final pre-commit invocation reported concurrent working-tree edits made
while its 508 passing tests ran; the subsequent clean-tree hook run is retained in
`raw/pre-commit-clean.log`.

## CMake action warning correction

The final log review found a real newly introduced DEP0169 warning in the CMake
setup dependency despite passing jobs. The current replacement action was queried
from its release registry, its tag dereferenced to a commit, and its platform
checksum catalog inspected. `experiments/verify_issue_30_cmake_action.py` executes
that exact bundle with Node 26, deprecation tracing and a 256 MiB JS heap, validates
CMake 4.5.0 / Ninja 1.13.2 and fails on any DeprecationWarning. The successful raw
log is `raw/get-cmake-smoke.log`. Focused workflow/pin regression checks: 67 passed
(`raw/cmake-action-policy-tests.log`). The full hosted suite is rerun for the
replacement commit; its exact head/conclusions are recorded in the PR.

All five workflows passed at 474a0f0 (run IDs/timestamps/SHA retained in
`raw/pre-action-replacement-runs.json`). Full pipeline log review found only the
same Setup CMake deprecation across its ten invocations; matching log line
numbers are retained in `raw/setup-cmake-pipeline-warnings.log`. This additional
review is why a further action correction was made despite green CI. The
workflow policy regression rejects the previous action and accepts all ten new
steps (`raw/cmake-action-regression.log`). Local hooks repeat only fast checks;
the 67 focused tests and native action smoke cover this correction locally, and
the full script suite is rerun in hosted CI.
