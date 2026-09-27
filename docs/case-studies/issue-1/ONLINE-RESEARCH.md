# Issue #1 - Online research: C/C++ library distribution, docs and CI best practices (as of 2026-09-27)

This document collects external facts needed to design the C++ AI-driven development pipeline
template (`link-foundation/cpp-ai-driven-development-pipeline-template`) so that it supports every
common way of distributing a C/C++ library, publishes Doxygen documentation, and follows current CI
best practices.

Conventions:

- Every section ends with the source URL(s). Short raw excerpts of what was fetched are stored in
  [`data/raw/online-*.txt`](data/raw/).
- Release dates and "latest" versions were taken from the GitHub REST API
  (`gh api repos/<owner>/<repo>/releases`) and PyPI JSON on 2026-09-27, not from rendered pages
  (rendered GitHub pages omit the year for current-year dates).
- Anything that could not be confirmed from a primary source is marked **unverified**.

Raw excerpt files:

| File | Content |
|------|---------|
| [`data/raw/online-github-releases.txt`](data/raw/online-github-releases.txt) | Latest release tags + dates of ~30 tools/actions |
| [`data/raw/online-runner-images.txt`](data/raw/online-runner-images.txt) | GitHub-hosted runner labels and toolchain versions |
| [`data/raw/online-cmake.txt`](data/raw/online-cmake.txt) | CMake docs excerpts (install/export/config helpers/FetchContent/presets/CPack) + PyPI versions |
| [`data/raw/online-conan.txt`](data/raw/online-conan.txt) | Conan 2 header-only recipe, ConanCenter process, Conan 1 freeze |
| [`data/raw/online-vcpkg.txt`](data/raw/online-vcpkg.txt) | vcpkg maintainer guide, registries |
| [`data/raw/online-other-package-managers.txt`](data/raw/online-other-package-managers.txt) | NuGet native, xmake-repo, WrapDB, Homebrew, Spack, BCR, build2 |
| [`data/raw/online-docs-quality.txt`](data/raw/online-docs-quality.txt) | Doxygen, Pages actions, sanitizers, coverage, linters, CodeQL language support |
| [`data/raw/online-codeql.txt`](data/raw/online-codeql.txt) | CodeQL build-mode none GA, action v3 deprecation |
| [`data/raw/online-templates-release.txt`](data/raw/online-templates-release.txt) | Comparable templates, release/changelog tooling |

## Table of contents

