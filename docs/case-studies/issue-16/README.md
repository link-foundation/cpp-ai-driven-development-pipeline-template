# Issues 13–16: workflow reliability and security

## Scope and work plan

Issue 16 requires all three native sub-issues in one PR, with `Fixes #13`,
`Fixes #14`, `Fixes #15`, and `Fixes #16` in the PR description. All issue
bodies and comments, PR conversation comments, inline comments and reviews
were read before implementation; there were no additional comments.

1. [x] Read repository guidance, every issue and PR discussion, and recent
   related merged PRs; inspect every workflow and shared helper.
2. [x] Research official documentation and existing components.
3. [x] Add bounded reproducing regressions before each fix; retain logs in
   `ci-logs/` locally and experiment scripts under `experiments/`.
4. [x] Implement each fix across the entire active workflow tree, retaining
   existing features and bounded push retries; commit useful atomic steps.
5. [x] Run the full script suite, local C++ checks, workflow linters and
   security regressions within the container's memory budget.
6. [x] Fetch and merge main if needed, review the PR diff, update its title,
   analysis, tests and closing references, push only the prepared branch.
7. Final CI timestamps, head SHA, log investigation, clean-tree confirmation
   and PR readiness are recorded in PR 17, so subsequent verification does
   not require another source commit that restarts CI.

## Requirement inventory, alternatives and implementation plans

| Source | Requirement | Options and selected plan | Verification |
| --- | --- | --- | --- |
| 16 | Read all three issues, comments and required sub-issues | Inventory native sub-issues and closing block, then read all discussion endpoints | Scope above; no nested sub-issues |
| 16 | Implement everything in this single PR; defer nothing | Separate commits in PR 17; keep every acceptance criterion here | PR diff and CI |
| 16 | Close parent and each issue with its own positive keyword | Use the four individual `Fixes` lines | Final PR description |
| 16 | Explicitly identify already-resolved/unreproducible issues | Reproduce each defect first; document any exceptions | Regression results below |
| 13 | Preserve queued main writers, including third and later arrivals | Native `queue: max` avoids a separate queue service | Workflow policy regression |
| 13 | All repository/main writers share one group and never cancel | Repository-wide literal group, false cancellation, max queue; include release, changelog and Pages writers | Enumerate all writing jobs, including Pages configuration |
| 13 | Read-only jobs keep distinct groups | Leave independent read-only checks job-scoped | Workflow policy regression |
| 13 | Retain bounded non-fast-forward recovery and never force push | Keep existing three-attempt retry and policy-error classification | Existing release tests; no forced pushes |
| 13 | Enumerate every remote action and pin reviewed full SHAs | Resolve existing release tags, peel annotated tags, inspect manifests, record pins; Docker uses image digest | Pin inventory and policy tests |
| 13 | Dependabot updates action pins | Retain existing GitHub Actions update group; remove trusted-namespace pin exemptions | Dependabot/policy checks |
| 13 | Work around actionlint 1.7.12 queue rejection independently | Validate block-style queue placement/value/cancellation, then comment out only those validated lines in the disposable checkout; leave all other lines unchanged for actionlint | Valid/invalid queue fixtures, inline/quoted forms and unrelated syntax/shell failures |
| 14 | Single failing URL sleeps before second attempt | Explicit first-round state and doubling delay | Mocked sleep equals 0.001 seconds |
| 14 | Multiple URLs collapsing to one still back off | Round state independent of pending count | Multi-URL regression |
| 14 | Finite retry budget remains effective | Check deadline before sleeping and before subsequent requests | Virtual-clock budget regression |
| 14 | Missing lychee report fails and writes all_archived=false | Return nonzero with actionable error | Missing report regression |
| 14 | Valid empty-error report succeeds | Keep empty-error handling distinct from missing artifact | Empty-error report regression |
| 14 | Broken live links fail even with archive copies | Keep workflow's live-link gate and ensure recovered transport failures never hide final 404/local errors | Mixed-report and workflow regressions |
| 15 | Full direct/transitive dependency audit on PR, main and schedule | Ecosystem-native audit tools, independently of dependency review; include CI Python tools, native developer dependencies, vcpkg helpers and CPM bootstrap | Workflow policies, resolved inventory and provider reports |
| 15 | Fatal verdict on CodeQL findings | Validate retained SARIF locally after analyze instead of relying on asynchronous upload checks | Analysis-success/finding fixture exits nonzero |
| 15 | Reject failed diagnostics, absent/empty invocations, unknown execution state and missing reports | Strict fail-closed SARIF validator; all finding levels are fatal | Malformed/incomplete scan fixtures |
| 15 | Retain SARIF and resolved dependency coordinates | Upload artifacts even on failure | Workflow artifact policies |
| 15 | Native audit uses supported provider, reports authorization/unknown-package gaps explicitly | ConanCenter audit provider; preserve graph and validate provider coverage, rather than treating an empty OSV match as proof of coverage | Coverage/auth/unknown-package regressions |
| 15 | Audit NuGet dependencies with locked/transitive auditing when applicable | This native package has no NuGet dependency tree; verify this rather than introduce an unrelated managed project | Packaging metadata check and documented applicability |
| 15 | Findings/incomplete scan fail terminal workflow gate | Add mandatory audit dependencies to existing Pipeline Status; no continue-on-error on enforcement | Gate integration regressions |
| 15 | Stay within this C++ template's scope | No copied Python/Rust/NuGet distribution projects | Review diff |

