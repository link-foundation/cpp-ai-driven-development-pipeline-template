---
bump: patch
---

### Fixed
- Pin runner OS labels and the lychee/zizmor action hashes across all workflows,
  enforce the policies with tests, and configure Git's initial branch everywhere.
- Verify NuGet API-key package/glob and owner scope with the one-time verification
  flow, reporting first-push and network uncertainty without claiming access.

### Added
- NuGet trusted publishing in automatic and instant releases, selected with
  `NUGET_USER`, with the existing API-key secret retained as a fallback.
