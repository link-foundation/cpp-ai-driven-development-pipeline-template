# Registry inventory before changes

Queried 2026-11-14 UTC. `raw/pypi-direct.json` and `raw/github-releases.json` retain registry metadata. Latest means latest stable release in the relevant distribution.

## Python

| Dependency | Before | Latest PyPI |
| --- | --- | --- |
| pip-audit | 2.10.1 | 2.10.1 |
| zizmor | 1.32.0 | 1.32.0 |
| pytest | 9.2.0 | 9.2.0 |
| clang-format | 23.1.5 | 23.1.5 |
| clang-tidy | 23.1.4 | 23.1.4 |
| cppcheck | 1.5.3 | 1.5.3 |
| gcovr | 8.8 | 8.8 |
| conan | 2.34.0 | 2.34.0 |
| pre-commit | not pinned | 4.7.0 |
| pip | not pinned | 26.3 |
| pip-tools | not pinned | 7.6.2 |
| uv | not pinned | 0.13.8 |
| cmake (PyPI distribution, not selected for CI) | not pinned | 4.4.4 |
| ninja | not pinned | 1.13.2 |

## GitHub Actions and native tools

| Dependency | Before | Latest release |
| --- | --- | --- |
| actions/checkout | v7 | [v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1) |
| github/codeql-action | v4.39.3 | [v4.39.3](https://github.com/github/codeql-action/releases/tag/v4.39.3) |
| actions/upload-artifact | v7 | [v7.0.2](https://github.com/actions/upload-artifact/releases/tag/v7.0.2) |
| actions/setup-python | v7 | [v7.1.0](https://github.com/actions/setup-python/releases/tag/v7.1.0) |
| actions/dependency-review-action | v5.0.0 | [v5.0.0](https://github.com/actions/dependency-review-action/releases/tag/v5.0.0) |
| codecov/codecov-action | v7.1.1 | [v7.1.1](https://github.com/codecov/codecov-action/releases/tag/v7.1.1) |
| NuGet/login | v1 | [v1.2.0](https://github.com/NuGet/login/releases/tag/v1.2.0) |
| peter-evans/create-pull-request | v8.1.2 | [v8.1.3](https://github.com/peter-evans/create-pull-request/releases/tag/v8.1.3) |
| lycheeverse/lychee-action | v2.9.0 | [v2.9.0](https://github.com/lycheeverse/lychee-action/releases/tag/v2.9.0) |
| actions/upload-pages-artifact | v5 | [v5.0.0](https://github.com/actions/upload-pages-artifact/releases/tag/v5.0.0) |
| actions/configure-pages | v6 | [v6.0.0](https://github.com/actions/configure-pages/releases/tag/v6.0.0) |
| actions/deploy-pages | v5 | [v5.0.1](https://github.com/actions/deploy-pages/releases/tag/v5.0.1) |
| pre-commit/pre-commit-hooks | v5.0.0 | [v6.0.0](https://github.com/pre-commit/pre-commit-hooks/releases/tag/v6.0.0) |
| pre-commit/mirrors-clang-format | v20.1.8 | [v23.1.5](https://github.com/pre-commit/mirrors-clang-format/tags) |
| google/googletest | v1.18.0 | [v1.18.0](https://github.com/google/googletest/releases/tag/v1.18.0) |
| google/benchmark | v1.9.5 | [v1.10.0](https://github.com/google/benchmark/releases/tag/v1.10.0) |
| cpm-cmake/CPM.cmake | v0.42.0 | [v0.43.2](https://github.com/cpm-cmake/CPM.cmake/releases/tag/v0.43.2) |
| microsoft/vcpkg | 07f4812200df3d3c931c0c8a6081d3b21fe2bf9f | [2026.10.16](https://github.com/microsoft/vcpkg/releases/tag/2026.10.16) |
| microsoft/vcpkg-tool | runner bundled | [2026-10-29](https://github.com/microsoft/vcpkg-tool/releases/tag/2026-10-29) |
| rhysd/actionlint | v1.7.12 | [v1.7.12](https://github.com/rhysd/actionlint/releases/tag/v1.7.12) |
| doxygen/doxygen | Ubuntu bundled | [Release_1_18_0](https://github.com/doxygen/doxygen/releases/tag/Release_1_18_0) |
| python/cpython | 3.13 | [v3.15.2](https://www.python.org/downloads/release/python-3152/) |
| Kitware/CMake | runner bundled; floor 3.21/3.25 | [v4.5.0](https://github.com/Kitware/CMake/releases/tag/v4.5.0) |
| ninja-build/ninja | runner bundled | [v1.13.2](https://github.com/ninja-build/ninja/releases/tag/v1.13.2) |
| .NET SDK (official release index) | runner bundled | [11.0.100](https://dotnet.microsoft.com/en-us/download/dotnet/11.0) |
| llvm/llvm-project | runner bundled compiler | [llvmorg-23.1.5](https://github.com/llvm/llvm-project/releases/tag/llvmorg-23.1.5) |

## Scope and decisions to verify

- No runtime library dependencies; C++ development dependencies are GoogleTest and Google Benchmark. CPM is a consumer example dependency. vcpkg brings native build helpers through its baseline.
- Existing case studies, archived workflow copies, and experiment diffs are historical evidence, not active pins. Preserve their accuracy.
- Initially no Dockerfile, npm, Rust, Terraform, Helm or git-submodule manifest existed; this PR adds npm manifests for the previously unpinned secret scanner. The only container dependency is the actionlint workflow image.
- CMake PyPI currently distributes 4.4.4 while upstream has 4.5.0: investigate portable installation before choosing a documented exception.
- Conan audit requires registration/token. Missing credentials must remain an explicit incomplete verdict; do not manufacture a clean scan.
- All existing direct Python pins are already current. Missing transitive locks and older hooks/toolchains still need work.

## Final resolution and distribution exceptions

Every Python package (including transitives and hook dependencies) is compared in
[PYTHON-LOCK.md](PYTHON-LOCK.md); all 60 resolved versions equal PyPI's latest.
The npm scanner's full resolution is compared in [NPM-LOCK.md](NPM-LOCK.md).
The package-manager CLI is a separate distribution, with its own recorded audit.

| Dependency / distribution | Before | Selected | Latest upstream | Reason if different |
| --- | --- | --- | --- | --- |
| Node.js | runner bundled | 26.13.1 | 26.13.1 | 27 alpha is excluded; official download checksum verified |
| npm CLI | runner bundled | 12.2.2 | 12.2.2 | Two unresolved public advisory families in its upstream bundle; see ANALYSIS.md |
| secretlint / recommended rules | unpinned npx | 13.1.0 | 13.1.0 | Exact direct pins and npm lock |
| actions/setup-node | absent | 7.1.0 | 7.1.0 | Commit 949feb2413d6458794dcd2491c4babbbce0c15c1 |
| zizmorcore/zizmor-action | absent (pipx workaround) | 0.8.1 | 0.8.1 | Commit 45d7276c9ca790aabd705e31ca99c6185c3e76dd; now supports zizmor 1.32.0 |
| jwlawson/actions-setup-cmake | absent | 2.2.0 | 2.2.0 | Commit 0d6a7d60b009d01c9e7523be22153ff8f19460d3 |
| CMake CI binary | runner bundled | 4.5.0 | 4.5.0 | Upstream distribution avoids PyPI lag |
| Conan Center CMake build requirement | implicitly resolved | 4.4.4 | 4.5.0 | Registry has not published 4.5.0; upstream PR 31443; audit retains the real version |
| .NET SDK / NuGet CLI | runner bundled | 11.0.100 | 11.0.100 | Official release index, rather than stale SDK GitHub release |
| vcpkg registry | 07f4812200df3d3c931c0c8a6081d3b21fe2bf9f | 4702e381dbbd9b54d3f7e1eb565cd8981c1814cd | master at query time | Newer than the latest monthly tag; checkout and tool bootstrap use this same baseline |
| vcpkg tool | runner bundled | 2026-10-29 | 2026-10-29 | Baseline's metadata pins release and platform SHA512 hashes |
| vcpkg Benchmark | 1.9.5 | 1.10.0 | 1.10.0 | Overlay until microsoft/vcpkg#55056 is released |
| vcpkg GoogleTest | 1.18.0 | 1.18.0 | 1.18.0 | No change needed |
| vcpkg-cmake | baseline resolved | 2025-08-07 | 2025-08-07 | Latest registry port; date is its version, not an unmaintained compiler |
| vcpkg-cmake-config | baseline resolved | 2026-07-21 | 2026-07-21 | Latest registry port |
| Cppcheck native binary | 2.22.0 via wheel 1.5.3 | 2.22.0 via wheel 1.5.3 | 2.22.0 | Old requirements comment incorrectly said 2.17.1; actual --version confirms 2.22.0 |
| clang-tidy wheel | 23.1.4 | 23.1.4 | LLVM 23.1.5 | Current PyPI wheel lags the upstream native patch release; explicit distribution exception |
| Ubuntu hosted image | 24.04 | 26.04 | 26.04 GA | Current maintained GA image; no preview label |
| macOS hosted image | 15 | 26 | 26 GA | Current Apple toolchain; Xcode 27 preview excluded |
| Windows hosted image | 2025 | 2025 | 2025 GA | Latest stable hosted Windows label, now includes VS 2026 |
| GNU / LLVM compilers on Ubuntu | previous runner bundle | GA image's GCC 15.2 / Clang 22.1.2 | GCC 16.2 / LLVM 23.1.5 | Runner distribution lag; no claim that the image ships latest upstream compilers |
| AppleClang / MSVC | previous runner bundle | current macos-26 / windows-2025 bundle | platform distribution | Vendor toolchain versions are not interchangeable with upstream LLVM numbers |

Hosted image component snapshots are retained in `raw/*-software.txt`. System
shells, curl, git, pkg-config, tar and other OS components follow those current
GA distributions; we do not rebuild or mix operating-system packages manually.
Action runtimes and their JavaScript dependencies follow the immutable upstream
action distributions. Their pins are all the latest stable action releases.

The Conan CMake and clang-tidy distribution lag, compiler distribution lag,
and npm CLI advisories are explicit remaining limits of a literal
"every upstream component current and no advisory" acceptance criterion.
They are not hidden by the clean Python/application audits.