## Research and existing components

- [GitHub concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency):
  the default replaces a waiting job, while `max` retains up to 100. Ordering
  is by entry into the waiting queue, not by workflow dispatch time.
- [actionlint issue 657](https://github.com/rhysd/actionlint/issues/657) and
  [duplicate 746](https://github.com/rhysd/actionlint/issues/746): the pinned
  1.7.12 rejects the new queue key. A broad syntax suppression would hide
  unrelated errors. Only validated block-style queue lines are removed from
  its input; all other fields and diagnostics remain unchanged.
- [Conan audit](https://docs.conan.io/2/reference/commands/audit.html) and
  [provider response contract](https://docs.conan.io/2.32/reference/extensions/python_api/AuditAPI.html):
  supports native dependency graphs and reports unknown packages explicitly.
  ConanCenter requires a free provider token. Missing coverage is an incomplete
  audit, never a clean result.
- [OSV-Scanner supported inputs](https://google.github.io/osv-scanner/supported-languages-and-lockfiles/):
  supports Conan locks and C++ commit scanning, but a no-match response alone
  cannot distinguish an unknown native package from a covered clean package.
  It is an alternative to ConanCenter, not a substitute for coverage checks.
- [pip-audit](https://github.com/pypa/pip-audit): resolves requirements and
  audits their transitive Python dependencies. Keep its report and reject
  skipped/unknown packages as incomplete. Include the pinned zizmor package
  invoked through pipx as well as the CI requirements.
- [CPM.cmake](https://github.com/cpm-cmake/CPM.cmake): the consumer bootstraps
  this existing CMake dependency manager. Retain its explicit version and
  SHA256, and submit its provider coordinate alongside the resolved graphs.
  An unsupported provider coordinate must fail as unknown rather than vanish
  from the inventory.
- [CodeQL analyze action](https://github.com/github/codeql-action/tree/main/analyze)
  can retain SARIF via its `output` input. Analysis/upload success is separate
  from the finding verdict, which is enforced by the new local validator.

## Reproduction and verification evidence

The local reproduction logs are deliberately kept outside tracked sources in
`ci-logs/`. `experiments/check_actionlint_queue.py` retains the bounded linter
experiment so it can be repeated with actionlint 1.7.12 and shellcheck.

- The original link helpers failed five reproducing regressions; all 32
  focused link tests pass after the fix. The additional mixed-report test
  prevents a recovered connection reset from hiding a final HTTP/local error.
- The original workflow tree failed the writer and full-SHA policies.
  All active workflows now pass those policies. Historical workflow snapshots
  under `docs/case-studies/issue-1/data/` are evidence, not executable workflows.
  [The pin inventory](action-pins.json) records resolved commits and reviewed
  upstream manifests. The dependency-review action publishes `v5.0.0` without
  a moving `v5` tag, so its reviewed release commit is used.
- Security regressions cover all finding levels, failed/unknown invocations,
  missing reports, provider refusals, unknown packages, transitive host/build
  packages and propagation of each failed job to the terminal gate. Missing
  native authorization is tested on PR, push, weekly and manual events, in
  both single-language and `cpp/` layouts. All 399 script tests pass, including
  127 focused security/workflow tests. Four additional queue edge-case failures found
  during review now pass, and the compatibility
  experiment also checks mismatched quotes and missing YAML separators.
  The CPM and pipx inventory omissions each have a failing-before regression.
- Debug, Release, ASan/UBSan and coverage presets each pass all ten C++ tests;
  line/function coverage is 100% (branch coverage 93.3%). Format, clang-tidy,
  cppcheck, all five consumer examples, required-document checks, Doxygen,
  actionlint with shellcheck, and regular/selected pedantic zizmor checks pass.
- A real strict Python audit found no known vulnerabilities across 49 resolved
  packages. Real native resolution retained `gtest/1.18.0`, `benchmark/1.9.5`,
  `cmake/4.4.4`, `vcpkg-cmake/2025-08-07` and
  `vcpkg-cmake-config/2026-07-21` and `cpm-cmake/0.42.0`, including CPM's
  integrity pin. No provider token is configured in this
  repository: native coverage is explicitly **incomplete**, not clean. PRs
  report this setup gap; main/weekly/manual runs fail until configured. Unknown
  provider packages remain fatal even after credentials are added.

Final commit-SHA-specific CI results and remaining work-plan verification are
tracked in [PR 17](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/pull/17).
