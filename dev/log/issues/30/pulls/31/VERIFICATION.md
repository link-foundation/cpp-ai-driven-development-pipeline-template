# Verification evidence

Runs are sequential for native builds, with one compiler process and vcpkg
concurrency one. No stack/memory stress payload was executed. Raw registry and
coordinate reports are preserved alongside selected command logs.

| Check | Result | Evidence |
| --- | --- | --- |
| Full script tests, Python 3.15.2 | 507 passed | `raw/pre-commit-final.log` |
| Full pre-commit hooks, current formatter/hooks | Passed | `raw/pre-commit-final.log` |
| Formatter version regression | Fails on original baseline, passes after fix | `raw/formatter-regression.log`; `experiments/reproduce_issue_30_formatter_drift.py` |
| Dependency policy/workflow tests | 65 passed | `raw/dependency-policy-tests.log` |
| CMake 4.5 Release build and C++ tests | 10 tests passed, benchmarks built | `raw/cmake-release.log` |
| All five consumer mechanisms | Passed, including CPM 0.43.2 | `raw/consumers.log` |
| C++ formatting/static analysis | clang-format 23.1.5, clang-tidy 23.1.4, Cppcheck 2.22.0 passed | `raw/cpp-lint.log` |
| Conan create and installed consumer | Passed, Fibonacci 55 | `raw/conan-create.log` |
| vcpkg features tests + benchmarks | Passed with Benchmark overlay 1.10.0 | `raw/vcpkg-build.log` |
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
