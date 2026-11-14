# Upstream findings and reports

All reports were searched before posting. Existing reports already containing the
same reproducer are linked rather than duplicated. This table distinguishes
availability requests from confirmed audit findings.

| Component | Evidence / proposal | Report and local handling |
| --- | --- | --- |
| npm CLI 12.2.2 | Published bundle contains affected glob/minimatch; consumer overrides cannot replace bundled copies. Rebuild CLI with patched current majors. | [Existing report with this repository's audit confirmation](https://github.com/npm/cli/issues/10299#issuecomment-6875268007); full CLI audit retained; zero-advisory criterion remains unfinished |
| vcpkg Benchmark port | Latest baseline still resolves 1.9.5. Updating official version/hash to 1.10.0 builds successfully. | [Build evidence and proposed port/database update](https://github.com/microsoft/vcpkg/issues/55056#issuecomment-6875267716); tested local overlay until release |
| clang-tidy wheel | Latest PyPI wheel 23.1.4 lags LLVM 23.1.5; publish wheel with existing platform smoke checks. | [Release availability request #133](https://github.com/ssciwr/clang-tidy-wheel/issues/133); current supported wheel retained, distribution gap explicit |
| Conan Center CMake | Registry's latest 4.4.4 lags upstream 4.5.0. | [Existing update PR #31443](https://github.com/conan-io/conan-center-index/pull/31443); CI uses upstream 4.5.0, Conan graph truthfully records its 4.4.4 build requirement |
| actionlint 1.7.12 | Current parser lacks concurrency queue semantics and Ubuntu 26.04 label. | [Queue report #657](https://github.com/rhysd/actionlint/issues/657), [parser proposal #654](https://github.com/rhysd/actionlint/pull/654), [runner label #682](https://github.com/rhysd/actionlint/issues/682); retain narrow adapter/configuration and tests |
| lychee 0.24.2 | Connect-reset classifier does not retry a confirmed transient transport failure. | [Existing reproducer and retry.rs proposal #2297](https://github.com/lycheeverse/lychee/issues/2297); retain bounded retry and permanent-error tests |
| zizmor-action 0.8.1 | Upstream now publishes hashes for current zizmor wheel. | [Previously reported support gap #175](https://github.com/zizmorcore/zizmor-action/issues/175); use native action and delete local pipx wrappers |
| Cppcheck wheel 1.5.3 | Native executable is already 2.22.0; old local comment was wrong. | [Upstream update #197](https://github.com/ssciwr/cppcheck-wheel/pull/197) is merged; correct local comment, no remaining workaround |

Conan Audit registration is an account prerequisite, not an upstream software bug.
No report asks a maintainer to bypass authentication or invent a clean verdict.

The npm scanner's older transitive major constraints are resolved with explicit,
tested root overrides. Further upstream dependency-range requests are recorded in
`raw/npm-upstream-reports.json` when posted; the major migration sources and
compatibility tests are described in ANALYSIS.md and VERIFICATION.md.
