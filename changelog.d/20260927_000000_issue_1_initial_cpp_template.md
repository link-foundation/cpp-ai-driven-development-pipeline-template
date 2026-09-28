---
bump: minor
---

### Added
- C++ CI/CD pipeline (`.github/workflows/release.yml`) with the job graph of the link-foundation Rust, Python, JavaScript and PHP templates: change detection, release credential preflight, changelog and version checks, secrets scan, fresh-merge simulation, lint (clang-format, clang-tidy, cppcheck), a GCC/Clang/Apple Clang/MSVC test matrix, sanitizers, coverage, release script tests, packaging of every channel, automatic and manual releases, and a terminal pipeline status gate.
- Single-language (C++ at the root, tags `v1.2.3`) and multi-language (C++ under `cpp/`, tags `cpp_v1.2.3`) repository layouts.
- Distribution through the repository itself (`add_subdirectory`, git submodule, `FetchContent`, CPM.cmake), `find_package` after `cmake --install`, pkg-config, GitHub release assets, a vcpkg overlay port, Conan 2 and native NuGet packages, each checked by CI.
- Doxygen API reference built on every change and deployed to GitHub Pages, plus CodeQL, dependency review, broken link and workflow lint workflows.
- `scripts/rename_project.py` to rename the placeholder package after creating a repository from the template.
