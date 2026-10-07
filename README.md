# cpp-ai-driven-development-pipeline-template

A template for AI-driven C/C++ development with a complete CI/CD pipeline: build
and test on every major toolchain, lint, sanitize, measure coverage, generate
Doxygen documentation, and release to every common C/C++ distribution channel
from changelog fragments.

[![CI/CD Pipeline](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/workflows/release.yml/badge.svg)](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/workflows/release.yml)
[![Docs](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/workflows/docs.yml/badge.svg)](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/workflows/docs.yml)
[![Security](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/workflows/security.yml/badge.svg)](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/workflows/security.yml)
[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)

It is the C++ member of the link-foundation template family
([Rust](https://github.com/link-foundation/rust-ai-driven-development-pipeline-template),
[Python](https://github.com/link-foundation/python-ai-driven-development-pipeline-template),
[JavaScript](https://github.com/link-foundation/js-ai-driven-development-pipeline-template),
[PHP](https://github.com/link-foundation/php-ai-driven-development-pipeline-template)):
the same job graph, triggers, release model and hardening, following the
[CI/CD best practices](https://github.com/link-assistant/hive-mind/blob/main/docs/CI-CD-BEST-PRACTICES.md),
and it covers what the [linksplatform](https://github.com/linksplatform) C++
libraries need (header-only template libraries, NuGet `TemplateLibrary`
packages, Conan, GitHub Pages documentation).

## Features

- **Single-language and multi-language repositories**: the C++ project lives at
  the repository root (tags `v1.2.3`) or under `cpp/` next to `rust/`, `js/`,
  `python/` ... (tags `cpp_v1.2.3`). Every script detects the layout; see
  [docs/multi-language.md](docs/multi-language.md).
- **Modern CMake**: an `INTERFACE` (header-only) library target with an alias,
  install rules, a relocatable CMake package config, a pkg-config file, and
  CMake presets (`cmake --workflow --preset dev`).
- **Every distribution channel**, each one exercised by CI on every pull
  request ([docs/distribution.md](docs/distribution.md)):
  - the repository itself: `add_subdirectory`, git submodule, `FetchContent`,
    CPM.cmake;
  - `find_package` after `cmake --install`, and pkg-config;
  - GitHub releases: reproducible source archives, the install tree, a vcpkg
    overlay port and `SHA256SUMS`;
  - vcpkg (overlay port or registry), Conan 2 (`conanfile.py` and
    `test_package`), and native NuGet packages for Visual Studio.
- **Cross-platform testing**: GCC and Clang on Ubuntu, Apple Clang on macOS,
  and MSVC on Windows, in Debug and Release, with GoogleTest; benchmarks with
  Google Benchmark.
- **Code quality**: clang-format, clang-tidy and cppcheck at pinned versions,
  warnings as errors, file size limits, and pre-commit hooks.
- **Sanitizers and coverage**: AddressSanitizer and UndefinedBehaviorSanitizer
  over the test suite; gcov and gcovr with a line coverage floor, uploaded to
  Codecov when a token is configured.
- **Documentation**: Doxygen API reference that fails on undocumented public
  symbols, published to GitHub Pages ([docs/ci-cd.md](docs/ci-cd.md#documentation)).
- **Release automation**: changelog fragments decide the semantic version
  bump; the pipeline bumps the version, updates `CHANGELOG.md`, tags, and
  publishes every configured channel, and it heals a release that failed
  half-way.
- **Hardened pipeline**: least-privilege permissions, hash-pinned third-party
  actions, credential preflight probes, CodeQL, dependency review, secret
  scanning, actionlint, zizmor, a broken link checker and a terminal pipeline
  status gate.

## Quick Start

### Using This Template

1. Click "Use this template" on GitHub to create a new repository, and clone it.
2. Rename the placeholder package `my_package` and the repository URLs:

   ```bash
   python3 scripts/rename_project.py your_library --repository your-org/your-repo
   git diff   # review, then commit
   ```

3. Replace the example code in `include/`, `tests/`, `examples/` and
   `benchmarks/` with your own, and describe the library in
   `docs/mainpage.md`.
4. Configure the publishing channels you need (see [Configuration](#configuration)).
5. Add a changelog fragment to every pull request (see [CONTRIBUTING.md](CONTRIBUTING.md)).

For a multi-language repository, move the C++ project into `cpp/` (see
[docs/multi-language.md](docs/multi-language.md)).

### Development Setup

You need CMake 3.25 or newer, a C++20 compiler, Python 3 and git. Ninja is
optional. The tests download GoogleTest with `FetchContent` unless it is
installed.

```bash
# Configure, build and run the tests (Debug)
cmake --workflow --preset dev

# The same in Release, with the benchmarks
cmake --workflow --preset release

# Tests under AddressSanitizer and UndefinedBehaviorSanitizer (GCC/Clang)
cmake --workflow --preset asan

# Build and run the consumer examples (every way to use the library)
python3 scripts/check_consumers.py
```

### Code Quality Checks

The lint tools are pinned in `scripts/requirements-ci.txt`, so everyone runs
the versions CI runs:

```bash
python3 -m pip install -r scripts/requirements-ci.txt

# clang-format, clang-tidy and cppcheck (needs the compile database)
cmake --preset lint
python3 scripts/lint_cpp.py

# Apply clang-format
clang-format -i include/*/*.hpp tests/*.cpp examples/*.cpp benchmarks/*.cpp

# Coverage report (gcovr.cfg sets the filter and the floor)
cmake --workflow --preset coverage
gcovr --object-directory build/coverage

# Tests of the release scripts
python3 -m pytest scripts/tests

# clang-format, the file size check and the script tests on every commit
pre-commit install
```

## Project Structure

```
.
├── CMakeLists.txt              # the library; project(VERSION) is the single version source
├── CMakePresets.json           # dev, release, asan, coverage, lint, install presets
├── cmake/                      # warnings, sanitizers, dependencies, install and package config
├── include/my_package/         # the public headers
├── tests/                      # GoogleTest unit tests
├── benchmarks/                 # Google Benchmark benchmarks
├── examples/                   # basic_usage.cpp and examples/consumers/*
├── conanfile.py, test_package/ # Conan 2 recipe and its test package
├── vcpkg.json                  # vcpkg manifest (dependencies of tests and benchmarks)
├── packaging/                  # templates of the vcpkg port and the NuGet package
├── Doxyfile, docs/             # Doxygen configuration, main page and documentation
├── changelog.d/                # changelog fragments of unreleased changes
├── scripts/                    # CI/CD scripts (Python standard library and bash) and their tests
└── .github/workflows/          # release.yml, docs.yml, security.yml, links.yml, workflows.yml
```

## CI/CD Pipeline

`.github/workflows/release.yml` (**CI/CD Pipeline**) runs on pull requests,
pushes to `main` and manual dispatch. Pull requests get change detection,
changelog and version checks, a secrets scan, fresh-merge simulation, lint,
the test matrix, sanitizers, coverage, the release script tests and a
packaging dry run of every channel. Pushes to `main` additionally release when
changelog fragments are pending. [docs/ci-cd.md](docs/ci-cd.md) describes
every job, the release flow and the other workflows.

## Configuration

Everything is optional: without any configuration the pipeline builds, tests
and creates GitHub releases with all the release assets. Set repository
**variables** (Settings → Secrets and variables → Actions → Variables) and
**secrets** to enable more:

| Name | Kind | Purpose |
| --- | --- | --- |
| `NUGET_PUBLISH` | variable | `true` pushes the NuGet package on release |
| `NUGET_PACKAGE_ID` | variable | NuGet package id, e.g. `Platform.Numbers.TemplateLibrary` |
| `NUGET_USER` | variable | nuget.org profile name for trusted publishing; takes priority over the API key |
| `NUGET_API_KEY` | secret | fallback nuget.org API key with push scope for that id when `NUGET_USER` is unset |
| `CONAN_REMOTE_URL` | variable | Conan remote to upload releases to |
| `CONAN_LOGIN_USERNAME` | variable or secret | Conan remote user |
| `CONAN_PASSWORD` | secret | Conan remote password or token |
| `RELEASE_ARCHIVE_BASENAME` | variable | release archive name, e.g. `platform.numbers_{version}` |
| `CODECOV_TOKEN` | secret | uploads coverage to Codecov |
| `DEPLOY_GITHUB_PAGES` | variable | `true` deploys the Doxygen reference to GitHub Pages |

The **Release Preflight** job checks credentials alongside the build and
blocks releases on refused credentials. NuGet API keys are checked against
an existing package version; first-push scope and deferred OIDC exchanges
are reported as `unknown`. To use trusted publishing, register a nuget.org
policy for this repository and `release.yml`, then set `NUGET_USER` to your
profile name. See [NuGet publishing](docs/distribution.md#nuget).
The branch protection of `main` should require the **Pipeline Status** check.

The CMake options are prefixed with the package name:

| Option | Default | Purpose |
| --- | --- | --- |
| `MY_PACKAGE_BUILD_TESTS` | top-level project | Build the unit tests |
| `MY_PACKAGE_BUILD_EXAMPLES` | top-level project | Build the examples |
| `MY_PACKAGE_BUILD_BENCHMARKS` | `OFF` | Build the benchmarks |
| `MY_PACKAGE_BUILD_DOCS` | top-level project | Add the `my_package_docs` Doxygen target |
| `MY_PACKAGE_INSTALL` | top-level project | Generate the install and package config rules |
| `MY_PACKAGE_FETCH_DEPENDENCIES` | `ON` | Download missing test dependencies |
| `MY_PACKAGE_WARNINGS_AS_ERRORS` | `OFF` | Treat warnings as errors (the presets turn it on) |
| `MY_PACKAGE_SANITIZERS` | empty | Sanitizers for the tests, e.g. `address;undefined` |
| `MY_PACKAGE_ENABLE_COVERAGE` | `OFF` | Instrument the tests for coverage |
| `MY_PACKAGE_NATIVE_ARCH` | `OFF` | Tune tests and benchmarks for the host CPU |

A project consumed through `add_subdirectory`, `FetchContent` or CPM only
gets the library target: tests, examples, docs and install rules default to
on only when the project is the top-level one.

## Contributing

Contributions are welcome. [CONTRIBUTING.md](CONTRIBUTING.md) covers the
development setup, the pull request process and changelog fragments. In short:

1. Create a branch and make your changes, with tests.
2. Run `cmake --workflow --preset dev` and the lint checks.
3. Add a changelog fragment to `changelog.d/`.
4. Open a pull request; the version is bumped by the release pipeline, never
   by hand.

## License

[Unlicense](LICENSE): public domain.
