# Issue #1 case study: data index

Raw evidence collected on 2026-09-27 for the C++ template case study. The
analysis built on this data is in `../CICD-COMPARISON.md` and
`../ONLINE-RESEARCH.md`.

## Top level

| File | Contents |
|---|---|
| `issue-1.json` | The issue #1 body and metadata, from `gh issue view --json` |
| `linksplatform-repos.json` | A survey of all 88 linksplatform repositories. See the details below the table. |

`linksplatform-repos.json` has two parts:

- A `summary` with overall counts: 27 repos list C++ as a language, 42 have a
  `cpp/` folder, 31 have both `cpp/` and `csharp/`, and 9 have both `cpp/`
  and `rust/`. It also counts which C++ workflow pattern each repo uses
  (`cppWorkflowPatterns`).
- A per-repo record with these fields:
  - languages
  - archived and fork flags
  - top-level entries
  - workflow files
  - C++ workflow files

## `template-trees/`

`<template>.txt` is the `git ls-files` output for each link-foundation
`<template>-ai-driven-development-pipeline-template`, excluding
`docs/case-studies/`. The templates covered are js, rust, python, go, java,
csharp and php.

## `template-workflows/<template>/`

Verbatim copies of every `.github/workflows/*.yml` in each template. The
sources are:

- js: `release.yml`, `example-app.yml`, `links.yml`, `security.yml`, `workflows.yml`
- rust: `release.yml`, `desktop-release.yml`, `links.yml`, `security.yml`, `workflows.yml`
- python, csharp, php: `release.yml`, `docs.yml`, `links.yml`, `security.yml`, `workflows.yml`
- go: `release.yml`, `workflows.yml`
- java: `release.yml`

## `linksplatform-cpp-workflows/`

Verbatim copies of linksplatform files, each prefixed with its source
repository name.

| File(s) | Source |
|---|---|
| `Workflows-cpp-test.yml`, `Workflows-deploy-cpp.yml`, `Workflows-cpp.yml`, `Workflows-get-cpp-package-info.yml`, `Workflows-get-cpp-conan-package-info.yml`, `Workflows-publish-to-conan.yml` | linksplatform/Workflows: the reusable workflows |
| `Interfaces-cpp-test.yml`, `Interfaces-deploy-cpp.yml`, `Interfaces-cpp-docs.yml`, `Interfaces-codeql.yml`, `Interfaces-readme-badges.yml` | linksplatform/Interfaces: the newest workflow set (includes Doxygen and CodeQL) |
| `Interfaces-cpp-CMakeLists.txt`, `Interfaces-cpp-conanfile.txt`, `Interfaces-cpp-Doxyfile`, `Interfaces-cpp-Platform.Interfaces.TemplateLibrary.nuspec`, `Interfaces-.github-scripts-check-cpp-docs.py` | linksplatform/Interfaces: the build, docs and packaging files |
| `Numbers-cpp-test.yml`, `Numbers-deploy-cpp.yml`, `Numbers-rust.yml`, `Numbers-cpp-CMakeLists.txt` | linksplatform/Numbers: a multi-language repo that has benchmarks and whose Rust part uses changelog.d |
| `Data.Doublets-cpp-test.yml`, `Data.Doublets-deploy-cpp.yml`, `Data.Doublets-cpp-CMakeLists.txt`, `Data.Doublets-cpp-conanfile.txt`, `Data.Doublets-cpp-install-local-conan-dependencies.sh` | linksplatform/Data.Doublets: consumes its sibling platform.* packages through Conan |
| `Documentation-cpp.yml`, `Disposables-cpp.yml` | The old-style `cpp.yml` (Conan 1), used by 21 repos; the two copies are identical |
| `Scripts-MultiProjectRepository-*.sh` | linksplatform/Scripts: helpers that the old-style `cpp.yml` downloads at run time |
| `Settings-.clang-format` | linksplatform/Settings: the shared clang-format style (Interfaces symlinks to it) |
| `conan-center-index-platform.interfaces-*` | linksplatform/conan-center-index: the `platform.interfaces` recipe (conanfile.py, conandata.yml, test_package) |
| `linksplatform-Files-TemplateLibrary.targets` | The MSBuild targets file that goes into the native NuGet packages |

## `raw/`

| File | Contents |
|---|---|
| `linksplatform-repo-list.json` | `gh repo list linksplatform` output |
| `cpp-repos.txt`, `cpp-repo-probe.txt` | The C++ repo list, and per-repo probes of their top-level entries and workflows |
| `non-cpp-repos.txt`, `non-cpp-repo-probe.txt` | The same probes for repos without C++ |
| `template-workflow-structure.txt` | An outline of the triggers, concurrency, permissions and jobs of every template workflow |
| `hive-mind-CI-CD-BEST-PRACTICES.md.txt` | A copy of link-assistant/hive-mind `docs/CI-CD-BEST-PRACTICES.md` (the 16 principles) |
| `interfaces-releases.txt`, `linksplatform-release-tags-sample.txt` | Release tag and title conventions: `cpp_<ver>` / `[C++] <ver>`, `csharp_<ver>` / `[C#] <ver>`, and combined tags |
| `interfaces-recent-runs.json` | Recent Interfaces workflow runs |
| `interfaces-deploy-cpp-failed-run-36213155523.txt` | The failed-step log: `E: Package 'nuget' has no installation candidate` |
| `nuget-templatelibrary-packages.txt` | The 16 `Platform.*.TemplateLibrary` NuGet packages, with versions and downloads |
| `linksplatform-conan-recipes.txt` | The 16 `platform.*` recipes in the linksplatform conan-center-index fork |
| `conancenter-upstream-platform-recipes.txt` | The `platform.*` recipes and versions in upstream conan-io/conan-center-index |
| `conan-center-index-platform-prs.json` | conan-center-index PRs for `platform.*` recipes |
| `linksplatform-conan-center-index-platform.interfaces-conanfile.py.txt`, `...-conandata.yml.txt` | Raw fetches of the recipe files |
| `linksplatform-Files-TemplateLibrary.targets.txt` | A raw fetch of the targets file |
| `vcpkg-linksplatform-presence.txt` | A vcpkg ports search: there are no linksplatform ports (`platform-folders` is an unrelated project) |
| `online-*.txt` | Raw notes and fetches from the online research that `../ONLINE-RESEARCH.md` relies on |

The `online-*.txt` files cover these topics:

- CMake
- CodeQL
- Conan
- docs quality
- GitHub releases
- other package managers
- runner images
- template release conventions
- vcpkg
