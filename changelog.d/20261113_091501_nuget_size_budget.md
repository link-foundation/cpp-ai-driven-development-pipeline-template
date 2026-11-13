---
bump: patch
---

### Fixed
- Reject NuGet packages above a configurable compressed byte budget during packaging, PR validation and immediately before publishing, with largest-entry diagnostics; identify HTTP 413 uploads as non-retryable.
