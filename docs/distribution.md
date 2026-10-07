# Distribution channels

The library is distributed through every common C/C++ channel from one source
of truth: `project(VERSION)` in `CMakeLists.txt`. The CMake package config,
pkg-config file, Conan recipe, vcpkg port, NuGet package and GitHub release
all take their version from it, and every channel installs the same files as
`cmake --install`.

CI proves each channel on every pull request, before anything is published:

| Channel | Checked by | Job |
| --- | --- | --- |
| `add_subdirectory` / git submodule | `scripts/check_consumers.py` | Test (all platforms) |
| `FetchContent` | `scripts/check_consumers.py` | Test (all platforms) |
| CPM.cmake | `scripts/check_consumers.py` | Test (all platforms) |
| `find_package` after `cmake --install` | `scripts/check_consumers.py` | Test (all platforms) |
| pkg-config | `scripts/check_consumers.py` | Test (Linux, macOS) |
| GitHub release assets | `scripts/package_release.py` | Build Packages |
| NuGet | `scripts/check-nuget-package.sh` (real `dotnet restore`) | Build Packages |
| Conan 2 | `conan create` with `test_package/` | Build Packages |
| vcpkg | `scripts/check-vcpkg-port.sh` (real `vcpkg install`) | Build Packages |

The snippets below use the placeholder name `my_package` (vcpkg port
`my-package`) and this repository; `scripts/rename_project.py` rewrites them.

## The repository as the distribution

### add_subdirectory and git submodules

```bash
git submodule add https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template.git external/my_package
```

```cmake
add_subdirectory(external/my_package EXCLUDE_FROM_ALL)
target_link_libraries(app PRIVATE my_package::my_package)
```

Tests, examples, benchmarks, docs and install rules are only enabled when the
library is the top-level project (`PROJECT_IS_TOP_LEVEL`), so a consumer only
gets the `my_package::my_package` target.

### FetchContent

```cmake
include(FetchContent)
FetchContent_Declare(
    my_package
    GIT_REPOSITORY https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template.git
    GIT_TAG v1.2.3
    GIT_SHALLOW TRUE
    FIND_PACKAGE_ARGS CONFIG   # CMake 3.24+: prefer an installed copy
)
FetchContent_MakeAvailable(my_package)
target_link_libraries(app PRIVATE my_package::my_package)
```

Instead of the git repository you can also download the release source
archive (`URL .../my-package-1.2.3.tar.gz` with `URL_HASH SHA256=...` from
`SHA256SUMS`), which is smaller and reproducible.

### CPM.cmake

```cmake
CPMAddPackage(
    NAME my_package
    GITHUB_REPOSITORY link-foundation/cpp-ai-driven-development-pipeline-template
    VERSION 1.2.3
    GIT_TAG v1.2.3
)
target_link_libraries(app PRIVATE my_package::my_package)
```

In a multi-language repository the C++ project is in `cpp/`: add
`SOURCE_SUBDIR cpp` to `FetchContent_Declare` and `CPMAddPackage`, use the
`cpp_v1.2.3` tag, and `add_subdirectory(external/repo/cpp)`. The release
source archives contain only the `cpp/` directory, so they need no
`SOURCE_SUBDIR`.

## Installed packages

### find_package

```bash
cmake --preset install            # Release, tests and examples off
cmake --build build/install
cmake --install build/install --prefix /opt/my_package
```

```cmake
find_package(my_package 1.2 CONFIG REQUIRED)   # SameMajorVersion compatibility
target_link_libraries(app PRIVATE my_package::my_package)
```

Configure the consumer with `-DCMAKE_PREFIX_PATH=/opt/my_package`. The
package config is installed under `share/cmake/my_package` because a
header-only library is architecture independent.

### pkg-config

```bash
PKG_CONFIG_PATH=/opt/my_package/share/pkgconfig pkg-config --cflags my_package
```

## GitHub releases

Every release has these assets (`scripts/package_release.py`):

| Asset | Contents |
| --- | --- |
| `my-package-1.2.3.tar.gz`, `.zip` | reproducible `git archive` of the C++ project |
| `my-package-1.2.3-install.tar.gz` | the `cmake --install` tree: headers, CMake config, pkg-config, license |
| `my-package-vcpkg-port-1.2.3.tar.gz` | a vcpkg overlay port that downloads the source archive, pinned by SHA512 |
| `my_package.1.2.3.nupkg` | the native NuGet package |
| `SHA256SUMS` | checksums of all of the above |

The release notes are the `CHANGELOG.md` entry of the version plus install
instructions. linksplatform repositories name their archives
`platform.<repo>_<version>`; set the `RELEASE_ARCHIVE_BASENAME` repository
variable to keep such a naming, e.g. `platform.numbers_{version}` (the
`{version}` placeholder is replaced; without it the version is appended).

## vcpkg

**Overlay port** (no registry needed): unpack the port asset of a release and
point vcpkg at it.

```bash
tar -xzf my-package-vcpkg-port-1.2.3.tar.gz -C ports
vcpkg install my-package --overlay-ports=ports
```

```cmake
find_package(my_package CONFIG REQUIRED)
target_link_libraries(app PRIVATE my_package::my_package)
```

