# Dependency inventory and final selections

Live registry queries: 2026-11-14 UTC. Before is the prepared PR branch
after Dependabot PR 32. Historical case studies and logs retain their
original pins. Latest means current stable in the named distribution.

All 60 Python entries are listed in [PYTHON-LOCK.md](PYTHON-LOCK.md);
all 76 scanner npm entries in [NPM-LOCK.md](NPM-LOCK.md); all 145 distinct
package/version pairs in the published npm CLI in [NPM-CLI.md](NPM-CLI.md).
The scanner and Python tables have no below-latest entries.

## GitHub Actions and hooks

Every immutable action commit still matches the newest stable tag.
The full commit identities and release notes are in `research/github-releases.json`.

| Dependency | Before | Final / latest |
| --- | --- | --- |
| actions/checkout | v7.0.1 | [v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1) |
| lukka/get-cmake | v4.5.0 | [v4.5.0](https://github.com/lukka/get-cmake/releases/tag/v4.5.0) |
| github/codeql-action | v4.39.3 | [v4.39.3](https://github.com/github/codeql-action/releases/tag/v4.39.3) |
| actions/upload-artifact | v7.0.2 | [v7.0.2](https://github.com/actions/upload-artifact/releases/tag/v7.0.2) |
| actions/setup-python | v7.1.0 | [v7.1.0](https://github.com/actions/setup-python/releases/tag/v7.1.0) |
| actions/dependency-review-action | v5.0.0 | [v5.0.0](https://github.com/actions/dependency-review-action/releases/tag/v5.0.0) |
| actions/setup-node | v7.1.0 | [v7.1.0](https://github.com/actions/setup-node/releases/tag/v7.1.0) |
| codecov/codecov-action | v7.1.1 | [v7.1.1](https://github.com/codecov/codecov-action/releases/tag/v7.1.1) |
| NuGet/login | v1.2.0 | [v1.2.0](https://github.com/NuGet/login/releases/tag/v1.2.0) |
| peter-evans/create-pull-request | v8.1.3 | [v8.1.3](https://github.com/peter-evans/create-pull-request/releases/tag/v8.1.3) |
| lycheeverse/lychee-action | v2.9.0 | [v2.9.0](https://github.com/lycheeverse/lychee-action/releases/tag/v2.9.0) |
| actions/upload-pages-artifact | v5.0.0 | [v5.0.0](https://github.com/actions/upload-pages-artifact/releases/tag/v5.0.0) |
| actions/configure-pages | v6.0.0 | [v6.0.0](https://github.com/actions/configure-pages/releases/tag/v6.0.0) |
| actions/deploy-pages | v5.0.1 | [v5.0.1](https://github.com/actions/deploy-pages/releases/tag/v5.0.1) |
| zizmorcore/zizmor-action | v0.8.1 | [v0.8.1](https://github.com/zizmorcore/zizmor-action/releases/tag/v0.8.1) |
| pre-commit/pre-commit-hooks | v6.0.0 | [v6.0.0](https://github.com/pre-commit/pre-commit-hooks/releases/tag/v6.0.0) |
| pre-commit/mirrors-clang-format | v23.1.5 | [v23.1.5](https://github.com/pre-commit/mirrors-clang-format/tags) |

## Native dependencies, runtimes, SDKs, tools and images

| Dependency / distribution | Before | Final | Registry / upstream latest | Reason when different |
| --- | --- | --- | --- | --- |
| GoogleTest | 1.18.0 | 1.18.0 | 1.18.0 | Current in FetchContent, Conan and vcpkg |
| Google Benchmark | 1.10.0 | 1.10.0 | 1.10.0 | Existing overlay remains necessary; registry port is still 1.9.5 |
| CPM.cmake | 0.43.2 | 0.43.2 | 0.43.2 | Bootstrap checksum retained |
| vcpkg registry | 9eec002df1cd109f8f104cd966a763daf9751489 | 4702e381dbbd9b54d3f7e1eb565cd8981c1814cd | master at query time | 471 commits ahead of the newest monthly release 2026.10.16; this advances rather than reverts the merged update |
| vcpkg-tool | 2026-09-26 | 2026-10-29 | 2026-10-29 | Baseline metadata selects the current release and checksums |
| vcpkg-cmake | 2025-08-07 | 2025-08-07 | 2025-08-07 | Current date-versioned registry port |
| vcpkg-cmake-config | 2026-07-21 | 2026-07-21 | 2026-07-21 | Current date-versioned registry port |
| CMake CI binary | 4.5.0 | 4.5.0 | 4.5.0 | Official binary; all get-cmake uses agree |
| Conan Center CMake build requirement | 4.4.4 | 4.4.4 | Conan 4.4.4 / upstream 4.5.0 | Registry publication pending in conan-center-index PR 31443; resolved version remains visible in native audit |
| PyPI CMake (not an active requirement) | not selected | not selected | PyPI 4.4.5 / upstream 4.5.0 | Upstream CI binary avoids this distribution lag |
| Ninja | 1.13.2 | 1.13.2 | 1.13.2 | Python package and get-cmake inputs agree |
| Python | 3.15.2 | 3.15.2 | 3.15.2 | Current stable; development tags excluded |
| Node.js | 26.13.1 | 26.13.1 | 26.13.1 | Official download checksum verified; 27 alpha excluded |
| npm CLI | 12.2.2, engine floor 11.20.0 | 12.2.2, engine floor 12.2.2 | 12.2.2 | Latest published CLI still has 21 moderate audit entries from two advisories; see separate CLI table |
| .NET SDK / NuGet CLI | 11.0.100 | 11.0.100 | 11.0.100 | Official release index, exact SDK; no managed TargetFramework or NuGet PackageReference exists |
| Doxygen | 1.18.0 | 1.18.0 | 1.18.0 | Official source/hash pin |
| actionlint / container | 1.7.12 | 1.7.12 | 1.7.12 | Multi-platform digest b1934ee5f1c509618f2508e6eb47ee0d3520686341fec936f3b79331f9315667 rechecked in registry |
| lychee | 0.24.2 via action 2.9.0 | unchanged | 0.24.2 | Latest action's default binary; bounded connect-phase retry workaround remains pending upstream |
| clang-format | 23.1.5 | 23.1.5 | LLVM / wheel 23.1.5 | Hook, Python and LLVM versions agree |
| clang-tidy | 23.1.4 | 23.1.4 | PyPI 23.1.4 / LLVM 23.1.5 | Wheel publication lag; ssciwr/clang-tidy-wheel issue 133 remains open |
| Cppcheck | wheel 1.5.3 / binary 2.22.0 | unchanged | wheel 1.5.3 / binary 2.22.0 | Distinguish wheel version from executable version |
| Ubuntu runner | ubuntu-26.04 | ubuntu-26.04 | current GA | Current vendor distribution |
| macOS runner | macos-26 | macos-26 | current GA | Xcode 26.6; Xcode 27 preview excluded |
| Windows runner | windows-2025 | windows-2025 | current GA | Current vendor distribution, including VS 2026 |
| Ubuntu GCC | image GCC 15.2 | unchanged | GCC 16.2 | Hosted distribution lag; no pinned supported binary for GCC 16 in this image |
| Ubuntu Clang | image Clang 22.1.2 | unchanged | LLVM 23.1.5 | Hosted distribution lag; no mixing of system compiler packages |
| AppleClang / MSVC | current GA runner bundle | unchanged | current vendor distributions | Apple and Microsoft version numbers are independent of LLVM |

Raw responses: `research/pypi-direct.json`, `github-releases.json`,
`node-releases.json`, `dotnet-index.json`, `vcpkg-head.json`, `vcpkg-ancestry.json`,
`vcpkg-{before,latest}-*`, `conan-cmake-versions.txt`, `actionlint-image.txt` and
`{ubuntu26,macos26,windows2025}-software.txt` in `research/`.
[GCC's official releases](https://gcc.gnu.org/releases.html) confirm 16.2.
System shells, git, curl, tar and OS packages follow these GA distributions.
Action runtime bundles follow the newest immutable published action releases.

## Scope and honest constraints

There are no runtime C++ library dependencies, Cargo/Gem/Maven manifests,
Terraform/Helm manifests, Dockerfiles, submodules, managed projects or NuGet
package manifests. `global.json` selects the SDK used for native NuGet packaging;
adding a NuGet updater without a dependency manifest would do no work.
C++20 and the tested CMake consumer floor 3.25 are compatibility promises,
not stale CI tool pins; CI uses CMake 4.5.0.

All direct Python inputs and generated manifests were regenerated using uv
0.13.8 with the shared universal constraints. They were already current, so
no meaningless lockfile changes are committed. npm-check-updates also found
both direct scanner dependencies current; the transitive loader needed the
major override. The npm engine floor now matches the selected CLI.

Every below-upstream selection above has its distribution reason recorded.
The Conan CMake, clang-tidy and hosted compiler gaps, npm CLI bundle lag, and
incomplete credentialed native audit remain **unfinished** under a literal
all-upstream-components-current / zero-advisories acceptance criterion.
A green PR cannot complete those external criteria.
