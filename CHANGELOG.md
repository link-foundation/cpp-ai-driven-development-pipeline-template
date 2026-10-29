# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Unreleased changes are kept as fragments in [changelog.d/](changelog.d/) and
collected here by the release pipeline.

## [0.2.2] - 2026-10-29

### Fixed
- Back off between every round of unanswered-link retries, respect the retry
  budget between requests, and keep final broken links from clearing the gate.
- Fail the Web Archive check when its expected lychee report is missing.

### Fixed
- Retain up to 100 waiting repository writers across release and Pages jobs
  with a shared concurrency group and `queue: max`.
- Validate the new queue field independently while keeping every other
  actionlint check enabled.

### Security
- Pin every remote workflow action to a reviewed full commit SHA and enforce
  the policy for all namespaces while Dependabot maintains updates.

### Security
- Fail Security on CodeQL findings, failed tool diagnostics, incomplete scans
  or missing SARIF, and retain reports for review.
- Trace the real C++20 build, consumers and Conan package test instead of
  inferring compiler flags and accepting partial extraction.
- Prebuild pinned external libraries outside the checkout before tracing,
  and explicitly discard benchmark iteration variables flagged by CodeQL.
- Audit the full Python CI dependency tree and resolved native dependencies
  on pull requests, main, schedules and manual runs, retaining coordinates
  and rejecting vulnerabilities or incomplete provider coverage.

## [0.2.1] - 2026-10-07

### Fixed
- Pin runner OS labels and the lychee/zizmor action hashes across all workflows,
  enforce the policies with tests, and configure Git's initial branch everywhere.
- Verify NuGet API-key package/glob and owner scope with both the temporary and
  original keys, reporting first-push and network uncertainty without claiming
  access even when the temporary key's rewritten glob verifies successfully.

### Added
- NuGet trusted publishing in automatic and instant releases, selected with
  `NUGET_USER`, with the existing API-key secret retained as a fallback.

## [0.2.0] - 2026-09-28

### Added
- C++ CI/CD pipeline (`.github/workflows/release.yml`) with the job graph of the link-foundation Rust, Python, JavaScript and PHP templates: change detection, release credential preflight, changelog and version checks, secrets scan, fresh-merge simulation, lint (clang-format, clang-tidy, cppcheck), a GCC/Clang/Apple Clang/MSVC test matrix, sanitizers, coverage, release script tests, packaging of every channel, automatic and manual releases, and a terminal pipeline status gate.
- Single-language (C++ at the root, tags `v1.2.3`) and multi-language (C++ under `cpp/`, tags `cpp_v1.2.3`) repository layouts.
- Distribution through the repository itself (`add_subdirectory`, git submodule, `FetchContent`, CPM.cmake), `find_package` after `cmake --install`, pkg-config, GitHub release assets, a vcpkg overlay port, Conan 2 and native NuGet packages, each checked by CI.
- Doxygen API reference built on every change and deployed to GitHub Pages, plus CodeQL, dependency review, broken link and workflow lint workflows.
- `scripts/rename_project.py` to rename the placeholder package after creating a repository from the template.