1. [CMake install / export / package config](#1-cmake-install--export--package-config)
2. [FetchContent and CPM.cmake](#2-fetchcontent-and-cpmcmake)
3. [Git submodule + add_subdirectory, PROJECT_IS_TOP_LEVEL](#3-git-submodule--add_subdirectory-project_is_top_level)
4. [Conan 2 (ConanCenter and own remote)](#4-conan-2-conancenter-and-own-remote)
5. [vcpkg (curated registry, custom registry, overlay ports)](#5-vcpkg-curated-registry-custom-registry-overlay-ports)
6. [NuGet native packages](#6-nuget-native-packages)
7. [Other channels: pkg-config, xmake, Meson WrapDB, Spack, Homebrew, Debian/CPack, build2, Bazel Central Registry](#7-other-channels)
8. [Doxygen + GitHub Pages + doxygen-awesome-css](#8-doxygen--github-pages--doxygen-awesome-css)
9. [Sanitizers and coverage (gcovr/lcov/llvm-cov + Codecov)](#9-sanitizers-and-coverage)
10. [clang-format, clang-tidy, cppcheck, IWYU, cpp-linter-action](#10-clang-format-clang-tidy-cppcheck-iwyu-cpp-linter-action)
11. [CodeQL for C/C++](#11-codeql-for-cc)
12. [GitHub-hosted runner images and compilers](#12-github-hosted-runner-images-and-compilers)
13. [Comparable C++ templates](#13-comparable-c-templates)
14. [Release automation (versioning, changelog, GitHub releases)](#14-release-automation)
15. [Recommended versions (as of 2026-09)](#recommended-versions-as-of-2026-09)
16. [Implications for the template](#implications-for-the-template)

---

## 1. CMake install / export / package config

**Summary.** The current stable CMake is **4.4.3**. The GitHub tag `v4.4.3` was published on
2026-08-25, and PyPI `cmake` is also 4.4.3. Maintenance releases 4.3.5 and 4.2.8 followed on
2026-09-04. No 4.5 release candidate existed on 2026-09-27.

CMake 4.0 removed compatibility with versions older than 3.5.
`cmake_minimum_required(VERSION <3.5)` is now an error, but the `<min>...<max>` form still works, and
`CMAKE_POLICY_VERSION_MINIMUM` can be used as an escape hatch when consuming old projects.

The canonical way to make a library consumable through `find_package(<Pkg> CONFIG)` is:

- `install(TARGETS ... EXPORT <Pkg>Targets FILE_SET HEADERS ...)`. With `EXPORT`, all PUBLIC or
  INTERFACE file sets must be listed with `FILE_SET`.
- `install(EXPORT <Pkg>Targets NAMESPACE <ns>:: DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/<Pkg>)`.
- `configure_package_config_file(<in> <out> INSTALL_DESTINATION <path> [PATH_VARS ...] [NO_SET_AND_CHECK_MACRO] [NO_CHECK_REQUIRED_COMPONENTS_MACRO] [INSTALL_PREFIX])`
  to generate a relocatable `<Pkg>Config.cmake`.
- `write_basic_package_version_file(<file> [VERSION] COMPATIBILITY <mode> [ARCH_INDEPENDENT])`.
  `ARCH_INDEPENDENT` (since 3.14) is documented as "intended for header-only libraries or similar
  packages with no binaries".

Compatibility modes:

- `AnyNewerVersion`, `SameMajorVersion` and `SameMinorVersion`.
- **New in 4.4:** `SamePatchVersion`, `SameFullVersion` and `SemanticVersion`.
- `ExactVersion` is **deprecated since 4.4**.

Other points:

- A matching `export(EXPORT ... NAMESPACE ...)` call makes the build tree usable directly, without
  installing it.
- CMake 4.3 added `install(PACKAGE_INFO <name> EXPORT <export> ...)`. It generates and installs a
  **Common Package Specification (`.cps`)** file next to or instead of the classic
  `<Pkg>Config.cmake`. The docs page places it under "Added in version 4.3"; I did not check the
  exact version separately. CPS is still new, so the template should keep generating classic config
  files and treat CPS as optional.
- For header-only libraries, use an `INTERFACE` library with `target_compile_features(<t> INTERFACE cxx_std_20)`
  and `FILE_SET HEADERS TYPE HEADERS BASE_DIRS include FILES ...` (file sets exist since 3.23).
- `GNUInstallDirs` supplies the install destinations.
- `CMakePresets.json` schema versions:

  | Schema | CMake | Notes |
  |---|---|---|
  | 1 | 3.19 | |
  | 2 | 3.20 | |
  | 3 | 3.21 | |
  | 4 | 3.23 | |
  | 5 | 3.24 | |
  | 6 | 3.25 | Adds `workflowPresets` and `packagePresets` |
  | 7 | 3.27 | |
  | 8 | 3.28 | |
  | 9 | 3.30 | |
  | 10 | 3.31 | |
  | 11 | 4.3 | |
  | 12 | 4.4 | |

  Schema 6 (CMake >= 3.25) is a good floor for the template: it gets workflow presets and runs on
  every current runner image (Ubuntu 24.04 ships 3.31.6).

Sources:
- https://cmake.org/download/ ; https://github.com/Kitware/CMake/releases ; https://pypi.org/project/cmake/
- https://cmake.org/cmake/help/latest/release/4.0.html
- https://cmake.org/cmake/help/latest/module/CMakePackageConfigHelpers.html
- https://cmake.org/cmake/help/latest/command/install.html
- https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html
- https://cmake.org/cmake/help/latest/guide/importing-exporting/index.html

## 2. FetchContent and CPM.cmake

**FetchContent.** FetchContent is the built-in, zero-dependency way for downstream users to consume
the library straight from Git.

- Since 3.24, `FetchContent_Declare(... FIND_PACKAGE_ARGS ...)` together with
  `FETCHCONTENT_TRY_FIND_PACKAGE_MODE` (`OPT_IN` | `ALWAYS` | `NEVER`) lets one declaration use an
  already-installed package or fall back to downloading it.
- `OVERRIDE_FIND_PACKAGE` redirects later `find_package()` calls to the fetched copy.
- `SYSTEM` (3.25) marks the dependency's include directories as system headers, which silences its
  warnings.
- `EXCLUDE_FROM_ALL` (3.28) keeps the dependency's targets out of the `all` build.
- Since 3.30 (policy CMP0169), the single-argument `FetchContent_Populate(<name>)` is deprecated. Use
  `FetchContent_MakeAvailable()`.

**CPM.cmake.** CPM.cmake is a thin wrapper over FetchContent with a download cache
(`CPM_SOURCE_CACHE`), shorthand syntax (`CPMAddPackage("gh:owner/repo@1.2.3")`) and a
`CPM_USE_LOCAL_PACKAGES` switch. The latest release is **v0.43.2** (2026-09-24).
ModernCppStarter and cpp-best-practices/cmake_template both use it (see section 13).

**Test frameworks the template may fetch:**
- GoogleTest **v1.18.0** (2026-08-10), which requires C++17 or newer.
- Catch2 **v3.16.0** (2026-08-25).

For the library to be FetchContent-friendly:
- Namespaced `ALIAS` targets (`add_library(ns::lib ALIAS lib)`), so the name is the same whether it
  comes from `find_package` or from `add_subdirectory`.
- Tests, examples, docs and install rules off by default when the project is not top-level (section 3).
- No global `CMAKE_CXX_FLAGS` changes and no `-Werror` leaking to consumers.

Sources:
- https://cmake.org/cmake/help/latest/module/FetchContent.html
- https://cmake.org/cmake/help/latest/policy/CMP0169.html
- https://github.com/cpm-cmake/CPM.cmake/releases
- https://github.com/google/googletest/releases ; https://github.com/catchorg/Catch2/releases

## 3. Git submodule + add_subdirectory, PROJECT_IS_TOP_LEVEL

**Summary.** `PROJECT_IS_TOP_LEVEL`, added in CMake 3.21, is true when the most recent `project()`
call is in the top-level `CMakeLists.txt`. `<PROJECT-NAME>_IS_TOP_LEVEL` is the per-project variant.

This is the standard switch for options such as:

```cmake
option(MYLIB_BUILD_TESTS    "Build tests"    ${PROJECT_IS_TOP_LEVEL})
option(MYLIB_BUILD_EXAMPLES "Build examples" ${PROJECT_IS_TOP_LEVEL})
option(MYLIB_INSTALL        "Generate install rules" ${PROJECT_IS_TOP_LEVEL})
```

With these options, the same source tree works in three ways:
- As a git submodule with `add_subdirectory(extern/mylib)`.
- Via FetchContent.
- As a stand-alone project, where tests, examples and docs are on.

Older templates used `CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR`, which the variable now
replaces. Submodule consumers should pin a release tag. The template should document
`git submodule add -b <tag>` and `git submodule update --init --recursive`. For
`actions/checkout`, the `submodules: recursive` input is needed.

Sources:
- https://cmake.org/cmake/help/latest/variable/PROJECT_IS_TOP_LEVEL.html
- https://cmake.org/cmake/help/latest/command/add_subdirectory.html
- https://github.com/actions/checkout (inputs `submodules`, `fetch-depth`)

## 4. Conan 2 (ConanCenter and own remote)

**Summary.** The current Conan is **2.32.0**, released 2026-08-31 on both GitHub and PyPI. Its notes
add LoongArch64 support and settings for Xcode 26.6 and GCC 16.2. Conan 1 is frozen: the last 1.x
release is 1.66.0 (2024-12-02). ConanCenter has only accepted Conan 2 recipe updates since
**2024-11-04**; existing Conan 1 packages remain downloadable.

For a **header-only** library, the Conan 2 recipe uses:
- `package_type = "header-library"` and `no_copy_source = True`.
- In `package_info()`: `self.cpp_info.bindirs = []` and `self.cpp_info.libdirs = []`.
- In `package_id()`: `self.info.clear()`, so a single package ID serves all settings.

Other recipe and publishing details:
- Tests use `test_requires` (for example `gtest/1.x`). `conan create .` builds the package and runs
  `test_package/`.
- **Own remote:**
  - `conan remote add <name> <url>` and `conan remote login <name> <user> -p <token>`.
  - `conan upload "<ref>" -r=<name> --confirm`.
  - Server options are `conan_server` or JFrog Artifactory (the free Community Edition for C/C++).
- **ConanCenter:**
  - Sign the CLA.
  - Copy `docs/package_templates/<type>` into `recipes/<name>/`, which contains `config.yml`,
    `all/conanfile.py`, `all/conandata.yml` (URL and sha256 per version) and `all/test_package/`.
  - Recipes must "match upstream".
  - The ConanCenter CI builds 30+ configurations before merge.
- The official GitHub Action is `conan-io/setup-conan` **v1.4.0** (2026-06-04). Its inputs are
  `version`, `home`, `config_urls`, `audit_token` and `cache_packages`; `python_version` is deprecated.
- In the consuming project, `conan install . --build=missing -of build` generates
  `conan_toolchain.cmake` and `CMakeDeps` files, used via `-DCMAKE_TOOLCHAIN_FILE`. Conan 2 also
  offers a `cmake-conan` dependency provider (`CMAKE_PROJECT_TOP_LEVEL_INCLUDES`). This is general
  Conan 2 knowledge; I did not re-fetch it for this study.

Sources:
- https://github.com/conan-io/conan/releases ; https://pypi.org/project/conan/
- https://blog.conan.io/2024/09/30/Conan-Center-will-stop-receiving-updates-for-Conan-1.html
- https://github.com/conan-io/conan-center-index/discussions/25461
- https://docs.conan.io/2/tutorial/creating_packages/other_types_of_packages/header_only_packages.html
- https://docs.conan.io/2/tutorial/conan_repositories/uploading_packages.html
- https://github.com/conan-io/conan-center-index/blob/master/docs/adding_packages/README.md
- https://github.com/conan-io/setup-conan

## 5. vcpkg (curated registry, custom registry, overlay ports)

**Summary.** The latest `microsoft/vcpkg` release tag is **2026.07.29** (published 2026-07-31). The
latest stable `vcpkg-tool` is **2026-07-27**, and a prerelease was published 2026-09-26. Projects
consume vcpkg through a `vcpkg.json` manifest:
- `$schema` is `https://raw.githubusercontent.com/microsoft/vcpkg-tool/main/docs/vcpkg.schema.json`.
- `name` and one of `version`, `version-semver`, `version-date` or `version-string`, plus `port-version`.
- `dependencies` entries can use `host`, `features`, `platform` and `"version>="`.
- `overrides`.
- `builtin-baseline`, a commit SHA of microsoft/vcpkg. It is required for versioning when no
  default registry is configured.
- An optional embedded `configuration` object, for example for overlay ports.

**Upstreaming to the curated registry** (maintainer guide, updated 2026-02-18):
- **Maturity:** the project needs a release at least 6 months old, or 6 months of active public
  development.
- **Pull requests:** one port per PR. Draft PRs are welcome, and PRs inactive for more than 60 days
  may be closed.
- **Port naming:** names must be distinctive. Ambiguous names get a `<github-owner>-<repo>` prefix,
  and CMake exports that upstream does not provide use an `unofficial-` prefix.
- **Portfile helpers:**
  - Use `vcpkg_from_github(OUT_SOURCE_PATH ... REPO ... REF ... SHA512 ... HEAD_REF ...)`. To get the
    hash, set `SHA512 0`, run the build, and copy the value from the error message.
  - Use `vcpkg_cmake_configure`, `vcpkg_cmake_install` and `vcpkg_cmake_config_fixup`, with host
    dependencies `vcpkg-cmake` and `vcpkg-cmake-config`. `vcpkg_fixup_cmake_targets` is deprecated.
  - Install the license with `vcpkg_install_copyright(FILE_LIST "${SOURCE_PATH}/LICENSE")`.
  - Hex strings must be lowercase.
- **Build rules:** no vendored dependencies, and tests and examples are off by default.
- **Versioning:** bump `port-version` for port-only changes. Run `vcpkg x-add-version <port>` and
  `vcpkg format-manifest --all`.

**Custom (git) registry.** This is the recommended option alongside, or instead of, upstreaming.
Registries come in three kinds: builtin, git and filesystem, and git is recommended.
- Layout:
  - `ports/<name>/{portfile.cmake,vcpkg.json}`.
  - `versions/baseline.json`.
  - `versions/<first-letter>-/<name>.json`, which maps each version to a `git-tree` SHA.
- Update it with
  `vcpkg x-add-version --x-builtin-ports-root=./ports --x-builtin-registry-versions-dir=./versions <name>`.
- Consumers reference it from `vcpkg-configuration.json` via `registries: [{kind: "git", repository, baseline, packages}]`.
- Never rewrite version history.
- **Overlay ports** (`--overlay-ports` or `configuration.overlay-ports`) are the fastest way to test
  a port in CI before submitting it.

CI integration:
- `lukka/run-vcpkg` **v11.6** (2026-04-23). Pin `vcpkgGitCommitId` or use a submodule. It provides
  binary caching through the GitHub Actions cache.
- Pair it with `lukka/run-cmake` and `lukka/get-cmake` **v4.4.2** (2026-08-01), driven by CMakePresets.
- The Ubuntu 24.04 and Windows 2025 runner images already contain vcpkg (`VCPKG_INSTALLATION_ROOT`).

Sources:
- https://github.com/microsoft/vcpkg/releases ; https://github.com/microsoft/vcpkg-tool/releases
- https://learn.microsoft.com/en-us/vcpkg/contributing/maintainer-guide
- https://learn.microsoft.com/en-us/vcpkg/concepts/registries
- https://learn.microsoft.com/en-us/vcpkg/reference/vcpkg-json
- https://learn.microsoft.com/en-us/vcpkg/maintainers/functions/vcpkg_from_github
- https://github.com/lukka/run-vcpkg ; https://github.com/lukka/get-cmake

## 6. NuGet native packages

**Summary.** Microsoft's guide says a package for C++ (MSBuild/Visual Studio) projects "must target
the `native` framework".

Package layout:
- Native packages "provide files in `\build`, `\content`, and `\tools` folders; `\lib` is not used
  in this case".
- Files named `build/native/<PackageId>.targets` and/or `.props` are imported automatically.
- Add `native` to the `<tags>` in the `.nuspec`.

Common practice:
- Headers go in a folder such as `lib/native/include` or `build/native/include`.
- The `.targets` file adds `$(MSBuildThisFileDirectory)..\..\lib\native\include` to
  `AdditionalIncludeDirectories`. This practice comes from secondary sources and existing LinksPlatform
  `TemplateLibrary.targets` (see `data/raw/linksplatform-Files-TemplateLibrary.targets.txt`).
- The package is built with `nuget pack <file>.nuspec`. Pushing to nuget.org needs an API key
  (`dotnet nuget push *.nupkg --api-key ... --source https://api.nuget.org/v3/index.json`). The same
  mechanism works for GitHub Packages.

The older CoApp PowerShell tooling ("autopkg") appears to be unmaintained. **Unverified:** only
secondary blog posts say this, not an official statement. A hand-written `.nuspec` plus `.targets`
is the low-risk choice. For header-only libraries, NuGet is mainly useful for existing
MSBuild/Visual Studio consumers; vcpkg is Microsoft's recommended C++ package manager today.

Sources:
- https://learn.microsoft.com/en-us/nuget/guides/native-packages
- https://learn.microsoft.com/en-us/nuget/reference/nuspec
- https://digitalhouseblog.wordpress.com/2019/08/22/how-to-make-a-nuget-package-for-c/ (secondary)

## 7. Other channels

### 7.1 pkg-config (.pc file)

**Summary.** Generate `<name>.pc` from a `<name>.pc.in` with `configure_file(... @ONLY)`, using
`GNUInstallDirs` paths. Install it to `${CMAKE_INSTALL_LIBDIR}/pkgconfig`, or to
`${CMAKE_INSTALL_DATADIR}/pkgconfig` for architecture-independent header-only packages. A header-only
`.pc` only needs `prefix`, `includedir`, `Name`, `Description`, `Version` and `Cflags: -I${includedir}`.
Build systems such as Meson, autotools and plain Makefiles use it. **Unverified:** I did not fetch
these URLs for this study; the content is standard pkg-config practice.

Sources:
- https://people.freedesktop.org/~dbn/pkg-config-guide.html
- https://cmake.org/cmake/help/latest/command/configure_file.html

### 7.2 xmake (xmake-repo)

**Summary.** Add a package to the official repository by writing `packages/<first-letter>/<name>/xmake.lua`
and opening a PR against the **`dev`** branch of `xmake-io/xmake-repo`. The recipe uses:
- `set_homepage`, `set_description`, `add_urls`, `add_versions("<ver>", "<sha256>")`.
- `on_install` (a header-only recipe just copies headers, for example `os.cp("include", package:installdir())`).
- `on_test` with `check_cxxsnippets`.

Stars: xmake-repo about 940, xmake about 12.2k.

Source: https://github.com/xmake-io/xmake-repo

### 7.3 Meson WrapDB

**Summary.** Submit a PR to `mesonbuild/wrapdb` that adds:
- `subprojects/<name>.wrap`.
- An overlay `subprojects/packagefiles/<name>/meson.build` if upstream has no Meson build.
- An entry in `releases.json`. Versions have the form `<upstream>-<revision>`, and the revision
  starts at 1.

`tools/sanity_checks.py` runs locally and in CI. A person other than the submitter must review the PR.

Sources:
- https://github.com/mesonbuild/wrapdb
- https://mesonbuild.com/Adding-new-projects-to-wrapdb.html

### 7.4 Spack

**Summary.** Since Spack v1.0, the builtin recipes live in a separate repository, `spack/spack-packages`,
at `repos/spack_repo/builtin/packages/<name>/package.py`. CMake projects subclass `CMakePackage` and
declare `version("x.y.z", sha256=...)` and `depends_on("cmake@3.25:", type="build")`. This mostly
matters for HPC users. Stars: spack about 5.1k.

Sources:
- https://github.com/spack/spack-packages
- https://spack.readthedocs.io/en/latest/build_systems/cmakepackage.html

### 7.5 Homebrew

**Summary.** homebrew-core has notability thresholds:
- For a third-party submission, the project needs "at least 30 forks, 30 watchers or 75 stars".
- For a **self-submission by the repository owner**, it needs "at least 90 forks, 90 watchers or 225 stars".

Below these thresholds, the way to ship is a **tap**: a repository named `<org>/homebrew-<tap>` with
`Formula/<name>.rb`. Users run `brew install <org>/<tap>/<name>`.

Source: https://docs.brew.sh/Package-Acceptance-Policy

### 7.6 Debian packages via CPack

**Summary.** The CPack DEB generator produces `.deb` files with no Debian packaging expertise needed.
Key variables:
- `CPACK_DEBIAN_PACKAGE_MAINTAINER`, which defaults to `CPACK_PACKAGE_CONTACT`.
- `CPACK_DEBIAN_FILE_NAME DEB-DEFAULT`, which produces `<name>_<ver>-<rev>_<arch>.deb`.
- `CPACK_DEBIAN_PACKAGE_SHLIBDEPS`, which runs `dpkg-shlibdeps`; it is irrelevant for header-only packages.
- `CPACK_DEB_COMPONENT_INSTALL`.

With presets schema 6, `packagePresets` and `workflowPresets` can run `cpack -G DEB;TGZ;ZIP` in one
command. CPack `.deb` files are suitable as GitHub Release assets, but they are not policy-compliant
Debian archive packages. Getting into Debian or Ubuntu needs a maintainer or sponsor, or a PPA.

Source: https://cmake.org/cmake/help/latest/cpack_gen/deb.html

### 7.7 build2 (cppget.org)

**Summary.** `bdep publish` submits the package to **cppget.org** by default. The repository section
(alpha, beta or stable) is derived from the version. The usual flow is
`bdep ci` → `bdep release --tag --push` → `bdep publish`. The project needs a build2 `manifest` and
`buildfile`s, so a CMake-only project has to maintain a second build description. Stars: build2
about 680.

Source: https://build2.org/bdep/doc/bdep-publish.xhtml

### 7.8 Bazel Central Registry (BCR)

**Summary.** A BCR entry lives at `modules/<name>/<version>/` and contains:
- `MODULE.bazel`.
- `source.json`, which only supports the archive type.
- `presubmit.yml`.
- Optional overlay or patches that add `BUILD.bazel` when upstream has none.

Create the entry with `bazel run //tools:add_module`, or automate it with the
`bazel-contrib/publish-to-bcr` reusable workflow, which opens a BCR PR on each release. Stars: BCR
about 390.

Sources:
- https://github.com/bazelbuild/bazel-central-registry/blob/main/docs/README.md
- https://github.com/bazel-contrib/publish-to-bcr

## 8. Doxygen + GitHub Pages + doxygen-awesome-css

**Summary.** The latest Doxygen is **1.18.0** (2026-08-13). Earlier releases are 1.17.0 (2026-04-30)
and 1.16.1 (2026-01-11). None of the GitHub runner images ships Doxygen, so CI must install it,
either with `apt-get install doxygen graphviz` (distro version) or from the official release binary
for an exact version. Useful Doxyfile settings:
- `WARN_AS_ERROR` accepts `NO`, `YES`, `FAIL_ON_WARNINGS` or `FAIL_ON_WARNINGS_PRINT`.
  `FAIL_ON_WARNINGS` processes everything and then exits non-zero, which suits CI.
- `WARN_IF_UNDOCUMENTED`.
- `USE_MDFILE_AS_MAINPAGE = README.md`.

The theme **doxygen-awesome-css** is at **v2.5.0** (2026-09-12). The release adds support for
Doxygen 1.17 and later, and the project says it "works best with Doxygen 1.9.1 - 1.9.4 and
1.9.6 - 1.18.0".
- Required settings: `GENERATE_TREEVIEW = YES`, `DISABLE_INDEX = NO`, `FULL_SIDEBAR = NO`,
  `HTML_COLORSTYLE = LIGHT`, and `HTML_EXTRA_STYLESHEET = doxygen-awesome.css` (plus optional
  sidebar-only and dark-mode-toggle extensions via `HTML_EXTRA_FILES` and `HTML_HEADER`).
- Install it as a git submodule, via FetchContent, or with
  `npm install https://github.com/jothepro/doxygen-awesome-css#v2.5.0`.

**Publishing** uses the official Pages actions:
- `actions/configure-pages` **v6.0.0** (2026-03-25).
- `actions/upload-pages-artifact` **v5.0.0** (2026-04-10). It moved to upload-artifact v7 and added
  `include-hidden-files`.
- `actions/deploy-pages` **v5.0.1** (2026-09-01, Node 24). Its README still shows `@v4`.

The deploy job needs `permissions: pages: write, id-token: write` and
`environment: { name: github-pages, url: ${{ steps.deployment.outputs.page_url }} }`. The
repository's Pages source must be set to "GitHub Actions". CMake can wrap Doxygen with
`find_package(Doxygen)` and `doxygen_add_docs()`, so `cmake --build --target docs` works locally.

Sources:
- https://github.com/doxygen/doxygen/releases ; https://www.doxygen.nl/manual/config.html
- https://jothepro.github.io/doxygen-awesome-css/ ; https://github.com/jothepro/doxygen-awesome-css/releases
- https://github.com/actions/deploy-pages ; https://github.com/actions/upload-pages-artifact ; https://github.com/actions/configure-pages
- https://cmake.org/cmake/help/latest/module/FindDoxygen.html

## 9. Sanitizers and coverage

**Sanitizers.**

- **ASan:** `-fsanitize=address -fno-omit-frame-pointer -O1 -g`, with about a 2x slowdown.
  LeakSanitizer is on by default on Linux. Runtime options are set separately through `ASAN_OPTIONS`,
  `LSAN_OPTIONS` and `UBSAN_OPTIONS`. A useful CI setting is
  `UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1` together with `-fno-sanitize-recover=all`.
- **UBSan** combines with ASan.
- **TSan** must run in its own job because it cannot be combined with ASan.
- **MSan:**
  - Clang only, on Linux, NetBSD or FreeBSD.
  - It "requires that all program code is instrumented ... even libc", so in practice it needs an
    instrumented libc++. It is optional and not worth it for a template.
  - Use `-fsanitize-memory-track-origins=2`.
- **MSVC** supports `/fsanitize=address`, `/fsanitize=kernel-address` and `/fsanitize=fuzzer` only.
  UBSan and TSan are listed as future work, and the comma-separated syntax is not accepted. On
  Windows, the template can therefore only offer ASan.
- **Runner gotcha:** newer Ubuntu kernels set `vm.mmap_rnd_bits=32`, which breaks older ASan, TSan
  and MSan runtimes with "unexpected memory mapping" errors. The fix is LLVM 18.1 or newer (or a
  matching GCC runtime), or a workaround step `sudo sysctl vm.mmap_rnd_bits=28`, or running under
  `setarch -R`.

**Coverage.**

- **gcovr 8.6** (2026-01-13):
  - Compile with `--coverage -O0 -fprofile-abs-path`. For Clang, use
    `gcovr --gcov-executable "llvm-cov gcov"`.
  - It writes Cobertura, Coveralls, HTML, LCOV, JSON, SonarQube, JaCoCo and Markdown.
    `--cobertura coverage.xml` or `--lcov` is what Codecov needs, and `--fail-under-line` enforces
    thresholds.
- **lcov v2.5** (2026-07-06) is the alternative. It is stricter about inconsistencies in 2.x; with
  GCC 14/15 you often need `--ignore-errors mismatch`, which is general knowledge and **unverified**
  here.
- **Clang source-based coverage** (`-fprofile-instr-generate -fcoverage-mapping` +
  `llvm-profdata merge` + `llvm-cov export -format=lcov`) is more precise for header-only code.

**Codecov upload.** Use `codecov/codecov-action` **v7.1.1** (2026-09-17).
- v6.0.0 (2026-03-26) moved to Node 24.
- v7.0.0 (2026-06-07) changed the GPG signing-key account to `codecovsecops`.
- The README still shows `@v5`.
- It supports `use_oidc: true` (with `id-token: write`) instead of a `CODECOV_TOKEN` secret.
  Tokenless uploads are only allowed for PRs from forks to public repositories.

Sources:
- https://clang.llvm.org/docs/AddressSanitizer.html ; https://clang.llvm.org/docs/MemorySanitizer.html
- https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html ; https://clang.llvm.org/docs/ThreadSanitizer.html
- https://learn.microsoft.com/en-us/cpp/build/reference/fsanitize?view=msvc-170
- https://github.com/actions/runner-images/issues/9515 ; https://github.com/google/sanitizers/issues/1716
- https://gcovr.com/en/stable/ ; https://gcovr.com/en/stable/guide/compiling.html ; https://github.com/linux-test-project/lcov/releases
- https://github.com/codecov/codecov-action

## 10. clang-format, clang-tidy, cppcheck, IWYU, cpp-linter-action

**Versions.**
- Latest LLVM is **23.1.2** (2026-09-22); the clang-tidy docs are already at 24.0.0git.
- The PyPI wheels, useful for pinning an exact formatter version in CI and pre-commit, are
  `clang-format` **23.1.1** and `clang-tidy` **22.1.8**.
- Runner images carry only older versions (Ubuntu 24.04: 16-18; Ubuntu 26.04: 20-22). Pin the
  clang-format major version (via pip wheel, `apt.llvm.org` or `aminya/setup-cpp` v1.10.1), because
  formatting output changes between majors.

**clang-tidy** needs `compile_commands.json` (`CMAKE_EXPORT_COMPILE_COMMANDS=ON`, which presets can
set). There are two ways to run it:
- `run-clang-tidy.py -p build` checks everything in parallel.
- `clang-tidy-diff.py` checks only the changed lines in a PR.

The `.clang-tidy` file should set `WarningsAsErrors` and `HeaderFilterRegex`, so that headers of a
header-only library are actually checked. CMake's `CMAKE_CXX_CLANG_TIDY` can also run it during the
build.

**Other analyzers.**
- **cppcheck 2.22.0** (2026-09-19). It is not preinstalled on runner images. It can use
  `--project=compile_commands.json` and `--enable=warning,style,performance,portability --error-exitcode=1`,
  or run via `CMAKE_CXX_CPPCHECK`.
- **include-what-you-use 0.26** (2026-03-22). Each release is tied to a specific Clang major version,
  and it runs via `CMAKE_CXX_INCLUDE_WHAT_YOU_USE`. It is better as an optional or advisory job.

**cpp-linter/cpp-linter-action v2.23.1** (2026-09-23) runs clang-format and clang-tidy and reports
through PR thread comments, step summaries and file annotations.
- Key inputs: `style: 'file'`, `tidy-checks: ''` (use `.clang-tidy`), `version: <llvm-major>`,
  `database: build`, `files-changed-only`, `thread-comments`, `step-summary`.
- Output: `checks-failed`, which is used to fail the job.
- About 146 stars.

Sources:
- https://github.com/llvm/llvm-project/releases ; https://pypi.org/project/clang-format/ ; https://pypi.org/project/clang-tidy/
- https://clang.llvm.org/extra/clang-tidy/ ; https://clang.llvm.org/docs/ClangFormatStyleOptions.html
- https://github.com/danmar/cppcheck/releases ; https://github.com/include-what-you-use/include-what-you-use/releases
- https://github.com/cpp-linter/cpp-linter-action ; https://github.com/aminya/setup-cpp

## 11. CodeQL for C/C++

**Build modes.** CodeQL analyzes C/C++ under the language id **`c-cpp`**, with build modes `none`,
`autobuild` or `manual`.
- **`build-mode: none`** (no build needed) for C/C++ became **generally available on 2025-10-14**
  with CodeQL 2.23.3. It had been in public preview since 2025-06-03.
- GitHub reported "over 10,000 repositories were enabled with a success rate of over 70%".
- Default setup now uses `none` for new repositories, and GHES supports it from 3.20.
- `none` infers compilation units and flags, so precision can drop with heavy macro use or many
  external dependencies. `manual` (running the real CMake build between `init` and `analyze`) gives
  the most accurate results.

**Action.** `github/codeql-action` **v4** was released 2025-10-07 on Node 24. **v3 will be
deprecated in December 2026**, so new workflows must use `@v4`. The latest tag is **v4.38.2**
(2026-09-24) with CodeQL bundle 2.27.1 (2026-09-22). The `/releases/latest` endpoint returns the
bundle tag, not the action tag.

**Language support.**
- Compilers: Clang up to 22, GCC up to 16, and Visual Studio 2022.
- C++23 support is beta.
- **C++20 modules are not supported.** Header-only C++20 code without modules is fine.

**Permissions.** `security-events: write` (plus `contents: read`). Code scanning is free for public
repositories.

Sources:
- https://github.blog/changelog/2025-10-14-codeql-scanning-rust-and-c-c-without-builds-is-now-generally-available/
- https://github.blog/changelog/2025-06-03-codeql-can-be-enabled-at-scale-on-c-c-repositories-in-public-preview-using-build-free-scanning/
- https://github.blog/changelog/2025-10-28-upcoming-deprecation-of-codeql-action-v3/
- https://docs.github.com/en/code-security/reference/code-scanning/codeql/build-options-for-compiled-languages
- https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/
- https://github.com/github/codeql-action/releases

## 12. GitHub-hosted runner images and compilers

**Labels** (runner-images README on 2026-09-27):

- `ubuntu-latest` = **ubuntu-24.04**. Also available: `ubuntu-26.04`, `ubuntu-26.04-arm`,
  `ubuntu-24.04-arm`, `ubuntu-22.04`, `ubuntu-22.04-arm`, `ubuntu-slim`.
- `windows-latest` = **windows-2025**. Also available: `windows-2025-vs2026` (Visual Studio 2026
  variant), `windows-2022`, `windows-11-arm`, `windows-11-vs2026-arm`.
- `macos-latest` = **macos-26** (arm64). Also available: `macos-26-intel`, `macos-15` (arm64),
  `macos-15-intel`. `macos-14` is deprecated (runner-images issue #13518).

**Toolchains per image:**

| Image (version) | GCC | Clang / LLVM | CMake | Other |
|---|---|---|---|---|
| ubuntu-24.04 (20260920.314.1) | 12.4.0, 13.3.0, 14.2.0 | 16.0.6, 17.0.6, 18.1.3 (+ clang-format/tidy same) | 3.31.6 | Ninja 1.13.2, vcpkg, Python 3.12.3; no Doxygen / Conan / cppcheck / gcovr |
| ubuntu-26.04 (20260920.143.1) | 13.4.0, 14.3.0, 15.2.0 | 20.1.8, 21.1.8, 22.1.2 | **4.4.3** | Python 3.14.4 |
| windows-2025 (20260922.270.2) | MinGW 15.2.0 | LLVM 20.1.8 | 3.31.6 | VS Enterprise 2022 17.14.37710.0, VC runtime 14.51.36247, vcpkg |
| macos-15 arm64 (20260907.0337.1) | 13.4.0, 14.4.0, 15.3.0 (brew) | Apple Clang 17.0.0 (Xcode 16.4); brew LLVM 18.1.8 | 3.31.5 / 4.1.2 | Ninja 1.13.2 |
| macos-26 arm64 (20260907.0351.1) | 13.4.0, 14.4.0, 15.3.0 (brew) | Apple Clang 21.0.0 (Xcode 26.6); brew LLVM 20.1.8 | 3.31.5 / 4.1.2 | |

The latest upstream GCC is 16.2.0 (gcc-mirror tags), and no hosted image ships GCC 16 yet. Getting
GCC 16 or Clang 23 means installing them yourself, via `aminya/setup-cpp` v1.10.1, `apt.llvm.org`,
the Ubuntu toolchain PPA, or a container. Full C++20 support (including `<format>`, ranges and
concepts) is solid in GCC 13 and newer, Clang 17 and newer (with libc++ or libstdc++ 13 and newer),
MSVC 17.x and Apple Clang 17 and newer. That C++20 support claim is based on cppreference
compiler-support tables; I did not re-fetch them, so it is **unverified** here.

Other common actions:
- `actions/checkout` **v7.0.1** (2026-07-20). v7.0.0 (2026-06-18) refuses to check out fork PR code
  under `pull_request_target` and `workflow_run`. v6.0.0 (2025-11-20) moved to Node 24 and persists
  credentials in a separate file.
- `actions/cache` **v6.1.0** (2026-06-26).
- `actions/upload-artifact` **v7.0.1**.
- `hendrikmuhs/ccache-action` **v1.2.24**.

Sources:
- https://github.com/actions/runner-images
- https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md
- https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2604-Readme.md
- https://github.com/actions/runner-images/blob/main/images/windows/Windows2025-Readme.md
- https://github.com/actions/runner-images/blob/main/images/macos/macos-15-arm64-Readme.md
- https://github.com/actions/runner-images/blob/main/images/macos/macos-26-arm64-Readme.md
- https://github.com/actions/checkout/releases ; https://github.com/actions/cache/releases

## 13. Comparable C++ templates

| Template | Stars | Last push | License | Kind | Packaging | Quality / CI | Docs |
|---|---|---|---|---|---|---|---|
| [cpp-best-practices/cmake_template](https://github.com/cpp-best-practices/cmake_template) | 1809 | 2026-08-17 | Unlicense | Executable (FTXUI) | CPM | Big OS/compiler matrix, ASan+UBSan on by default, clang-tidy + cppcheck, warnings-as-errors, Catch2, libFuzzer, Codecov | No explicit Doxygen; WASM demo to Pages |
| [TheLartians/ModernCppStarter](https://github.com/TheLartians/ModernCppStarter) | 5408 | 2026-05-30 | Unlicense | Library + standalone | CPM, PackageProject.cmake (install/export/version header) | doctest, Format.cmake, clang-tidy/IWYU/cppcheck, sanitizers, Codecov, ccache | Doxygen to gh-pages |
| [filipdutescu/modern-cpp-template](https://github.com/filipdutescu/modern-cpp-template) | 1921 | 2025-12-26 | Unlicense | Library/exe | install/export, Conan and vcpkg | GTest/Catch2, clang-tidy/cppcheck, Codecov, ccache, Win/Linux/macOS CI | Doxygen |
| [friendlyanon/cmake-init](https://github.com/friendlyanon/cmake-init) | 2545 | 2026-04-15 | GPL-3.0 (generator) | Generator: exe / static / shared / header-only | Relocatable install, find_package, optional Conan or vcpkg, presets | clang-tidy, cppcheck, clang-format, codespell, sanitizers, lcov | Doxygen + m.css to Pages |
| [bsamseth/cpp-project](https://github.com/bsamseth/cpp-project) | 625 | 2023-09-19 (stale) | Unlicense | Exe + lib | none | Travis/Appveyor/GHA, Coveralls/Codecov, doctest | Doxygen |

Notes:
- The license of code generated by cmake-init (as opposed to the generator's own GPL-3.0) is
  **unverified**.
- None of these templates publishes to ConanCenter, vcpkg, NuGet, Homebrew, WrapDB, xmake-repo, BCR
  or build2, or covers release automation with changelog fragments. That gap is where this template
  can stand out.
- ModernCppStarter (CPM + install/export + Doxygen to Pages) and cmake-init (presets + header-only
  mode + relocatable install) are the closest references for the library side.
- cmake_template is the reference for strict warnings and sanitizers.

Source: GitHub REST API repo metadata (2026-09-27) and each repository's README (see `data/raw/online-templates-release.txt`).

## 14. Release automation

**Summary.** C++ has no native package-metadata file, so release tooling has to update the version
in `CMakeLists.txt` (`project(... VERSION x.y.z)`) and in any other version file.

- **release-please** (**v17.11.2**, 2026-08-24; `googleapis/release-please-action` **v5.0.0**,
  2026-04-22):
  - It has no C++ or CMake release type. Use `release-type: simple` (`version.txt` + `CHANGELOG.md`).
  - List further files under `extra-files` with the generic updater.
  - Mark lines with `x-release-please-version`, or a block with
    `x-release-please-start-version` … `x-release-please-end` (for example around
    `project(foo VERSION 1.2.3)`).
  - It opens a release PR from Conventional Commits and creates the tag and GitHub Release on merge.
- **semantic-release** (**v25.0.9**, 2026-08-05; v26.0.0-beta.2 prerelease 2026-09-25; about 24k
  stars):
  - Uses `@semantic-release/exec` (`prepareCmd` runs `sed`/`cmake` to bump the version) and
    `@semantic-release/git` to commit it.
  - Fully automatic, but it needs Node in CI.
- **Changelog-fragment tools** avoid merge conflicts in `CHANGELOG.md`, which matters when many
  AI-driven PRs run in parallel:
  - **changie v1.26.0** (2026-08-20, about 910 stars) is a language-agnostic Go binary with YAML
    fragments in `.changes/unreleased/`.
  - **towncrier 26.9.0** (2026-09-04, about 920 stars; Python, works for any language).
  - **scriv 1.8.0** (2025-12-30, about 300 stars).
  - **changesets** (`@changesets/cli@3.0.3`, 2026-09-14, about 12.4k stars) is Node/monorepo-oriented
    and awkward for CMake projects.
- **GitHub Release assets** (source tarball, CPack `.deb`/`.tar.gz`/`.zip`, `.nupkg`) can be attached
  with `softprops/action-gh-release` **v3.0.3** (2026-08-30) or `gh release create`.
- **Package-registry publishing after the tag:**
  - Conan: `conan create` + `conan upload`.
  - NuGet: `dotnet nuget push`.
  - vcpkg custom registry: an `x-add-version` commit.
  - BCR: `publish-to-bcr`.
  - Homebrew tap: formula bump.
  - These should all run as follow-up jobs triggered by `release: published`, or be chained in the
    same workflow.

Sources:
- https://github.com/googleapis/release-please ; https://github.com/googleapis/release-please/blob/main/docs/customizing.md
- https://github.com/googleapis/release-please-action
- https://github.com/semantic-release/semantic-release ; https://github.com/semantic-release/exec ; https://github.com/semantic-release/git
- https://github.com/miniscruff/changie ; https://github.com/twisted/towncrier ; https://github.com/nedbat/scriv ; https://github.com/changesets/changesets
- https://github.com/softprops/action-gh-release

---

## Recommended versions (as of 2026-09)

| Component | Latest (date) | Recommended pin / floor for the template | Source |
|---|---|---|---|
| CMake | 4.4.3 (2026-08-25) | `cmake_minimum_required(VERSION 3.25...4.4)`, presets schema 6; CI via `lukka/get-cmake` or PyPI `cmake` | Kitware/CMake, PyPI |
| Ninja | 1.13.2 | preinstalled on all images | runner-images, PyPI |
| GCC | 16.2.0 upstream; 15.2.0 on ubuntu-26.04 | GCC 13, 14, 15 in matrix | gcc tags, runner-images |
| Clang/LLVM | 23.1.2 (2026-09-22); 22.1.2 on ubuntu-26.04 | Clang 18 (24.04) and 22 (26.04); pin tools to one major | llvm-project |
| MSVC | VS 2022 17.14 (windows-2025); VS 2026 on `windows-2025-vs2026` | windows-2025 (+ optional vs2026 label) | runner-images |
| Apple Clang | 21.0.0 (Xcode 26.6, macos-26) | macos-latest (macos-26) + macos-15 | runner-images |
| Conan | 2.32.0 (2026-08-31) | Conan >= 2.x only (Conan 1 frozen) | conan-io/conan |
| conan-io/setup-conan | v1.4.0 (2026-06-04) | `@v1` | GitHub API |
| vcpkg | 2026.07.29 (tag), tool 2026-07-27 | `builtin-baseline` = pinned vcpkg commit | microsoft/vcpkg |
| lukka/run-vcpkg | v11.6 (2026-04-23) | `@v11` | GitHub API |
| lukka/get-cmake | v4.4.2 (2026-08-01) | `@latest` or pinned tag | GitHub API |
| CPM.cmake | v0.43.2 (2026-09-24) | v0.43.x | GitHub API |
| GoogleTest | v1.18.0 (2026-08-10) | v1.18.0 (needs C++17+) | GitHub API |
| Catch2 | v3.16.0 (2026-08-25) | v3.16.x | GitHub API |
| Doxygen | 1.18.0 (2026-08-13) | 1.17+ (awesome-css 2.5 support); distro doxygen acceptable | doxygen/doxygen |
| doxygen-awesome-css | v2.5.0 (2026-09-12) | v2.5.0 | GitHub API |
| actions/checkout | v7.0.1 (2026-07-20) | `@v7` (v6+ is Node 24) | GitHub API |
| actions/cache | v6.1.0 (2026-06-26) | `@v6` | GitHub API |
| actions/upload-artifact | v7.0.1 | `@v7` | GitHub API |
| actions/configure-pages | v6.0.0 (2026-03-25) | `@v6` | GitHub API |
| actions/upload-pages-artifact | v5.0.0 (2026-04-10) | `@v5` | GitHub API |
| actions/deploy-pages | v5.0.1 (2026-09-01) | `@v5` (README still shows v4) | GitHub API |
| github/codeql-action | v4.38.2 (2026-09-24), bundle 2.27.1 | `@v4` (v3 deprecated Dec 2026) | GitHub API, changelog |
| codecov/codecov-action | v7.1.1 (2026-09-17) | `@v7` (README still shows v5) | GitHub API |
| gcovr | 8.6 (2026-01-13) | 8.x via pip | GitHub API, PyPI |
| lcov | v2.5 (2026-07-06) | optional alternative | GitHub API |
| cppcheck | 2.22.0 (2026-09-19) | >= 2.14 (distro) or latest | GitHub API |
| include-what-you-use | 0.26 (2026-03-22) | optional job | GitHub API |
| clang-format (PyPI) | 23.1.1 | pin one major (e.g. `clang-format==22.*` or 23) | PyPI |
| clang-tidy (PyPI) | 22.1.8 | match compiler major | PyPI |
| cpp-linter/cpp-linter-action | v2.23.1 (2026-09-23) | `@v2` | GitHub API |
| hendrikmuhs/ccache-action | v1.2.24 (2026-08-31) | `@v1.2` | GitHub API |
| aminya/setup-cpp | v1.10.1 (2026-09-09) | `@v1` when newer toolchains are needed | GitHub API |
| softprops/action-gh-release | v3.0.3 (2026-08-30) | `@v3` (or `gh release`) | GitHub API |
| release-please / action | v17.11.2 / v5.0.0 | `@v5`, `release-type: simple` + generic updater | GitHub API |
| semantic-release | v25.0.9 (2026-08-05) | alternative only | GitHub API |
| changie / towncrier / scriv | v1.26.0 / 26.9.0 / 1.8.0 | changelog fragments (choose one) | GitHub API, PyPI |

## Implications for the template

**Library and build:**
- **Library shape:** use a header-only `INTERFACE` target with an `ns::name` alias,
  `target_compile_features(... cxx_std_20)` and `FILE_SET HEADERS`. Declare
  `cmake_minimum_required(VERSION 3.25...4.4)` and use presets schema 6 or newer, so workflow and
  package presets are available and every hosted runner works as-is.
- **Package config:** install and export with
  `configure_package_config_file` + `write_basic_package_version_file(COMPATIBILITY SameMajorVersion ARCH_INDEPENDENT)`.
  Keep `SemanticVersion` and `install(PACKAGE_INFO)` (CPS, CMake 4.3/4.4) opt-in, behind a CMake
  version check.
- **Consumer tests in CI:** verify consumption in all three modes, each as a small `test_package/`
  consumer:
  - `find_package` after `cmake --install`.
  - `FetchContent_Declare(... FIND_PACKAGE_ARGS)`, with CPM as a documented alternative.
  - `add_subdirectory` from a submodule.

  Guard tests, examples, docs and install rules with `PROJECT_IS_TOP_LEVEL`.

**Package channels:**
- **Conan 2 only:**
  - Ship a `conanfile.py` (`header-library`, `no_copy_source`, `self.info.clear()`) and a `test_package`.
  - CI runs `conan create .` via `conan-io/setup-conan@v1`.
  - An optional release job runs `conan upload` to a configurable remote.
  - A ConanCenter PR stays a manual, documented step (CLA, conandata.yml sha256, 30+ config CI).
- **vcpkg:**
  - Ship `vcpkg.json` for consumers, and a port under `ports/<name>/` (for overlay testing in CI with
    `lukka/run-vcpkg@v11`).
  - Document or automate a **git registry** (`x-add-version`).
  - Upstreaming to microsoft/vcpkg needs 6 months of maturity and lowercase SHA512 hashes via
    `vcpkg_from_github`, so it stays manual.
- **NuGet native:** generate a `.nuspec` (`native` tag, headers under `lib/native/include`) plus
  `build/native/<id>.targets` adding the include dir. Pack it on Windows and push on release.
  Consistent with the existing LinksPlatform `TemplateLibrary.targets` pattern. Avoid CoApp.
- **Cheap extras:**
  - A generated `.pc` file.
  - CPack `DEB` + `TGZ` + `ZIP` package presets, attached to GitHub Releases.
  - A Homebrew **tap** formula; homebrew-core needs 225 stars for self-submission.
- **Documented-only (templates/snippets, manual PRs):** xmake-repo (PR to `dev`), Meson WrapDB
  (`releases.json`, reviewer other than submitter), Spack (`spack-packages`, `CMakePackage`), BCR
  (`publish-to-bcr` workflow) and build2 (`bdep publish`, needs a second build description).

**Docs and CI quality:**
- **Docs:**
  - Doxygen 1.17 or newer with doxygen-awesome-css v2.5.0 (submodule or FetchContent pinned to the tag).
  - `WARN_AS_ERROR = FAIL_ON_WARNINGS`.
  - `doxygen_add_docs` target.
  - Deploy with `configure-pages@v6` → `upload-pages-artifact@v5` → `deploy-pages@v5`, only on main
    and release, with `pages: write` + `id-token: write`.
  - Install Doxygen explicitly, because no runner image has it.
- **Compiler matrix:**
  - ubuntu-24.04 (GCC 13/14, Clang 18) and ubuntu-26.04 (GCC 15, Clang 22, CMake 4.4).
  - windows-2025 (MSVC 17.14; optionally `windows-2025-vs2026`).
  - macos-26 (Apple Clang 21) and optionally macos-15.
  - Avoid macos-14, which is deprecated. Newer GCC 16 or Clang 23 only via setup-cpp or containers.
- **Sanitizers and coverage:**
  - An ASan+UBSan job (`-fno-sanitize-recover=all`) and a separate TSan job on Linux with Clang 18
    or newer; guard against the `mmap_rnd_bits` issue.
  - MSVC `/fsanitize=address` only on Windows. Skip MSan.
  - Coverage via gcovr 8.x (Cobertura or LCOV) uploaded with `codecov/codecov-action@v7` using OIDC.
- **Lint:**
  - Pin clang-format to one LLVM major (pip wheel) in both pre-commit and CI.
  - clang-tidy with `compile_commands.json` and `WarningsAsErrors`, via
    `cpp-linter/cpp-linter-action@v2` for PR feedback.
  - cppcheck 2.x as a blocking job. IWYU as optional or advisory.
- **Security:**
  - CodeQL with `language: c-cpp`, `github/codeql-action@v4` (never v3, which is deprecated in
    December 2026).
  - Use `build-mode: manual` with the real CMake preset for accuracy, or `none` for a zero-config
    fallback. C++20 modules are not analyzable, so do not use modules in the template.
- **Actions pins:** `actions/checkout@v7` (safer fork handling), `actions/cache@v6`,
  `actions/upload-artifact@v7`, `hendrikmuhs/ccache-action@v1.2`. Every current major runs on
  Node 24. Where README examples lag behind releases (deploy-pages, codecov), follow the release tags.

**Releases:**
- **Release automation:**
  - Use changelog fragments to avoid conflicts between parallel AI PRs (changie or towncrier, both
    language-agnostic).
  - Bump the version in one place (`project(VERSION)`, optionally mirrored to `version.txt`) and
    tag `vX.Y.Z`.
  - Create the GitHub Release (`softprops/action-gh-release@v3` or `gh`).
  - Then fan out to the Conan remote, NuGet, the vcpkg registry, Pages and CPack assets.
  - release-please (`simple` + generic `x-release-please-version` markers) is the main off-the-shelf
    alternative.
- **Differentiation:** no popular template (cmake_template, ModernCppStarter, modern-cpp-template,
  cmake-init) automates publishing to package registries. Covering install/export, Conan, vcpkg,
  NuGet, CPack and Pages in one tested pipeline is the template's unique value.
