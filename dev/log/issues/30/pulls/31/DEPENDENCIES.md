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
| cmake | not pinned | 4.4.4 |
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
| dotnet/sdk | runner bundled | [v10.0.404](https://github.com/dotnet/sdk/releases/tag/v10.0.404) |
| llvm/llvm-project | runner bundled compiler | [llvmorg-23.1.5](https://github.com/llvm/llvm-project/releases/tag/llvmorg-23.1.5) |

## Scope and decisions to verify

- No runtime library dependencies; C++ development dependencies are GoogleTest and Google Benchmark. CPM is a consumer example dependency. vcpkg brings native build helpers through its baseline.
- Existing case studies, archived workflow copies, and experiment diffs are historical evidence, not active pins. Preserve their accuracy.
- No Dockerfile, npm, Rust, Terraform, Helm or git-submodule manifest exists. The only container dependency is the actionlint workflow image.
- CMake PyPI currently distributes 4.4.4 while upstream has 4.5.0: investigate portable installation before choosing a documented exception.
- Conan audit requires registration/token. Missing credentials must remain an explicit incomplete verdict; do not manufacture a clean scan.
- All existing direct Python pins are already current. Missing transitive locks and older hooks/toolchains still need work.
