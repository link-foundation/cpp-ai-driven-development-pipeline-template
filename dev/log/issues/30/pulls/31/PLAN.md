# Issue 30 / PR 31 work plan

Objective: implement and verify every issue requirement in this PR; leave the PR unmerged.

## Requirement inventory and acceptance evidence

| Requirement | Solution and planned evidence | Status |
| --- | --- | --- |
| Read issue, comments, required sub-issues and all three PR comment types | Raw API snapshots under `raw/`; no sub-issues or review feedback exist initially | Complete |
| Investigate failures after merged PRs 26/27 without reverting updates | Preserve default branch run timestamps/SHAs/logs; fix actual failures with regression tests | Diagnosed: missing Conan credential, see ANALYSIS.md |
| Python first: every direct/transitive tool current, honest constraints and committed resolution | Query PyPI; pin direct tools; compile complete portable lock; install and audit exact resolved tree | Implemented; see ANALYSIS.md and VERIFICATION.md |
| Every Actions reference, including images and reusable/composite actions | Query upstream releases, dereference immutable commits/digests, read manifests and major migrations | Implemented; see ANALYSIS.md and VERIFICATION.md |
| Every pre-commit hook and updater coverage | Query releases; autoupdate; align clang-format; add missing Dependabot ecosystems | Implemented; see ANALYSIS.md and VERIFICATION.md |
| Shell/CMake/C++ dependencies and toolchains | Audit downloads, native libraries, vcpkg baseline, Python, CMake, compiler, .NET and runner versions; record exceptions | Implemented, distribution exceptions explicit in DEPENDENCIES.md |
| Registry-derived before/latest tables for every ecosystem | Record registry metadata and a complete dependency table, including unchanged pins and exceptions | Implemented, distribution exceptions explicit in DEPENDENCIES.md |
| Read migration docs for major bumps; use new upstream features | Save migration analysis and remove redundant local logic where an upstream feature fits | Implemented; see ANALYSIS.md and VERIFICATION.md |
| One consistent version wherever dependency is actively used | Search entire codebase including tests/docs; historical evidence remains immutable and marked historical | Implemented; see ANALYSIS.md and VERIFICATION.md |
| Full build/test/lint and no introduced deprecations | Full Python tests, C++ build/tests, lint, consumers, packaging, docs and CI for current SHA | Local suite passed; current-head hosted CI pending |
| No unresolved security advisories | Exact Python lock audit and native dependency audit with retained coordinates and verdicts | Unfinished: external credential / upstream CLI advisories |
| Report dependency bugs/features/duplicated logic upstream | Search existing reports, report concrete confirmed issues with reproducer, affected versions, workaround and proposal; link PR | Existing reports confirmed; new release/range reports in progress |
| Research existing components and solutions | Compare pip-tools/uv, Dependabot/Renovate, Conan audit/OSV; record sources and choices | Implemented; see ANALYSIS.md and VERIFICATION.md |
| Prepare next release | Add patch changelog fragment (repository uses automatic version bumps) | Implemented; see ANALYSIS.md and VERIFICATION.md |
| Preserve atomic commits and push only prepared branch | Verify branch before mutations; regular commits/pushes; final clean status | In progress; final hosted CI and review pending |
| Keep default branch included; update PR title/body, close #30, ready only when done | Fetch/merge main as needed; review gh pr diff; current-head CI; positive closing reference | In progress; final hosted CI and review pending |
| Default branch green again | Diagnose/fix in PR; cannot change main without merging, which is outside authorized branch workflow; report remaining external setup explicitly | Unfinished: external credential / upstream CLI advisories |

## Sequence

1. Complete source/log/dependency inventory and online research; record before/latest versions before edits.
2. Update Python and locks, then actions, hooks, native tools and all matching active references.
3. Fix failures without weakening scans or skipping tests; add minimal regression tests for actual bugs.
4. Run resource-bounded sequential verification and audits; commit/push; inspect every current-head CI failure.
5. Finish evidence, upstream reports and PR description; review final diff, current base, clean status and CI; mark ready when acceptance criteria allow.

## Initial findings

- Branch `issue-30-fb8c705cf350`, initial head `df7f56b`, base `2565890`.
- Default branch Security run 43575793401 fails at log line 595: missing `CONAN_AUDIT_PROVIDER_TOKEN_CONANCENTER`; aggregate failure at line 4952. The script already warns for pull requests and fails on main/schedules with explicit setup instructions. This is a real external-credential blocker until a complete credential-free audit or configured credential is available.
- Default branch CI/CD, Docs and Workflows passed after both merged updates; the initial changelog failure is stale.
- No UI work is required. No screenshots or attachments occur in the issue or PR.
- No AGENTS.md files were found. No sub-agents are authorized or used.
