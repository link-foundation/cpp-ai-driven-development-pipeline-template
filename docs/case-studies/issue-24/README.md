# Issues 22–24: dependency validation and NuGet upload budgets

## Scope and plan

Read issue #24, its native sub-issues #22 and #23, all issue comments, and
PR #25 conversation comments, inline comments and reviews. There were no
comments or additional sub-issues at investigation time (2026-11-13).
All changes belong to PR #25; keep separate `Fixes` references for all three
issues. Neither bug was already resolved.

| Requirement | Chosen solution | Verification |
| --- | --- | --- |
| #22: count CI/security requirements as code | Recognize `requirements*.txt` after project scope and folder exclusions | Pattern tests and requirements-only real-git PR tests, root and `cpp/` layouts |
| #22: tool upgrades must run checks | Requirements enable all three detector outputs; Security already runs independently | Gate assertions; current PR CI |
| #22: regression asserting `scripts/requirements-ci.txt` is code | Parameterized assertions cover both shared manifests | Tests fail against original classifier |
| #22: rerun PR #21 so upgrades are exercised | Include PR #21's exact dependency updates here and align executable zizmor pins and resolve upgrade findings | Current PR CI runs the upgraded tools; historical run rerun requested (see below) |
| #23: configurable budget below about 250 MB | Standard-library checker, default 249,000,000 compressed bytes; positive integer environment/repository variable | Exact boundary, default/empty, invalid values, missing/corrupt ZIP tests |
| #23: error annotation and largest ZIP entries | Reject over-budget archives, list top ten by compressed size with uncompressed sizes | Diagnostic and ordering assertions |
| #23: gate on PRs | Enforce in `pack_nuget.pack` and before local NuGet push/restore | Packer regression, shell test proving dotnet is never called, Build Packages CI |
| #23: gate immediately before push | Independent check in shared publish script, used by auto and instant releases | Alternate packer regression and workflow policy test |
| #23: treat HTTP 413 as non-retryable | One push attempt; retain exit status, annotate 413/RequestEntityTooLarge, stop later channels | Stubbed push failures, exact call counts, no Conan/GitHub publication |
| #24: complete both issues in one PR | Implement and verify both together | PR diff and closing references |
| Release preparation | Patch changelog fragments; automatic version bump on merge | Existing changelog/version CI checks |

## Root causes and alternatives

At 29d8cf2 the detector recognized neither `.txt` in general nor Python
requirements manifests specifically. Both shared requirements paths returned
false for every gate. Matching all `.txt` files would waste builds on notes;
a narrow `requirements*.txt` basename rule preserves documentation,
experiment and unrelated-language exclusions. Shared requirements also need
to enable coverage and documentation gates, beyond the matrix's code gate.

