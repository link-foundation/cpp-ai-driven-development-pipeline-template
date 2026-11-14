# Issue 33 / PR 34 work plan

Objective: implement and verify every requirement in issue 33 in this single PR.
Work only on `issue-33-2c3d53a97d9f`; preserve history and leave PR unmerged.

## Requirements and proposed solutions

| ID | Requirement | Solution / verification plan | Status |
| --- | --- | --- | --- |
| R1 | Read complete issue, comments, required sub-issues, and all PR comment types | Save issue and three PR discussion sources here; inspect all prose. No required sub-issues or images were referenced initially. Recheck before finishing. | Complete initially; final refresh pending |
| R2 | Investigate every default-branch failure after PR 32, without reverting updates | Preserve runs, SHAs, timestamps and full failure logs; identify root cause and regression coverage. Re-run main validation where possible without changing main. | Root cause: missing Conan token, predates PR 32; main-green criterion externally blocked |
| R3 | Update all Python direct and transitive packages, honest floors and consistent locks | Query PyPI for every constraint; use existing pinned uv universal resolver; regenerate all requirements and constraints; test and pip-audit. | Complete: all 60 current, regenerated, full tests and strict audit passed |
| R4 | Update all npm direct, transitive and CLI dependencies and Node | Query npm stable dist-tags and official Node distribution; inspect overrides and migration guides; regenerate lock, run scanner tests and audit project plus CLI tree. | Scanner complete: 76 current, 20 tests pass, audit clean; current CLI bundle advisory criterion externally blocked |
| R5 | Update every Actions reference, reusable/composite action and container digest | Compare all uses against upstream releases and immutable commits; verify actionlint image digest and workflow lint/security checks. | All refs and image digest current; CI verification pending |
| R6 | Update .NET SDK and any NuGet dependencies/frameworks | Query official release index; inspect repository for projects and package references; update global.json and every SDK install consistently; package validation in CI. | SDK current; updater added; packaging CI pending |
| R7 | Update pre-commit and any infrastructure dependencies | Query hook tags and Python hook resolution; regenerate hook pins if needed; inspect Terraform/Helm/submodules/base images and exercise hooks. | All hook pins current; full hooks running; no other IaC managers present |
| R8 | Update native/CMake dependencies, tools and toolchains throughout | Query native releases, CMake, vcpkg registry/tool and helper ports, Conan and hosted-image metadata; align baseline checkout and manifest; verify all supported consumers/builds in CI. | Baseline/tool advanced; native matrix pending; publication gaps explicit in DEPENDENCIES.md |
| R9 | Per-ecosystem table of every before/latest version from live registry; document every exception | Retain raw query responses, complete Python/npm tables, native/toolchain/action table and reasons for lag. Preserve historical evidence unchanged. | Complete: PYTHON-LOCK.md, NPM-LOCK.md, NPM-CLI.md and DEPENDENCIES.md |
| R10 | Read major migration guides, adopt upstream features, remove obsolete shims, fix deprecations | Compare fresh versions; review relevant changelogs/previous workaround reports; remove only superseded workarounds with focused tests. | Complete: rc-config-loader migration guide applied; native ESM/TS adopted, no local shim |
| R11 | Keep automatic updates covering every actual ecosystem and directory | Verify Dependabot supported managers; cover SDK global.json; avoid NuGet updates if no NuGet dependency manifest exists; validate configuration and health. | Complete: SDK manager added, all actual manifests covered; known vcpkg downgrade excluded |
| R12 | Full build/test/lint in every ecosystem, clean advisory reports and green CI | Sequential lightweight local checks plus current-commit CI matrix; inspect full logs for failures/deprecations; preserve exact evidence. Never call incomplete audits clean. | 509 script tests, 20 scanner tests and project audits pass; CI pending; native audit / CLI zero-advisory blocked |
| R13 | Search upstream issues and report bugs/features/general-purpose workarounds | Inspect prior reports and current upstream code; reproduce ongoing problems, update existing reports with affected versions/workaround/proposal; link from PR. | Complete: 20 prior reports refreshed, two new reproducible reports; see UPSTREAM.md |
| R14 | Research existing components and alternative solution plans online | Evaluate uv/pip-tools, npm-check-updates, Dependabot/Renovate, Conan audit and OSV against actual gaps; save primary-source citations. | Complete: primary sources, alternatives and choices in ANALYSIS.md |
| R15 | Repository-wide implementation, release trigger, meaningful regression checks | Search every active pin, align copies, retain features, add patch changelog fragment, run focused existing/regression tests before CI. | Implementation complete with patch fragment and before/after regression; final review pending |
| R16 | Finalize concrete PR with implementation/reproduction/tests/limits and positive closing keyword | Commit atomic steps, push only prepared branch, merge main if needed, review PR diff, update title/body via gh, verify clean tree/checks, mark PR ready. | Pending commits, push, current-commit CI, final review and PR ready |

## CI investigation protocol

1. List recent branch and main runs with timestamps, conclusions and head SHAs.
2. Compare to latest local and remote commits; distinguish stale runs.
3. Download complete non-passing logs into `ci-logs/`.
4. Read logs in chunks of at most 1500 lines and report exact errors/line numbers.
5. Fix causes, run focused regressions and verify new current-commit runs.

## Resource limits

Use sequential builds, `CMAKE_BUILD_PARALLEL_LEVEL=1`, bounded experiments,
small outputs and log files. Leave full cross-platform compilation to CI.
No agent delegation is authorized by repository instructions.
