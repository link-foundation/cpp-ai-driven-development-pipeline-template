# Contributing to cpp-ai-driven-development-pipeline-template

Thank you for contributing. This guide covers the development setup, the
workflow, and how releases are made from changelog fragments.

## Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR-USERNAME/cpp-ai-driven-development-pipeline-template.git
   cd cpp-ai-driven-development-pipeline-template
   ```

2. **Install the toolchain**: CMake 3.25 or newer, a C++20 compiler (GCC,
   Clang, Apple Clang or MSVC), Python 3 and git. Ninja is optional; Doxygen
   is needed only for the documentation target.

3. **Install the pinned CI tools** (clang-format, clang-tidy, cppcheck, gcovr,
   Conan, pytest) and the pre-commit hooks:

   ```bash
   python3 -m pip install -r scripts/requirements-ci.txt
   python3 -m pip install pre-commit
   pre-commit install
   ```

4. **Build and test**

   ```bash
   cmake --workflow --preset dev
   ```

## Development Workflow

1. **Create a branch** from `main`:

   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes** with tests. Public headers go to `include/`, tests to
   `tests/`, and every public symbol needs a Doxygen comment: the Docs
   workflow fails on undocumented symbols.

3. **Run the checks** that CI runs:

   ```bash
   cmake --workflow --preset dev        # Debug build and tests
   cmake --workflow --preset asan       # sanitizers (GCC/Clang)
   cmake --preset lint && python3 scripts/lint_cpp.py
   python3 scripts/check_consumers.py   # every way to consume the library
   python3 -m pytest scripts/tests      # when you change scripts/
   ```

4. **Add a changelog fragment** (see [Changelog Management](#changelog-management)).

5. **Commit and push**. The pre-commit hooks run clang-format, the file size
   check and the script tests.

## Code Style Guidelines

- The code style is defined by `.clang-format` and `.clang-tidy`; do not
  format by hand.
- Compiler warnings are errors in every preset (`/W4` on MSVC, `-Wall -Wextra
  -Wpedantic` and more on GCC and Clang).
- Keep files under 1000 lines of code (markdown: 2500 lines).
  `scripts/check_file_size.py` warns from 900 lines and fails above the limit.
- Scripts in `scripts/` use only the Python standard library or bash, so they
  run on every runner without a setup step.

## Testing Guidelines

- Unit tests use GoogleTest (`tests/`) and run with `ctest`. `constexpr`
  functions should also get `static_assert` checks.
- Benchmarks use Google Benchmark (`benchmarks/`, built by the `release`
  preset).
- A change to the CMake install or package config must keep
  `python3 scripts/check_consumers.py` passing.
- A change to a script in `scripts/` needs a test in `scripts/tests/`.

## Pull Request Process

1. Make sure the checks above pass locally.
2. Add a changelog fragment, unless the pull request only changes
   documentation (markdown, `docs/`) or experiments.
3. Do not change the version in `CMakeLists.txt`, `vcpkg.json` or elsewhere:
   the **Version Modification Check** fails a pull request that does. The
   release pipeline bumps the version.
4. Open the pull request with a clear description of the change.
5. All CI checks must pass; the **Pipeline Status** job summarizes them.
6. Address review feedback.

## Changelog Management

This project uses changelog fragments instead of editing `CHANGELOG.md`
directly, so parallel pull requests never conflict in the changelog.

### Creating a Fragment

```bash
python3 scripts/create_changelog_fragment.py --bump-type minor --description "Add the frobnicate() function"
```

or create `changelog.d/YYYYMMDD_HHMMSS_short_description.md` by hand:

```markdown
---
bump: minor
---

### Added
- The `frobnicate()` function.
```

### Choosing the Bump Type

- `major`: a breaking change of the public API;
- `minor`: a new backwards-compatible feature;
- `patch`: a backwards-compatible bug fix, or anything else (the default).

The highest bump among all pending fragments decides the next version.

### Fragment Categories

Use the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) sections:
`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. See
[changelog.d/README.md](changelog.d/README.md).

### During Release

When a pull request with fragments is merged into `main`, the **Auto Release**
job bumps the version, collects the fragments into `CHANGELOG.md` under the
new version, deletes them, commits, tags and publishes the release.

## Release Process

Releases are automatic; see [docs/ci-cd.md](docs/ci-cd.md#release-flow). A
release can also be started manually from the Actions tab (**CI/CD Pipeline**
→ **Run workflow**):

- `instant` bumps the version and releases immediately;
- `changelog-pr` opens a pull request with a fragment for review first.

## Getting Help

Open an issue for bugs and feature requests, and check the existing issues
and pull requests first.

## Code of Conduct

Be respectful and constructive, and help us keep this project welcoming.