**Custom registry**: copy the unpacked port into `ports/my-package/` of a git
registry and add the version to `versions/`. `scripts/render_vcpkg_port.py
--github-repo OWNER/REPO --ref v1.2.3 --sha512 HASH` renders a port that uses
`vcpkg_from_github`, which curated registries prefer.

**The curated registry** (microsoft/vcpkg): submit the rendered port in a pull
request to microsoft/vcpkg once the library is stable enough for it.

The root `vcpkg.json` is the manifest for developing this project with vcpkg
(its `tests` and `benchmarks` features provide GoogleTest and Google
Benchmark); configure with `-DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
-DVCPKG_MANIFEST_FEATURES=tests`.

## Conan 2

```bash
conan create . -s compiler.cppstd=20 --build=missing   # build and run test_package
```

Consumers add `my_package/1.2.3` to their `requires` and use the
`CMakeDeps` generator (`find_package(my_package CONFIG REQUIRED)`) or
`PkgConfigDeps`. The recipe reads the version from `CMakeLists.txt` and
packages the output of the project's own install rules. As a header-only
package, its package id ignores settings, so one binary package serves every
configuration.

**Publishing**: set the `CONAN_REMOTE_URL` variable (for example an Artifactory
or GitLab Conan remote) and the `CONAN_LOGIN_USERNAME` / `CONAN_PASSWORD`
credentials. The release job then runs `conan create`, `conan remote auth
--strict` and `conan upload`. For ConanCenter, submit the recipe to
conan-io/conan-center-index instead.

## NuGet

The native NuGet package follows the linksplatform `TemplateLibrary`
convention: the headers under `lib/native/include` and
`build/native/<id>.targets`, which adds them to the include path of every
Visual Studio C++ project that references the package (and selects C++20
unless the project asks for a newer standard). `scripts/pack_nuget.py` builds
it with the Python standard library only, so no `nuget.exe` is needed.

```bash
python3 scripts/pack_nuget.py --out-dir dist --id Platform.Example.TemplateLibrary
bash scripts/check-nuget-package.sh dist/Platform.Example.TemplateLibrary.1.2.3.nupkg
```

**Publishing**: set the repository variables `NUGET_PUBLISH=true` and
`NUGET_PACKAGE_ID`, then choose either authentication mode:

- **Trusted publishing**: register a
  [nuget.org trusted publishing policy](https://learn.microsoft.com/en-us/nuget/nuget-org/trusted-publishing)
  with this repository's owner and name, workflow file `release.yml` (file
  name only), and the appropriate package owner, push scopes and glob.
  Leave the policy's environment empty: the release jobs do not declare a
  GitHub environment. Set the repository variable `NUGET_USER` to the
  nuget.org profile name, not an email address. Both automatic and instant
  releases use `NuGet/login` to exchange GitHub OIDC credentials for an API
  key valid for one hour, immediately before the publishing script runs.
- **API key fallback**: leave `NUGET_USER` unset and configure the
  `NUGET_API_KEY` secret with push scope, the correct package glob and owner.
  Existing API-key configurations keep working. If `NUGET_USER` is set,
  trusted publishing takes priority and login failures stop the release.

Preflight reports which mode is selected. In API-key mode, obtaining a
one-time verification key checks validity and general push scope, then
verification against a published version checks the package glob and owner.
A refused key or scope blocks the release; a package with no published
versions has `unknown` scope because its first push cannot be checked this
way. Trusted publishing is also `unknown` during preflight: the actual token
exchange happens in the publishing job. Network errors and malformed
responses never count as proof of access. See
[credential checks](ci-cd.md#variables-and-secrets) for the verdict rules.

## Other channels

These channels need a submission to a third-party repository rather than a
CI step, so they are not automated. Each can reuse the release source archive
and its SHA256 from `SHA256SUMS`:

- **Homebrew**, **Spack**, **Meson WrapDB**, **xmake-repo**, **build2
  (cppget.org)** and the **Bazel Central Registry** accept a recipe that
  downloads the release source archive.
- **Debian/RPM packages** can be generated from the install rules with CPack
  (`include(CPack)` in `CMakeLists.txt`).

The research behind these choices is in
[docs/case-studies/issue-1](case-studies/issue-1/README.md).

## Switching to a compiled library

The template library is header-only (an `INTERFACE` target). For a library
with sources:

1. In `CMakeLists.txt`, replace `add_library(${PROJECT_NAME} INTERFACE)` with
   `add_library(${PROJECT_NAME})` plus the sources, change the `INTERFACE`
   keywords to `PUBLIC`, and call `my_package_apply_project_options()` on it.
   `BUILD_SHARED_LIBS` then selects a static or shared build.
2. In `cmake/PackageInstall.cmake`, install the package config under
   `${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}`, drop `ARCH_INDEPENDENT`,
   and add the library to `cmake/package.pc.in` (`Libs:`).
3. In `conanfile.py`, set `package_type = "library"`, add the `shared` and
   `fPIC` options, build with `cmake.build()`, remove the `package_id()`
   override, and set `self.cpp_info.libs`.
4. In `packaging/vcpkg/portfile.cmake.in`, remove `set(VCPKG_BUILD_TYPE release)`
   and point `vcpkg_cmake_config_fixup` at `lib/cmake`.
5. NuGet packages of compiled libraries need per-platform binaries under
   `lib/native/<platform>`; extend `scripts/pack_nuget.py` or stop publishing
   to NuGet.
