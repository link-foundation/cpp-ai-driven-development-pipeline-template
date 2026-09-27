# Multi-language repositories

The template supports two layouts, and every script and workflow detects
which one it is in, so the same files work in both:

| | Single-language | Multi-language |
| --- | --- | --- |
| C++ project | repository root | `cpp/`, next to `rust/`, `js/`, `python/` ... |
| Detected by | `./CMakeLists.txt` | `./cpp/CMakeLists.txt` (or `CPP_ROOT`) |
| Release tags | `v1.2.3` | `cpp_v1.2.3` |
| Release titles | `my_package 1.2.3` | `[C++] 1.2.3` |
| Changelog | `CHANGELOG.md`, `changelog.d/` | `cpp/CHANGELOG.md`, `cpp/changelog.d/` |
| API reference on Pages | `https://<owner>.github.io/<repo>/` | `.../<repo>/cpp/`, with a redirect from the root |

The tag prefix and the title follow the other templates (`rust_v1.2.3` and
`[Rust] 1.2.3`, `js_v1.2.3` and `[JavaScript] 1.2.3` ...), so the releases
of every language live side by side in one repository.

## Converting to the multi-language layout

Move everything that belongs to the C++ project into `cpp/`:

```bash
mkdir cpp
git mv CMakeLists.txt CMakePresets.json cmake include tests benchmarks examples \
  conanfile.py test_package vcpkg.json packaging Doxyfile gcovr.cfg \
  .clang-format .clang-tidy CHANGELOG.md changelog.d cpp/
mkdir cpp/docs && git mv docs/mainpage.md cpp/docs/
cp LICENSE cpp/LICENSE && git add cpp/LICENSE
```

What stays at the repository root, shared by every language:

- `.github/` (the workflows), `scripts/` (the release scripts);
- `README.md`, `CONTRIBUTING.md`, `LICENSE`, `docs/` (except `mainpage.md`);
- `.editorconfig`, `.gitignore`, `.lycheeignore`, `.pre-commit-config.yaml`,
  `.secretlintrc.json`.

Notes:

- **`cpp/LICENSE` is required.** The C++ project is packaged on its own: the
  source archive is a `git archive` of `cpp/`, the CMake install rules and the
  vcpkg port install `LICENSE` from the C++ root, and the NuGet and Conan
  packages are built from it.
- **`packaging/`** (the vcpkg port and NuGet templates) is looked up in `cpp/`
  first and in the repository root otherwise.
- **Tags**: new releases are tagged `cpp_v1.2.3`. The older linksplatform tags
  `cpp_1.2.3` and `cpp-v1.2.3` are recognised as C++ versions, so the next
  version always follows the last one. To keep tagging in the old style, set
  `CPP_TAG_PREFIX` (for example `cpp_`) in the `env:` of `release.yml`.
- **Another directory**: to keep the C++ project somewhere other than `cpp/`
  (say `cpp/Platform.Numbers`), set `CPP_ROOT` to that path in the `env:` of
  every workflow. A `CPP_ROOT` always means the multi-language layout.
- **Change detection**: only files under `cpp/`, `scripts/` and `.github/`
  count as C++ code changes, so a pull request that only touches `rust/` does
  not run the C++ build, test and release jobs, and needs no C++ changelog
  fragment.
- **Documentation**: `docs.yml` runs Doxygen in `cpp/` and publishes the
  reference under `/cpp/`. A GitHub Pages site has one source, so when
  another language publishes Pages too, build all sites into one artifact in
  a single workflow.
- **Workflow names**: every template names its pipeline `release.yml`
  (**CI/CD Pipeline**). When several languages share `.github/workflows/`,
  rename each language's files and `name:` (for example `cpp.yml`,
  **C++ CI/CD Pipeline**). The write concurrency group is derived from the
  workflow name, so each language keeps its own. Do not add a `paths:`
  filter: a skipped workflow reports no **Pipeline Status**, which blocks a
  branch protection that requires it; change detection already skips the
  work.

## Consumers

The repository as a distribution still works. CMake consumers point at the
subdirectory:

```cmake
FetchContent_Declare(my_package
  GIT_REPOSITORY https://github.com/<owner>/<repo>.git
  GIT_TAG cpp_v1.2.3
  SOURCE_SUBDIR cpp)
FetchContent_MakeAvailable(my_package)
```

`add_subdirectory(external/<repo>/cpp)` does the same for a git submodule.
The release archives, the vcpkg port, the Conan recipe and the NuGet package
contain only the C++ project, so their consumers see no difference. See
[distribution.md](distribution.md).

## Trying it out

[`experiments/multi_language_layout.py`](../experiments/multi_language_layout.py)
converts a copy of the template in a temporary repository, adds a stand-in
Rust project, and checks the layout detection, the tags and titles, the
documentation check, the bump from `cpp/changelog.d/`, the change detection
of a Rust-only commit, and the contents of the release archive. With
`--build` it also builds and tests the project and every consumer example
inside `cpp/`.

```bash
python3 experiments/multi_language_layout.py --build
```
