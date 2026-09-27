# Case study: issue #1, the initial C++ CI/CD template

Issue: [link-foundation/cpp-ai-driven-development-pipeline-template#1](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/issues/1)
("Initial version of CI/CD template for C++"). Data collected on 2026-09-27.

This folder holds the evidence and the analysis behind the template:

| File | Contents |
| --- | --- |
| [README.md](README.md) | This summary: the requirements, a solution and plan for each, where each one is implemented, and what is left |
| [CICD-COMPARISON.md](CICD-COMPARISON.md) | File-by-file and job-by-job comparison of the link-foundation templates and the linksplatform C++ workflows |
| [ONLINE-RESEARCH.md](ONLINE-RESEARCH.md) | Online research: C/C++ distribution channels, Doxygen, sanitizers, lint, CodeQL, runner images, comparable templates, release automation |
| [data/](data/README.md) | The raw evidence: the issue, a survey of all 88 linksplatform repositories, copies of every template workflow and of the linksplatform C++ workflows, file trees, and API and log excerpts |

## How the data was collected

- **The issue**: `gh issue view 1 --json ...` → `data/issue-1.json`.
- **linksplatform**: every repository of the organization was listed through
  the GitHub API (88 repositories). For each one the languages, the top-level
  entries and the workflow files were recorded (`data/linksplatform-repos.json`),
  and every C++ workflow, CMakeLists, Conan file and Doxyfile was copied to
  `data/linksplatform-cpp-workflows/`. The recent runs and the failed deploy
  log of `linksplatform/Interfaces`, the NuGet versions of the
  `*.TemplateLibrary` packages and the linksplatform conan-center-index
  recipes are in `data/raw/`.
- **Templates**: the file trees (`data/template-trees/`) and the workflows
  (`data/template-workflows/`) of the js, rust, python, go, java, csharp and
  php `*-ai-driven-development-pipeline-template` repositories, and the
  hive-mind
  [CI/CD best practices](https://github.com/link-assistant/hive-mind/blob/main/docs/CI-CD-BEST-PRACTICES.md)
  (`data/raw/hive-mind-CI-CD-BEST-PRACTICES.md.txt`).
- **Online research**: the official documentation of CMake, Conan, vcpkg,
  NuGet, Doxygen, the runner images and the actions used, and the READMEs and
  API metadata of comparable templates. Every claim in
  [ONLINE-RESEARCH.md](ONLINE-RESEARCH.md) cites its source.

## Findings in brief

1. **linksplatform ships C++ in 42 repositories** (31 next to C#, 9 next to
   Rust), always in a `cpp/` folder: every one of them is a multi-language
   repository. The C++ workflows follow three patterns, and none of them
   works end to end today (see [linksplatform](#linksplatform) below).
2. **The link-foundation templates share one pipeline**: the same job graph,
   the triggers, the changelog fragments, the release preflight, the
   pipeline-status gate, job-scoped concurrency and zizmor hardening
   ([CICD-COMPARISON.md](CICD-COMPARISON.md), sections 1-13). The C++ template
   has to be a sibling of these, not a new design.
3. **No popular C++ template automates publishing to package registries**
   (cmake_template, ModernCppStarter, modern-cpp-template, cmake-init,
   cpp-project; [ONLINE-RESEARCH.md](ONLINE-RESEARCH.md#13-comparable-c-templates)).
   A tested pipeline for the repository, release archives, CMake packages,
   vcpkg, Conan and NuGet is new.
4. **Each channel can be tested in CI without publishing anything**:
   `find_package` after `cmake --install`, `conan create` with a
   `test_package`, `vcpkg install` of an overlay port, and a NuGet restore
   from a local feed.

## Requirements

The issue asks for eleven things. Each has a solution, the plan that was
followed, and where it lives.

### R1. Support every need of the linksplatform repositories

**What linksplatform needs** (from `data/linksplatform-repos.json` and the
copied workflows, [CICD-COMPARISON.md](CICD-COMPARISON.md) sections 14-15):

- C++ in `cpp/` next to `csharp/` and `rust/`;
- header-only C++20 libraries with GoogleTest tests and Google Benchmark
  benchmarks;
- tags `cpp_<version>`, release titles `[C++] <version>`;
- the NuGet package `Platform.<Repo>.TemplateLibrary`, whose `.targets` file
  adds the include directory;
- a release zip `platform.<repo>_<version>.zip`, which their
  conan-center-index fork downloads by URL;
- the Conan package `platform.<repo>`;
- a Doxygen reference, with `WARN_AS_ERROR` in `linksplatform/Interfaces`;
- CodeQL for C/C++ (`linksplatform/Interfaces`).

**Solution**: every convention is a setting of the template, and the defaults
stay generic:

| Need | Implementation |
| --- | --- |
| `cpp/` layout | Detected automatically, or set with `CPP_ROOT` (`scripts/cpp_project.py`, `detect_layout`) |
| `cpp_<version>` tags | `CPP_TAG_PREFIX: cpp_`; the old `cpp_` and `cpp-v` tags are read as C++ versions, and a bump always lands above the highest one |
| `[C++] <version>` titles | The multi-language default |
| NuGet `TemplateLibrary` | `NUGET_PUBLISH`, `NUGET_PACKAGE_ID`, `NUGET_API_KEY`; `packaging/nuget/` (`.nuspec` + `.targets`), `scripts/pack_nuget.py` |
| `platform.<repo>_<version>.zip` | `RELEASE_ARCHIVE_BASENAME=platform.<repo>_{version}` |
| Conan `platform.<repo>` | The `name` of `conanfile.py`, uploaded as that reference (`read_conan_name`) |
| GoogleTest, Google Benchmark | `tests/`, `benchmarks/`, `cmake/Dependencies.cmake` (`find_package` first, FetchContent otherwise) |
| `-march` tuning | `MY_PACKAGE_NATIVE_ARCH`, off by default |
| Doxygen with warnings as errors | `Doxyfile`, `docs.yml` |
| CodeQL | `security.yml` |

The migration steps are in
[docs/multi-language.md](../../multi-language.md#migrating-a-linksplatform-repository).
[`experiments/multi_language_layout.py`](../../../experiments/multi_language_layout.py)
converts the template to the `cpp/` layout and checks the detection, the
tags, the changelog, the change detection, the release archive, the build,
the consumers and Doxygen.

**Status**: done. One manual step remains for a migrated repository: the
template's archives keep the headers under `include/`, so the
conan-center-index recipe of the next version copies from `include/`
(step 4 of the migration guide).

### R2. A general template like the other link-foundation templates, following the hive-mind best practices

**Solution**: the same five workflows as the Python, C# and PHP templates,
with the same job names, triggers, `workflow_dispatch` inputs
(`release_mode`, `bump_type`, `description`), concurrency groups, hardening
and pipeline-status gate. The shared scripts (`check-pipeline-status.sh`,
`run-with-budget-warning.sh`, `simulate-fresh-merge.sh`,
`check_web_archive.py`, `recheck_broken_links.py` ...) are copied from the
Python template and keep a note saying so. The C++-specific parts replace the
language tools:

| Best practice (hive-mind) | C++ template |
| --- | --- |
| 1. Run checks only on relevant changes | `detect_code_changes.py`, with a C++ file set; no `paths:` filter, so a required check never stays pending |
| 2. File size limits | `check_file_size.py` (1000 lines of code) |
| 3. Formatting | clang-format, pinned in `scripts/requirements-ci.txt` and `.pre-commit-config.yaml` |
| 4. Static analysis | clang-tidy and cppcheck (`lint_cpp.py`), warnings as errors in the presets |
| 5. Fast-fail ordering | detect → lint / test / sanitizers / script tests → build packages → release |
| 6. Changeset versioning | `changelog.d/` fragments with a `bump:` front matter |
| 7. Validate the merge result | Fresh Merge Simulation |
| 8. Pre-commit hooks | `.pre-commit-config.yaml` |
| 9. Release automation | Auto Release, Instant Release, Create Changelog PR |
| 10. Concurrency control | job-scoped groups, a shared `main-write` group for writers |
| 11. Secrets detection | secretlint |
| 12. Documentation validation | `check-required-docs.sh`, Doxygen with `WARN_AS_ERROR` |
| 13. Container images | not applicable: a library template has no image |
| 14. Lint the workflows | actionlint, zizmor, `scripts/tests/test_workflows.py` |
| 15. Audit dependencies | dependency review, Dependabot with a 7-day cooldown |
| 16. Prove you can publish first | `preflight-credentials.sh` (GitHub, NuGet, Conan) |

`scripts/tests/test_workflows.py` also checks the rules that actionlint and
zizmor cannot see: least privilege, timeouts on every job, a pipeline-status
job that needs every other job, credentials dropped on checkout, hash-pinned
third-party actions, no untrusted input in `run:` blocks, and publishing
secrets scoped to steps.

**Status**: done. See [docs/ci-cd.md](../../ci-cd.md).

### R3. Single-language and multi-language modes in one template

**Solution**: one set of files serves both layouts. The scripts detect the
layout: a root `CMakeLists.txt` means single-language mode, `cpp/CMakeLists.txt`
means multi-language mode, and `CPP_ROOT` overrides the detection. The tag
prefix, the release title, the changelog location, the change detection, the
packaging paths and the Pages sub-path all follow the layout, using the same
naming as the other templates (`rust_v1.2.3`, `[Rust] 1.2.3` ...). The
scripts' tests run in both layouts (the `make_repo(multi=True)` fixture), and
the experiment converts the template end to end.

**Status**: done. See [docs/multi-language.md](../../multi-language.md).

### R4. Every way to distribute C/C++

**Solution**: every channel from the research is either automated and tested
in CI, or documented with the release assets it needs:

| Channel | How | Tested in CI by |
| --- | --- | --- |
| The repository (`add_subdirectory`, git submodule) | `PROJECT_IS_TOP_LEVEL` guards | `check_consumers.py` → `examples/consumers/add_subdirectory` |
| FetchContent | `FIND_PACKAGE_ARGS` | `examples/consumers/fetch_content` |
| CPM.cmake | `CPMAddPackage` | `examples/consumers/cpm` |
| CMake package (`find_package`) | `cmake/PackageInstall.cmake`, a versioned, relocatable config | `examples/consumers/find_package` |
| pkg-config | `cmake/package.pc.in` | `examples/consumers/pkg_config` |
| GitHub release | source `.tar.gz` and `.zip`, install tree, vcpkg port, `.nupkg`, `SHA256SUMS` (`package_release.py`) | Build Packages |
| vcpkg | `vcpkg.json` manifest, a port rendered from `packaging/vcpkg/` for an overlay or a registry | `check-vcpkg-port.sh`: a real `vcpkg install` and a consumer build |
| Conan 2 | `conanfile.py` + `test_package/`, optional upload to `CONAN_REMOTE_URL` | `conan create` |
| NuGet (native) | `packaging/nuget/`, pushed with `NUGET_PUBLISH` | `check-nuget-package.sh`: a real restore from a local feed |
| Homebrew, Spack, Meson WrapDB, xmake-repo, build2, Bazel Central Registry, CPack DEB/RPM | documented: they need a submission to another repository, and can reuse the release archive and its SHA256 | - |

The GitHub release is created last, after every registry accepted the
package. A release that failed half-way is completed by the next push to
`main` (`check_release_needed.py`).

**Status**: done for the automated channels. ConanCenter and the curated
vcpkg registry need a manual pull request by design (CLA, review, a maturity
period); [docs/distribution.md](../../distribution.md) describes them.

### R5. Automated documentation with Doxygen

**Solution**: `Doxyfile` with `WARN_IF_UNDOCUMENTED` and
`WARN_AS_ERROR = FAIL_ON_WARNINGS`, the project version read from
`CMakeLists.txt`, HTML and XML output. `docs.yml` builds it on every push
and pull request and keeps the result as an artifact. With
`DEPLOY_GITHUB_PAGES=true` it deploys to GitHub Pages, under `/cpp/` in a
multi-language repository. The `my_package_docs` CMake target builds the same
reference locally.

**Status**: done. A theme such as doxygen-awesome-css is left to the users of
the template (see [Gaps](#gaps-and-future-work)).

### R6. Compare every file of every CI/CD workflow and template

**Solution**: [CICD-COMPARISON.md](CICD-COMPARISON.md) compares the workflow
files, the jobs, the triggers, the concurrency, the permissions, the
pipeline-status gate, the changelog mechanism, the preflight, the fresh
merge, the docs, the link check, the security scans, the workflow lint, the
multi-language naming, the publishing targets, the test matrices and the
lint tools of the seven templates and of linksplatform. It maps each one to
the 16 hive-mind principles (section 18) and lists 23 implications for this
template (section 19). The copies it cites are in `data/`.

**Status**: done.

### R7. Collect the data in `docs/case-studies/issue-1`

**Status**: done. See [data/README.md](data/README.md).

### R8. A deep case study, with online research

**Status**: done: this file, [CICD-COMPARISON.md](CICD-COMPARISON.md) and
[ONLINE-RESEARCH.md](ONLINE-RESEARCH.md).

### R9. List each requirement and propose solutions and plans

**Status**: done: this section.

### R10. Check existing components and libraries

See [Existing components](#existing-components).

**Status**: done.

### R11. Everything in one pull request

**Status**: done: [pull request #2](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/pull/2).

## Existing components

What the template uses, and what it evaluated but did not adopt:

| Component | Used? | Why |
| --- | --- | --- |
| CMake presets (schema 6, workflow presets) | yes | One command per CI job (`cmake --workflow --preset dev`), the same locally |
| GoogleTest, Google Benchmark | yes | What linksplatform uses; found with `find_package` or fetched |
| CPM.cmake | documented | A consumer option; the template itself needs no package manager |
| PackageProject.cmake (ModernCppStarter) | no | The install rules are 64 lines of plain CMake (`cmake/PackageInstall.cmake`) with no extra dependency |
| cmake-init, cmake_template, ModernCppStarter | reference | Their presets, warnings and sanitizer setup informed the template; none publishes packages or automates releases |
| `lukka/run-vcpkg`, `conan-io/setup-conan` | no | The runners ship vcpkg, and Conan is installed from `requirements-ci.txt`, so the versions are pinned in one place and no extra third-party action needs hash-pinning |
| changie, towncrier, scriv | no | The fragment format of the sibling templates (`changelog.d/*.md` with `bump:`) needs only the stdlib scripts |
| release-please | no | Conventional-commit based; parallel AI pull requests conflict less with fragments |
| `cpp-linter/cpp-linter-action` | no | `lint_cpp.py` runs the same tools at pinned versions, locally and in CI |
| doxygen-awesome-css | no | A theme is a choice for each project; it is a submodule or FetchContent away |
| CodeQL (`github/codeql-action@v4`) | yes | `build-mode: none` works in both layouts with no build |
| gcovr, Codecov | yes | Coverage with a 90 % line floor; Codecov only when `CODECOV_TOKEN` is set |
| lychee, actionlint, zizmor, secretlint | yes | Shared with the other templates |

## linksplatform

The problems of the current linksplatform C++ workflows that the template
fixes, with the evidence in [CICD-COMPARISON.md](CICD-COMPARISON.md#151-linksplatform-c-deploy-is-broken-right-now):

| Problem today | In the template |
| --- | --- |
| `sudo apt-get install nuget` fails on `ubuntu-24.04` ("no installation candidate"). The GitHub releases `cpp_0.4.0` and `cpp_0.4.1` of Interfaces exist, but NuGet stops at 0.3.41 | The .NET SDK packs and pushes; the preflight proves the key before the build; the GitHub release is created last, and a missing package is re-published on the next push |
| The tests are compiled but never run (`Workflows-cpp-test.yml`) | `ctest` in every Test, Sanitizers and Coverage job |
| `pull_request: types: [edited]`: pushes to a pull request are never tested | `pull_request` on `opened`, `synchronize` and `reopened` |
| `sed -i '5d'` on the Conan profile | `conan profile detect` and `-s compiler.cppstd=20` |
| 21 repositories run Conan 1 commands with Conan 2 installed | Conan 2 only, pinned in `requirements-ci.txt` |
| An unused `recipe_folder` input with a copy-pasted value | The recipe is `conanfile.py` of the C++ root |
| One OS and one compiler | GCC and Clang on Linux, Apple Clang on macOS, MSVC on Windows, and ASan + UBSan |
| `-march=haswell` whenever the host is x86_64 | `MY_PACKAGE_NATIVE_ARCH`, off by default |
| Scripts downloaded from `linksplatform/Scripts@main` at run time | Every script is in the repository and tested |
| `.clang-format` present but never checked | clang-format, clang-tidy and cppcheck in CI |

## Bugs found while building the template

Each was reproduced by a test that failed before the fix:

- `check_version_modification.py` missed a hand-edited version when a
  commented-out `project(... VERSION ...)` came first; it now uses the
  comment-aware parser of `cpp_project.py`.
- The credential preflight treated only an empty curl status as
  "unreachable", but curl prints `000`, so the unreachable branch never ran.
  `preflight-credentials.sh` matches `'' | 000)`. The Python template has the
  same pattern (`scripts/preflight-credentials.sh`, the `'')` branches);
  there a `000` still ends up as "unknown", but with the message "answered
  000".
- In a multi-language repository the packaging templates were read from the
  repository root instead of `cpp/` (`bfca967`).
- The build, publish, preflight and release-check steps did not all receive
  `NUGET_PACKAGE_ID` and `RELEASE_ARCHIVE_BASENAME`, so the assets checked on
  a pull request could differ from the published ones (`4ebfcb0`, guarded by
  `test_packaging_steps_get_the_release_naming`).
- The Conan upload used the CMake project name instead of the recipe name,
  which differ in linksplatform (`Platform.Numbers` vs `platform.numbers`)
  (`915d1e2`).
- zizmor (`dependabot-cooldown`) asked for a cooldown in
  `.github/dependabot.yml` (`e047379`).
- `check_web_archive.py`, shared with the Python template, reported the
  redirects listed at the end of a lychee report as broken links. Newer lychee
  versions add a "Redirects per input" section, so healthy links such as
  `http://unlicense.org/` got a "Broken link detected" error. It now reads
  only the errors.

## Gaps and future work

Known gaps, none required by the issue:

- **ThreadSanitizer**: only ASan + UBSan run. The template library has no
  threads; a project with threads adds a `tsan` preset like `asan`.
- **CPack**: DEB/RPM packages are documented, not built.
- **CodeQL `build-mode: manual`**: `none` needs no build and works in both
  layouts; `manual` with the `dev` preset is more precise (a comment in
  `security.yml` explains the switch).
- **Runner images**: the jobs use `ubuntu-latest`, `macos-latest` and
  `windows-latest` like the sibling templates, so the compilers move with
  the images; the research lists the versions per image.
- **Registry submissions** (ConanCenter, microsoft/vcpkg, Homebrew and the
  others in R4) stay manual.
- **Repository setting**: the dependency review needs the dependency graph
  (Settings → Advanced Security → Dependency graph). The sibling templates
  have it enabled; this repository does not yet, so the **Security**
  workflow fails its dependency review until it is.
