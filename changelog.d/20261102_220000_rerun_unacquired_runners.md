---
bump: patch
---

### Fixed
- Re-run a CI/CD Pipeline run automatically, at most twice, when a job was
  never acquired by a hosted runner (no steps, no runner, "not acquired"
  annotation), so a macOS capacity shortage on `main` no longer blocks the
  release until someone re-runs it by hand. Jobs that ran steps and failed
  are never re-run.
- Make the Pipeline Status gate name runner-acquisition failures as
  infrastructure failures instead of reporting them as code failures.

### Added
- Opt-in `MACOS_NON_BLOCKING` repository variable that runs the macOS test leg
  as a non-blocking, separately annotated signal.