[dorny/paths-filter](https://github.com/dorny/paths-filter) is an existing
GitHub Action with glob rules and named boolean outputs. Adopting it is
possible but would replace the established C++ layout handling, require
workflow changes and add an action dependency. Extending the existing Python
classifier is the smaller solution.

NuGet packaging and both push sites previously had no compressed-size gate.
[Microsoft's publishing guide](https://learn.microsoft.com/en-us/nuget/nuget-org/publish-a-package#package-size-limits)
documents an approximate 250 MB limit and HTTP 413. A default of 249,000,000
decimal bytes leaves headroom even if MB is interpreted as decimal. Different
feeds can override the budget; no local check can guarantee a remote policy
will remain unchanged, so server rejection still fails publication clearly.

A shell `stat -c %s` gate would work on Linux but differs on BSD/macOS and
cannot explain ZIP contributors by itself. Python's standard-library
[`zipfile`](https://docs.python.org/3/library/zipfile.html) provides compressed
and uncompressed entry sizes through ZIP metadata. Together with `Path.stat`
it needs no external library or decompression. Checking in the common packer
covers standalone use and `package_release.py`; checking both shell push
sites independently covers externally supplied packages.

The downstream [hive-mind PR #4051](https://github.com/link-assistant/hive-mind/pull/4051)
is a related example of splitting oversized platform payloads. This template
currently packages headers; automatically splitting its package would change
the distribution contract without a demonstrated need. Diagnostics instead
point maintainers at the largest entries and suggest removing unused assets
or splitting native platforms. Microsoft also recommends separating symbols
or using dependency packages in its publishing guide.

[`dotnet nuget push`](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-nuget-push)
provides `--skip-duplicate` for HTTP 409; it does not make HTTP 413 recoverable.
The script has no upload retry loop. It now forces English output for stable
413 classification, captures output in a temporary file, preserves failure
status and stops before publishing any later channel. A later manually
started or main-push-triggered release remains a separate invocation; it
must use corrected contents or budget rather than expecting a retry to fix
an identical payload. No release-completion behavior was removed.

PR #21's requirements-only run skipped the checks that would have detected
a mismatch between its upgraded audit pin and the executable workflow pin:
requirements-security.txt selected zizmor 1.31.1 but workflows.yml still ran
1.29.0. This PR includes the dependency updates and aligns both executable
zizmor pins. A rerun of an old GitHub Actions run uses its original commit,
so it cannot alone verify this fix; the current PR runs the same updated
tools with the corrected detector.

## Reproduction and validation

```bash
# Baseline: all detector outputs false for the two shared requirements.
python3 -c 'import sys; sys.path.insert(0, "scripts"); import detect_code_changes as d; print(d.classify(["scripts/requirements-ci.txt", "scripts/requirements-security.txt"]))'
# Expected after this PR: all outputs true.

# Runs selected new tests against 29d8cf2, then restores working files.
# Do not run concurrently with another test process.
python3 experiments/verify_issue_24_regressions.py

python3 -m pytest scripts/tests -q
bash -n scripts/check-nuget-package.sh scripts/publish-release.sh
```

The original scripts fail all 11 selected regression cases. The probes use
small ZIPs and mocked publishing commands, require no compiler or real
upload, and save output under `experiments/` (logs are ignored by git).
The size gate tests use byte-sized budgets to reproduce an oversized upload
without writing a 250 MB fixture. CI supplies real package restoration and
the C++ matrix instead of duplicating full builds locally.

GitHub refused `gh run rerun 42463434826 --failed` because the historical
run had no failing jobs. A full `gh run rerun 42463434826` was accepted.
It still uses PR #21's original commit and classifier, so the current PR
is the verification of those updated dependencies with the corrected gates.

## Findings exposed by running the upgraded tools

- Workflows run 43400020350 on f81e425: the preserved log
  `ci-logs/workflows-43400020350.log`, line 400, reports
  `Unknown version: 1.31.1`. The pinned zizmor action uses a frozen version
  table. Run the audited PyPI version directly with `pipx run`, retaining
  the regular persona, medium confidence floor, online token, configuration
  and GitHub annotations. This follows zizmor's
  [documented manual integration](https://docs.zizmor.sh/integrations/).
  The separate pedantic high-severity/high-confidence check is retained.
- CI/CD run 43400020323, lint job 131801296207: log
  `ci-logs/lint-131801296207.log`, lines 431 and 435, reports
  `misc-const-correctness` for both benchmark iteration values. clang-tidy
  23.1.4 catches these; both loop variables are now `const`. No lint rule
  is disabled. The existing CI lint command reproduces and guards the fix.

Local validation: 455 script tests passed using pytest 9.2.0. After switching
the zizmor integration, all 50 workflow policy tests pass, and zizmor 1.31.1
reports no findings in regular/medium-confidence and pedantic/high-confidence
high-severity offline checks. Full builds remain in CI.

The subsequent online zizmor run (43400739222) also exposed two stale
CodeQL `# v4` comments (log lines 376–377): the moving major tag no longer
matched the pinned commit. GitHub's annotated `v4.39.1` tag resolves to the
existing pinned SHA `9b3254085494b55a0f7c4c2b3d2d52cc712ce370`. Both comments
now name `v4.39.1`; the action code is unchanged. Online validation matters
because the ref-version-mismatch audit cannot run offline.
