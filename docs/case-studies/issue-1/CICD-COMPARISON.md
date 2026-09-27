# CI/CD comparison: link-foundation templates vs. linksplatform C++ workflows

This document compares the CI/CD workflow files in the seven existing
link-foundation `*-ai-driven-development-pipeline-template` repositories. It
then compares them with the C++ workflows that linksplatform uses today. The
goal is to derive requirements for the C++ template (issue #1).

All claims cite files in this case study's `data/` folder:

- `data/template-workflows/<template>/*.yml`: verbatim copies of every
  workflow file in each template.
- `data/template-trees/<template>.txt`: the full tracked-file list of each
  template (the output of `git ls-files`).
- `data/raw/template-workflow-structure.txt`: an extracted outline of each
  workflow (triggers, concurrency, permissions, jobs).
- `data/linksplatform-cpp-workflows/`: verbatim copies of linksplatform C++
  workflows, build files and packaging files. Each is prefixed with its source
  repository name.
- `data/linksplatform-repos.json`: a survey of all 88 linksplatform
  repositories.
- `data/raw/*`: other raw evidence (API outputs, registry probes, run logs).

The data was snapshotted on 2026-09-27. The templates were cloned from the
`main` branch of:

| Short name | Repository |
|---|---|
| js | link-foundation/js-ai-driven-development-pipeline-template |
| rust | link-foundation/rust-ai-driven-development-pipeline-template |
| python | link-foundation/python-ai-driven-development-pipeline-template |
| go | link-foundation/go-ai-driven-development-pipeline-template |
| java | link-foundation/java-ai-driven-development-pipeline-template |
| csharp | link-foundation/csharp-ai-driven-development-pipeline-template |
| php | link-foundation/php-ai-driven-development-pipeline-template |

---

## 1. Workflow files per template

| Template | Workflow files (line count) | Total |
|---|---|---|
| js | `release.yml` (1023), `example-app.yml` (379), `links.yml` (174), `workflows.yml` (169), `security.yml` (136) | 5 |
| rust | `release.yml` (1320), `desktop-release.yml` (215), `links.yml` (165), `workflows.yml` (123), `security.yml` (111) | 5 |
| python | `release.yml` (1008), `workflows.yml` (138), `links.yml` (132), `docs.yml` (130), `security.yml` (106) | 5 |
| csharp | `release.yml` (953), `links.yml` (126), `docs.yml` (119), `workflows.yml` (102), `security.yml` (53) | 5 |
| php | `release.yml` (509), `links.yml` (133), `workflows.yml` (131), `security.yml` (127), `docs.yml` (113) | 5 |
| go | `release.yml` (401), `workflows.yml` (45) | 2 |
| java | `release.yml` (552) | 1 |

Source: `data/template-workflows/<template>/`.

The five mature templates (js, rust, python, csharp, php) share a common
**five-file layout**:

1. `release.yml`: the main CI/CD pipeline (checks, tests, build, release).
2. `workflows.yml`: lints the workflows themselves (actionlint, zizmor).
3. `security.yml`: CodeQL, dependency review, and a language dependency
   audit.
4. `links.yml`: lychee link checking.
5. `docs.yml`: API docs build and GitHub Pages deploy. js and rust have no
   separate `docs.yml`. rust deploys docs from the `deploy-docs` job in
   `release.yml`. js deploys a demo app through `example-app.yml`.

go and java lag behind: they have no `security.yml`, `links.yml` or
`docs.yml`, and no `pipeline-status` gate.

**Conclusion for C++:** start from the five-file layout (`release.yml`,
`workflows.yml`, `security.yml`, `links.yml`, `docs.yml`). A C++ template
also needs Doxygen docs, so a dedicated `docs.yml` (like python, csharp and
php) is the closest match.

### 1.1 Linksplatform C++ workflow files

`data/linksplatform-repos.json` (`summary.cppWorkflowPatterns`) groups the
42 linksplatform repositories that have a `cpp/` folder by workflow pattern:

| Pattern | Repos | Example (copied verbatim) |
|---|---|---|
| `cpp.yml` (old style, Conan 1, scripts downloaded from linksplatform/Scripts) | 21 | `data/linksplatform-cpp-workflows/Documentation-cpp.yml`, `Disposables-cpp.yml` |
| `cpp-test.yml` + `deploy-cpp.yml` (calls reusable workflows in linksplatform/Workflows) | 17 | `Numbers-cpp-test.yml`, `Numbers-deploy-cpp.yml`, `Data.Doublets-*.yml` |
| `cpp-test.yml` + `deploy-cpp.yml` + `cpp-docs.yml` (newest) | 1 (Interfaces) | `Interfaces-cpp-test.yml`, `Interfaces-deploy-cpp.yml`, `Interfaces-cpp-docs.yml` |
| no C++ workflow | 3 | n/a |

The reusable workflows live in linksplatform/Workflows:

- `data/linksplatform-cpp-workflows/Workflows-cpp-test.yml`
- `Workflows-deploy-cpp.yml`
- `Workflows-cpp.yml`
- `Workflows-get-cpp-package-info.yml`
- `Workflows-get-cpp-conan-package-info.yml`
- `Workflows-publish-to-conan.yml`

---

## 2. Jobs per release workflow

The table lists jobs in file order. Source:
`data/template-workflows/<t>/release.yml`, summarised in
`data/raw/template-workflow-structure.txt`.

| Template | Jobs in `release.yml` |
|---|---|
| js | detect-changes, test-compilation, check-file-line-limits, version-check, changeset-check, lint, test, docker-build, validate-docs, release-preflight, release, instant-release, docker-publish-config, docker-publish-build, docker-publish, changeset-pr, pipeline-status |
| rust | detect-changes, validate-docs, release-preflight, changelog, version-check, secrets-scan, fresh-merge, docker-build, cargo-lock, lint, test, script-tests, coverage, build, auto-release, manual-release, docker-publish, docker-merge-manifest, changelog-pr, deploy-docs, pipeline-status |
| python | detect-changes, lint, validate-docs, release-preflight, test, build, changelog, docker-build, auto-release, manual-release, docker-publish-config, docker-publish-build, docker-publish, pipeline-status |
| csharp | detect-changes, changeset-check, lint, test, build, release-preflight, release, instant-release, changeset-pr, pipeline-status |
| php | detect-changes, lint, release-preflight, test, changeset, build, auto-release, manual-release, pipeline-status |
| go | detect-changes, changeset-check, lint, test, build, auto-release, instant-release, changeset-release |
| java | detect-changes, lint, test, build, changeset-check, auto-release, manual-release-changeset, manual-release-instant, changeset-pr |

These jobs appear in every template, so the C++ template needs them too:

- `detect-changes`
- `lint`
- `test`
- `build`
- an automatic release job
- a manual-release path (workflow_dispatch)

rust has the most complete job set (21 jobs). It is also the only template
that runs `secrets-scan` and `fresh-merge` as separate jobs, and it has a
dedicated `coverage` job.

### 2.1 Jobs in the other workflows

| Template | `workflows.yml` | `security.yml` | `links.yml` | `docs.yml` |
|---|---|---|---|---|
| js | actionlint, status-gate-coverage, zizmor, pipeline-status | codeql, dependency-review, npm-audit, pipeline-status | link-checker, pipeline-status | n/a (`example-app.yml`) |
| rust | actionlint, zizmor, pipeline-status | cargo-audit, codeql, dependency-review, pipeline-status | link-checker, pipeline-status | n/a (`deploy-docs` in release) |
| python | actionlint, zizmor, pipeline-status | dependency-audit, codeql, dependency-review, pipeline-status | link-checker, pipeline-status | build, deploy, pipeline-status |
| csharp | actionlint, zizmor | codeql, dependency-review | link-checker | build, deploy |
| php | actionlint, zizmor, pipeline-status | dependency-audit, codeql, dependency-review, pipeline-status | link-checker, pipeline-status | build, deploy, pipeline-status |
| go | one `workflows` job ("Lint and test workflows") | n/a | n/a | n/a |
| java | n/a (actionlint runs inside `release.yml`) | n/a | n/a | n/a |

### 2.2 Jobs in linksplatform C++ workflows

| File | Jobs |
|---|---|
| `Workflows-cpp-test.yml` (reusable) | `test` |
| `Workflows-deploy-cpp.yml` (reusable) | `test`, `get_package_info`, `pushToNuget`, `get_conan_package_info`, `publishRelease`; the conan-center-index PR job is commented out (lines 114+) |
| `Interfaces-cpp-docs.yml` | a single Doxygen build + docs check + artifact upload job (no Pages deploy) |
| `Interfaces-codeql.yml` | `analyze`, with a matrix over `c-cpp` and `csharp` |
| `Documentation-cpp.yml` (old style) | `test`, `pushToNuget`, plus a release job driven by scripts from linksplatform/Scripts |

---

## 3. Triggers

| Template | `release.yml` triggers | workflow_dispatch inputs |
|---|---|---|
| js | push (main), pull_request, workflow_dispatch | `release_mode` (instant, changeset-pr), `bump_type`, `description` |
| rust | push (main), pull_request, workflow_dispatch | `release_mode` (instant, changelog-pr), `bump_type`, `description` |
| python | push (main), pull_request, workflow_dispatch | `bump_type`, `description` (no release_mode) |
| csharp | push (main), pull_request, workflow_dispatch | `release_mode` (instant, changeset-pr), `bump_type`, `description` |
| php | push (main), pull_request, workflow_dispatch | `bump_type`, `description` (no release_mode) |
| go | push (main), pull_request, workflow_dispatch | `release_mode` (instant, changeset), `bump_type`, `description` |
| java | push (main), pull_request, workflow_dispatch | `release_mode` (changeset, instant, changeset-pr), `bump_type`, `description` |

In the other workflow files:

- `security.yml` adds a weekly `schedule`.
- `links.yml`, `docs.yml` and `workflows.yml` run on push, on pull_request,
  and (usually) on workflow_dispatch.

Source: `data/raw/template-workflow-structure.txt`.

Linksplatform triggers (`data/linksplatform-cpp-workflows/Interfaces-cpp-test.yml`
lines 3-21, `Interfaces-deploy-cpp.yml`):

- `cpp-test.yml` runs on:
  - `push` to `main`, filtered to paths `cpp/**.h`, `cpp/**.cpp`,
    `cpp/CMakeLists.txt` and `cpp/conanfile.txt`;
  - `pull_request` with **`types: [edited]` only**.

  **This is a bug.** A pull request that opens with or pushes C++ changes is
  never tested. Only editing the PR title or body triggers the tests. The
  template's default `pull_request` types (opened, synchronize, reopened) fix
  this.
- `deploy-cpp.yml` runs on `push` to `main` that touches `cpp/**/*.nuspec`,
  and on `workflow_dispatch`. A release therefore happens when someone edits
  the version in the nuspec, which is the "manual version bump" model. It
  has no changelog fragments and no bump type.
- `codeql.yml` runs on push, on pull_request and on a weekly cron.

**Conclusion:** the C++ template must use the standard template trigger
set: push to main, pull_request (default types) and workflow_dispatch with
`release_mode`, `bump_type` and `description`. Path filters must be
replaced by a `detect-changes` job, because a skipped required workflow
blocks merging, whereas a job that runs and is skipped does not.

---

## 4. Concurrency style

| Template | Workflow-level concurrency | Per-job concurrency blocks (all files) | Style |
|---|---|---|---|
| js | none | 32 | `check-${{ github.workflow }}-${{ github.ref }}-<job>` with `cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}`; release jobs share `main-writer-${{ github.repository }}-main` with `cancel-in-progress: false` |
| rust | `desktop-release.yml` only | 23 | per-job `${{ github.workflow }}-${{ github.ref }}-<job>` |
| python | `docs.yml` only | 14 | per-job, same pattern as rust |
| csharp | `release.yml` and `docs.yml` | 4 | workflow-level `${{ github.workflow }}-${{ github.ref }}`, cancel unless main |
| php | `security.yml`, `docs.yml`, `links.yml` | 2 | mostly workflow-level |
| go | none | 9 | per-job |
| java | none | 9 | per-job |

Source: `grep '^concurrency:'` and `grep '^    concurrency:'` over
`data/template-workflows/<t>/*.yml`.

hive-mind principle 10 ("Concurrency Control") recommends per-job groups:

- PR runs of the same ref cancel each other.
- `main` runs are never cancelled.
- Every job that writes to `main` serialises on one group.

js is the reference implementation of this pattern.

Linksplatform C++ workflows have **no concurrency control at all**
(`Workflows-cpp-test.yml`, `Workflows-deploy-cpp.yml`). Two nuspec edits
merged in quick succession could therefore race to publish.

---

## 5. Permissions and hardening

| Template | Top-level `permissions: contents: read` | `persist-credentials: false` count | `timeout-minutes` count | Actions pinned by SHA | `run-with-budget-warning.sh` usages |
|---|---|---|---|---|---|
| js | yes | 34 | 45 | 4 | 8 |
| rust | yes | 32 | 40 | 19 | 6 |
| python | yes | 24 | 34 | 3 | 4 |
| csharp | yes | 16 | 23 | 0 | 22 |
| php | yes | 20 | 37 | 0 | 17 |
| go | yes | 1 | 1 | 1 | 0 |
| java | **no** | 0 | 0 | 0 | 0 |

Source: grep counts over `data/template-workflows/<t>/*.yml`.

- Write permissions (`contents: write`, `pull-requests: write`,
  `id-token: write`, `pages: write`, `security-events: write`) are granted
  per job, only where needed.
- zizmor (section 13) enforces this.

Runner labels:

- js and csharp pin `ubuntu-24.04`, following hive-mind's "Pin hosted runner
  operating systems" note.
- rust, python and php still mostly use `ubuntu-latest`.

Linksplatform C++:

- No `permissions:` block anywhere.
- `actions/checkout@v1` in `Workflows-cpp-test.yml` line 17.
- `ubuntu-latest` everywhere.
- No `timeout-minutes`.
- The newer `Interfaces-cpp-docs.yml` and `Interfaces-codeql.yml` use
  `ubuntu-24.04` and `actions/checkout@v7`.

---

## 6. Pipeline-status gate

| Template | Where `pipeline-status` exists | Condition |
|---|---|---|
| js | all 5 workflows | `if: ${{ !cancelled() }}` |
| rust | all 4 non-desktop workflows | `if: ${{ !cancelled() }}` |
| python | all 5 workflows | `if: always()` |
| php | all 5 workflows | `if: always()` |
| csharp | `release.yml` only | `if: always()` |
| go | none | n/a |
| java | none | n/a |

How the gate works:

- It `needs:` every other job and fails if any of them failed or was
  cancelled unexpectedly (`scripts/check-pipeline-status.sh` in python).
- Branch protection then needs to require **one** check per workflow.
- js adds a `status-gate-coverage` job in `workflows.yml`. It verifies that
  every job is listed in the gate's `needs:`.

Linksplatform: none. Branch protection would have to list every job by
name.

**Conclusion:** the C++ template needs a `pipeline-status` job in every
workflow, plus the js `status-gate-coverage` check.

---

## 7. Changelog mechanism and source of the bump type

| Template | Fragment folder | Fragment format | Bump-type source |
|---|---|---|---|
| js | `.changeset/` | Changesets frontmatter `'<pkg>': patch\|minor\|major` | fragment frontmatter; workflow_dispatch `bump_type` for instant releases |
| go | `.changeset/` | Changesets-style frontmatter | fragment frontmatter / `bump_type` |
| java | `.changeset/` | Changesets-style frontmatter | fragment frontmatter / `bump_type` |
| csharp | `.changeset/` | Changesets-style frontmatter `'MyPackage': patch` | fragment frontmatter / `bump_type` |
| rust | `changelog.d/` | `---\nbump: minor\n---` + Keep-a-Changelog sections (`### Added`, `### Fixed`) | fragment frontmatter `bump:` (highest wins) / `bump_type` |
| php | `changelog.d/` | `---\nbump: minor\n---` + Keep-a-Changelog sections | fragment frontmatter `bump:` / `bump_type` |
| python | `changelog.d/` | scriv fragments (`### Added` etc.), no frontmatter | a version change in `pyproject.toml` triggers auto-release; workflow_dispatch `bump_type` for manual releases |

Sources:

- the fragment folders listed in `data/template-trees/<t>.txt`;
- sample fragments from each template;
- the python fragment template `changelog.d/fragment_template.md.j2`.

In the workflows:

- `changeset-check` (js, go, java, csharp) or `changelog` (rust, python)
  fails a PR that has code changes but no fragment.
- In php, the `changeset` job does the same.

Linksplatform C++ has no changelog mechanism. The release notes are the
`<releaseNotes>` element of the nuspec. `Workflows-deploy-cpp.yml` greps it
out (the `get_package_info` job) and pastes it into the GitHub release body.

Numbers already migrated its **Rust** part to `changelog.d/`
(`data/linksplatform-cpp-workflows/Numbers-rust.yml`), so linksplatform is
used to the fragment model.

**Conclusion for C++:** there is no native C++ changeset tool, so use the
language-neutral `changelog.d/` + `bump:` frontmatter format from rust and
php. The scripts can be:

- shell,
- Python (available on every runner),
- or C++ scripts compiled with the project.

Where the version lives:

- The single source of truth should be `project(... VERSION x.y.z)` in
  `CMakeLists.txt`.
- For linksplatform compatibility, a mirror in the nuspec, conanfile.py and
  vcpkg.json must be updated in the same bump.

---

## 8. Version-modification check, release-preflight, secrets scan, file-size limits

| Feature | js | rust | python | go | java | csharp | php |
|---|---|---|---|---|---|---|---|
| Version-modification check (PR must not hand-edit the version) | `version-check` job | `version-check` job | n/a | n/a | n/a | n/a | script in `lint` |
| `release-preflight` (prove the publish credentials work before building) | yes | yes | yes | no | no | yes | yes |
| Secrets scan (secretlint) | in `lint` | separate `secrets-scan` job | in `lint` | no | no | no | no |
| File-size limit | `check-file-line-limits` (1500 lines) | `check-file-size` (1000 lines, `MAX_LINES: usize = 1000`) | `scripts/check_file_size.py` (1000 lines code, 2500 docs) | `check-file-size` (1000) | `check-file-size` (1000) | `check-file-size` (1000) | `check-file-size` (1000) |

Sources:

- `data/template-workflows/<t>/release.yml`.
- `scripts/preflight-credentials.sh` (listed in the python, js and rust
  trees).
- The secretlint invocation in the rust `secrets-scan` job and the js/python
  `lint` jobs:
  `npx --yes -p secretlint -p @secretlint/secretlint-rule-preset-recommend secretlint "**/*"`.

The preflight job (hive-mind principle 16, "Prove You Can Publish Before You
Build") exists because a release can fail late on an expired token. That is
exactly the linksplatform failure mode in section 15.

Linksplatform C++:

- No version check.
- No preflight: the NuGet push is the last step, after the GitHub release
  already exists.
- No secrets scan.
- No file-size limit.

---

## 9. Fresh-merge simulation

Present in **js, rust and python only**:

- rust: the `fresh-merge` job.
- js: invoked 3 times.
- python: invoked once.

All of them call `scripts/simulate-fresh-merge.sh`.

What it does:

- Merges the PR head into the *current* base branch tip.
- Re-runs the checks on the merged result.
- This is hive-mind principle 7, "Validate the Actual Merge Result".

It is missing from csharp, php, go, java and all linksplatform workflows.

**Conclusion:** include it in the C++ template. It matters most for C++,
where header changes on `main` can break a PR that was green on its own
base.

---

## 10. Docs build and deploy

| Template | Tool | Workflow/job | Pages deploy | Opt-in gate |
|---|---|---|---|---|
| python | Sphinx (`sphinx-build`) | `docs.yml` build/deploy | `actions/deploy-pages@v5` | `vars.DEPLOY_GITHUB_PAGES` |
| csharp | DocFX (`docfx.json`) | `docs.yml` build/deploy | `actions/deploy-pages@v5` | `vars.DEPLOY_GITHUB_PAGES` |
| php | phpDocumentor | `docs.yml` build/deploy | `actions/deploy-pages@v4` (older `upload-pages-artifact@v3`) | none |
| rust | `cargo doc` | `release.yml` `deploy-docs` job | `actions/deploy-pages@v5` | runs on release |
| js | example app build | `example-app.yml` | `actions/deploy-pages@v5` | n/a |
| go, java | none | n/a | n/a | n/a |

Every template also has a `validate-docs` job (js, rust, python) or a
`scripts/check-required-docs.sh` script (python). They check that the
required docs exist, such as README, CONTRIBUTING and the changelog. This is
hive-mind principle 12.

Linksplatform C++ docs (`data/linksplatform-cpp-workflows/Interfaces-cpp-docs.yml`,
`Interfaces-cpp-Doxyfile`, `Interfaces-.github-scripts-check-cpp-docs.py`):

- The build steps, in order:
  1. Install Doxygen via apt on `ubuntu-24.04`.
  2. Run `check-cpp-docs.py`, a custom checker that every public
     declaration has a doc comment, plus its own unit test.
  3. Run `doxygen cpp/Doxyfile`.
  4. Verify that `html/index.html` and the XML output exist.
  5. Upload the result as a workflow artifact.
- Doxyfile settings: `WARN_IF_UNDOCUMENTED = YES` and
  `WARN_AS_ERROR = FAIL_ON_WARNINGS`, so undocumented API fails CI.
  `EXCLUDE_SYMBOLS = Platform::Interfaces::Internal`. `OUTPUT_DIRECTORY` is
  `cpp/docs`. Both HTML and XML are generated.
- **No GitHub Pages deploy.** The nuspec `projectUrl` still points to
  `https://linksplatform.github.io/Interfaces`, which the C# DocFX pipeline
  serves.

**Conclusion for C++:**

- Add a `docs.yml` that runs Doxygen with `WARN_AS_ERROR=FAIL_ON_WARNINGS`,
  uploads with `upload-pages-artifact@v5` and deploys with
  `deploy-pages@v5`.
- Gate the deploy behind `vars.DEPLOY_GITHUB_PAGES`, like python and
  csharp.
- In multi-language mode, publish under a `cpp/` subpath so the C++ docs do
  not overwrite the C# DocFX site on the same Pages domain.

---

## 11. Link checking

Templates with a `links.yml`: js, rust, python, csharp, php. All of them:

- use lychee;
- recheck broken links against the Web Archive
  (`scripts/check_web_archive.py` and `scripts/recheck_broken_links.py` in
  python);
- run a `pipeline-status` job (except csharp).

go and java have no link checking. Neither do the linksplatform C++
workflows.

**Conclusion:** copy `links.yml`. It is language-neutral.

---

## 12. Security scanning

| Template | CodeQL languages (matrix) | Dependency audit | dependency-review-action |
|---|---|---|---|
| js | `javascript-typescript`, `actions` | `npm-audit` job | yes |
| rust | `rust`, `actions` | `cargo-audit` job | yes |
| python | `python`, `actions` | `dependency-audit` (`scripts/audit_dependencies.py`, pip-audit) | yes |
| csharp | `csharp`, `actions` | none (no audit job) | yes |
| php | `actions` only | `dependency-audit` (composer audit) | yes |
| go | none | none | no |
| java | none | none | no |

Source: `data/template-workflows/<t>/security.yml`.

Linksplatform: `data/linksplatform-cpp-workflows/Interfaces-codeql.yml` runs:

- CodeQL `c-cpp` and `csharp`, with `build-mode: none`;
- queries `security-extended,security-and-quality`;
- `github/codeql-action` v4, on a weekly cron.

`build-mode: none` works for header-only C++ and avoids having to reproduce
the Conan build inside CodeQL.

**Conclusion for C++:**

- CodeQL matrix `[c-cpp, actions]`, with `build-mode: none` by default.
  Allow `manual` or `autobuild` for compiled libraries.
- Keep `dependency-review-action`.
- A C++ dependency audit has no standard tool equivalent to cargo-audit. The
  options (see ONLINE-RESEARCH.md for details) are:
  - OSV-Scanner over `conan.lock` / `vcpkg.json`;
  - `conan audit` (available in recent Conan 2 releases);
  - skip the audit when there are no third-party dependencies.

---

## 13. Workflow linting (actionlint, zizmor)

| Template | actionlint | zizmor | Where |
|---|---|---|---|
| js | yes | yes | `workflows.yml` (+ `status-gate-coverage`) |
| rust | yes | yes | `workflows.yml` |
| python | yes | yes | `workflows.yml` |
| csharp | yes | yes | `workflows.yml` |
| php | yes | yes | `workflows.yml` (actionlint Docker image pinned by digest, 1.7.12, per its `changelog.d`) |
| go | yes | no | `workflows.yml`, single job |
| java | yes | no | inside `release.yml` |

This is hive-mind principle 14 ("Lint the Workflows Themselves").

Linksplatform: none. Running actionlint on the linksplatform files would
flag several problems:

- `actions/checkout@v1`;
- the unused `recipe_folder` input in `Workflows-deploy-cpp.yml` line 6;
- `ncipollo/release-action@v1.11.2` running on Node 16.

zizmor would additionally flag the missing `permissions:` blocks and
`persist-credentials`.

---

## 14. Multi-language support and tag naming

Several templates detect whether the code lives at the repository root
(single-language mode) or in a language subfolder (multi-language mode). The
tag and release name change accordingly:

| Template | Detection | Single-language tag / title | Multi-language tag / title | Source |
|---|---|---|---|---|
| rust | Cargo root ≠ `.` (e.g. `rust/`) | `v<ver>` / `<name> <ver>` | `rust_v<ver>` / `[Rust] <ver>` | `scripts/release-naming.rs` (`RUST_MULTI_LANGUAGE_TAG_PREFIX = "rust_v"`) |
| python | `python/pyproject.toml` exists | `v<ver>` / `<dist> <ver>` | `py_v<ver>` / `[Python] <ver>` | `scripts/release_naming.py` lines 13, 30-38, 56-77 |
| js | `js/package.json` | `v<ver>` | `js_v<ver>` | `scripts/release-naming.mjs` line 14 |
| csharp | `csharp/` subdirectory | `v<ver>` | `cs_v<ver>` | `scripts/release-naming.mjs` lines 129, 198 |
| go, java, php | none | `v<ver>` | n/a | n/a |

Linksplatform tag conventions (`data/raw/linksplatform-release-tags-sample.txt`,
`data/raw/interfaces-releases.txt`):

| Language | Tag | Title |
|---|---|---|
| C++ | `cpp_<ver>` (no `v`) | `[C++] <ver>` |
| C# | `csharp_<ver>` | `[C#] <ver>` |
| Older combined releases | `<csver>_<cppver>`, e.g. `0.5.2_0.2.0` | `[C#] 0.5.2, [C++] 0.2.0` |
| Numbers Rust | plain `v0.8.0` | n/a |

The Numbers Rust tag is plain `v0.8.0` even though Numbers is a
multi-language repository, which is an inconsistency.

The `cpp_<ver>` tag is **load-bearing**:

- The linksplatform Conan recipes download
  `https://github.com/linksplatform/<Repo>/releases/download/cpp_<ver>/platform.<repo>_<ver>.zip`
  (`data/linksplatform-cpp-workflows/conan-center-index-platform.interfaces-conandata.yml`).
- The recipes already merged into ConanCenter use the same URLs
  (`data/raw/conancenter-upstream-platform-recipes.txt`).

Layout facts (`data/linksplatform-repos.json`):

- 42 of 88 linksplatform repos keep C++ in `cpp/`.
- 31 of those also have `csharp/`, and 9 also have `rust/`.
- Every C++ project uses a `cpp/Platform.<Repo>/` sub-folder for headers and
  `cpp/Platform.<Repo>.Tests/` for tests.

**Conclusion for C++:**

- Single-language mode: the project is at the root (`CMakeLists.txt` at
  root). The tag is `v<ver>` and the title `<name> <ver>`.
- Multi-language mode: the project is in `cpp/`. The template convention
  would be `cpp_v<ver>` / `[C++] <ver>`, but linksplatform needs
  `cpp_<ver>`. Make the prefix configurable, for example with a repository
  variable `CPP_TAG_PREFIX` or a config file, and default it to `cpp_v`
  (the template convention).
- The release notes and the tag parser must accept `v`, `cpp_v`, `cpp-v` and
  `cpp_` prefixes, the same way `normalize_version` in python strips
  `v`/`py_v`/`py-v`/`js_v`/`rust_v`.

---

## 15. Package publishing targets

| Template | Registry targets | Mechanism |
|---|---|---|
| js | npm, Docker Hub | `npm publish` with provenance, docker buildx multi-arch |
| rust | crates.io, Docker Hub, GitHub release binaries (`desktop-release.yml`) | `rust-script scripts/publish-crate.rs` (`publish-crate` step), buildx, `actions/attest@v4` in `desktop-release.yml` |
| python | PyPI, Docker Hub | `pypa/gh-action-pypi-publish` (trusted publishing), buildx |
| csharp | NuGet | `dotnet nuget push` |
| php | Packagist | tag + `scripts/wait-for-packagist.php` waits for Packagist to index the version |
| go | GitHub release (Go modules resolve from the tag) | `Create GitHub Release` steps in auto/instant/changeset release jobs |
| java | GitHub release artifacts (JAR) | `mvn package` + `Upload release artifacts` + `Verify published release artifacts` (no Maven Central deploy) |

Linksplatform C++ publishes to **three** targets today:

1. **NuGet native "TemplateLibrary" packages.** The package is
   `Platform.<Repo>.TemplateLibrary`, published by
   `data/linksplatform-cpp-workflows/Workflows-deploy-cpp.yml` (`pushToNuget`
   job, lines 30-80). Details:
   - Headers are packed into `lib\native\include\` and an MSBuild
     `build\native\Platform.<Repo>.TemplateLibrary.targets` is added.
     `data/linksplatform-cpp-workflows/linksplatform-Files-TemplateLibrary.targets`
     adds the include directory for MSVC consumers.
   - `<dependencies><group targetFramework="native">` is used
     (`Interfaces-cpp-Platform.Interfaces.TemplateLibrary.nuspec`).
   - 16 such packages are live, e.g. Delegates 0.3.7 (35.7k downloads) and
     Interfaces 0.3.41 (34.3k); see
     `data/raw/nuget-templatelibrary-packages.txt`.
2. **GitHub release zip.** The archive is `<conanname>_<ver>.zip` with
   `<conanname>` = `platform.<lowercased repo>`, under tag `cpp_<ver>`,
   title `[C++] <ver>`, and a body made of the NuGet URL plus the release
   notes (`publishRelease` job, lines 86-106). The Conan recipes consume
   this zip.
3. **Conan.**
   - 16 `platform.*` recipes live in the linksplatform fork of
     conan-center-index; the fork was last pushed on 2023-09-25
     (`data/raw/linksplatform-conan-recipes.txt`).
   - ConanCenter upstream has these recipes:
     - `platform.converters`
     - `platform.delegates`
     - `platform.equality`
     - `platform.exceptions`
     - `platform.hashing`
     - `platform.interfaces` (up to 0.3.41)

     Source: `data/raw/conancenter-upstream-platform-recipes.txt`.
   - The recipe style
     (`conan-center-index-platform.interfaces-conanfile.py`):
     - `basic_layout`, `package_id(): self.info.clear()` (header-only);
     - `check_min_cppstd(self, 20)`;
     - minimum compilers gcc 11, clang 13, msvc 193, and apple-clang
       rejected;
     - CMake names `Platform.Interfaces` /
       `Platform.Interfaces::Platform.Interfaces`.
   - The automated conan-center-index PR is **commented out** in
     `Workflows-deploy-cpp.yml` (lines 114+). A separate
     `Workflows-publish-to-conan.yml` uses `Minimonium/conan-request-action@master`.
   - As a result, ConanCenter is stuck at old versions. Interfaces is at
     0.3.41 there while the repo is at 0.4.1.

**vcpkg:** there are no linksplatform ports in the vcpkg registry
(`data/raw/vcpkg-linksplatform-presence.txt`). The only grep hit,
`platform-folders`, is an unrelated project.

**CMake install/export:** the linksplatform CMakeLists
(`Interfaces-cpp-CMakeLists.txt`, `Numbers-cpp-CMakeLists.txt`,
`Data.Doublets-cpp-CMakeLists.txt`) do the following:

- declare `add_library(${PROJECT_NAME}.Library INTERFACE)`;
- have **no `install()` / `export()` / `*Config.cmake`**;
- so `find_package()` works only via the Conan-generated CMakeDeps files.

Data.Doublets consumes its siblings via
`find_package(Platform.Interfaces)` plus Conan
(`Data.Doublets-cpp-conanfile.txt`). Locally it uses
`Data.Doublets-cpp-install-local-conan-dependencies.sh`, which clones the
conan-center-index fork and runs `conan create`.

**Conclusion for C++:** the template should publish or support all of the
following. Each target should be optional and switched on by
secrets/variables, following the preflight pattern.

1. The **repository itself as a distributable**: CMake
   `install(TARGETS/EXPORT)`, a `<Name>Config.cmake` +
   `ConfigVersion.cmake` package config, and `add_subdirectory` /
   `FetchContent` / CPM.cmake / git-submodule consumption.
2. A **GitHub release** with a source/header archive and a checksum. The
   archive name and tag prefix must be configurable, so that linksplatform
   keeps `cpp_<ver>` and `platform.<repo>_<ver>.zip`.
3. **Conan 2**:
   - a `conanfile.py` in the repo, with `conan create` in CI as a test;
   - optionally, upload to a Conan remote;
   - optionally, a PR to conan-center-index (or to the linksplatform fork).
4. **vcpkg**:
   - a port (`vcpkg.json` + `portfile.cmake`) tested in CI, using an overlay
     port;
   - optionally, a custom registry, or a PR to microsoft/vcpkg.
5. **NuGet native packages** (linksplatform-specific, opt-in): a
   `.nuspec` with `lib/native/include` and a `build/native/*.targets` file.
   Pack them with `dotnet pack`/NuGet from the preinstalled .NET SDK, or
   with `nuget/setup-nuget`, **never `apt-get install nuget`** (see the next
   subsection).
6. Optionally, xrepo/xmake, CPM or Homebrew. These are covered in
   ONLINE-RESEARCH.md.

### 15.1 Linksplatform C++ deploy is broken right now

Evidence: `data/raw/interfaces-deploy-cpp-failed-run-36213155523.txt` and
`data/raw/interfaces-recent-runs.json`.

- Interfaces `deploy-cpp` failed three times: on 2026-09-21, and twice on
  2026-09-26.
- The failing line is
  `E: Package 'nuget' has no installation candidate`, from the
  `sudo apt-get install nuget` step (`Workflows-deploy-cpp.yml` line 34) on
  the `ubuntu-24.04` image behind `ubuntu-latest`.
- Because `publishRelease` does not depend on `pushToNuget`, the GitHub
  releases `cpp_0.4.0` and `cpp_0.4.1` exist, but NuGet
  `Platform.Interfaces.TemplateLibrary` stops at 0.3.41
  (`data/raw/nuget-templatelibrary-packages.txt`). A release is marked done
  even though one of its registries was never updated.
- The template's `release-preflight` and job ordering would have caught
  this before tagging.
- `Interfaces/MIGRATION_SUMMARY.md` (mentioned in `data/raw/cpp-repo-probe.txt`)
  already plans the switch from `nuget.exe` to the dotnet CLI.

### 15.2 Other bugs in the current linksplatform C++ workflows

1. **Tests are compiled but never run.** `Workflows-cpp-test.yml` lines
   38-41 run `conan install`, `cmake` and `cmake --build`, with no `ctest`
   and no test binary execution.
2. **`pull_request: types: [edited]`** means PR pushes are never tested
   (`Interfaces-cpp-test.yml` lines 13-14).
3. **Profile patching.** `conan profile detect` is followed by
   `sed -i '5d' ~/.conan2/profiles/default` (`Workflows-cpp-test.yml`
   line 27). This deletes a line by number, presumably the `compiler.cppstd`
   line, and breaks silently when Conan changes the profile layout.
4. **Old-style `cpp.yml` in 21 repos is broken on Conan 2.** It uses Conan 1
   commands such as `conan profile new ... --detect` and
   `conan profile update` (`Documentation-cpp.yml` lines 35-40), while
   `pip install conan` now installs Conan 2.
5. **`recipe_folder` input is unused.** Numbers and Data.Doublets pass
   `"platform.delegates"`, a copy-paste error (`Numbers-deploy-cpp.yml`,
   `Data.Doublets-deploy-cpp.yml`).
6. **Single OS/compiler.** Only ubuntu + GCC (`egor-tensin/setup-gcc@v1`)
   or clang 13 is tested. The Conan recipe claims MSVC 193 support, but
   nothing tests it.
7. **Hard-coded `-march=haswell` / `armv7` / `armv8-a`** in
   `Interfaces-cpp-CMakeLists.txt`. The flag is applied whenever the host
   is x86_64, which makes the built tests non-portable. `LINKS_PLATFORM_TESTS`
   is also forced to TRUE.
8. **Scripts downloaded at run time** from
   `https://raw.githubusercontent.com/linksplatform/Scripts/main/...`
   (`Documentation-cpp.yml` line 13, then `wget` at lines 68-73). They are
   unpinned and not reviewed in the PR.
9. **The workflows do not use submodules consistently.** Interfaces symlinks
   `.clang-format` into the `Settings` submodule, but the CI never checks
   formatting.

---

## 16. Test matrices

| Template | Test OS matrix |
|---|---|
| js | ubuntu-24.04, macos-latest, windows-latest |
| rust | ubuntu-latest, macos-latest, windows-latest |
| python | ubuntu-latest only, Python 3.13 |
| csharp | ubuntu-24.04, macos-latest, windows-latest |
| php | ubuntu-latest, PHP 8.1 / 8.2 / 8.3 / 8.4 |
| go | ubuntu-latest, macos-latest, windows-latest |
| java | ubuntu-latest, macos-latest, windows-latest |

Source: the `test` job in each `release.yml`.

Coverage upload (codecov) exists in rust, python, go, java and csharp.

**Conclusion for C++:** the test matrix should be OS × compiler:

- Linux GCC (≥ 11) and Clang (≥ 13, per the linksplatform Conan recipe's
  minimums), macOS AppleClang, and Windows MSVC.
- Use `ctest --output-on-failure`.
- Sanitizers (ASan/UBSan) in a Linux job.
- Coverage via gcov/llvm-cov.

---

## 17. Formatting and static analysis (hive-mind principles 3-4)

| Template | Formatter check | Linter |
|---|---|---|
| js | Prettier | ESLint |
| rust | `cargo fmt --check` | `cargo clippy -D warnings` |
| python | ruff format | ruff / mypy |
| csharp | `dotnet format` | .NET build analyzers |
| php | PHP-CS-Fixer | PHPStan |
| go | gofmt | go vet |
| java | `mvn spotless:check` | `mvn spotbugs:check` |

Linksplatform C++ has a shared style in
`data/linksplatform-cpp-workflows/Settings-.clang-format`:

- `BasedOnStyle: Google`
- `ColumnLimit: 999999999`
- `NamespaceIndentation: All`
- `PointerAlignment: Left`
- `SortIncludes: false`

No CI job runs clang-format or clang-tidy.

**Conclusion:** the C++ `lint` job should run `clang-format --dry-run
--Werror` and `clang-tidy` (using `compile_commands.json`), and optionally
cppcheck. The template ships a `.clang-format`. A linksplatform repo can
replace it with the Settings style.

---

## 18. Mapping to the 16 hive-mind principles

Source: `data/raw/hive-mind-CI-CD-BEST-PRACTICES.md.txt` (copy of link-assistant/hive-mind `docs/CI-CD-BEST-PRACTICES.md`), section "Key CI/CD
Principles".

| # | Principle | Best template example | Linksplatform C++ today | C++ template requirement |
|---|---|---|---|---|
| 1 | Run checks only on relevant file changes | `detect-changes` job (all) | `paths:` filters (skip ⇒ blocks required checks) | `detect-changes` with a C++ file set (`*.h,*.hpp,*.cpp,*.cc,*.ipp,CMakeLists.txt,*.cmake,conanfile.*,vcpkg.json`) |
| 2 | File size limits | rust/csharp/php `check-file-size` (1000), js (1500) | none | 1000 lines for code, per the templates |
| 3 | Automated code formatting | `cargo fmt --check` | none | `clang-format --dry-run --Werror` |
| 4 | Static analysis & linting | clippy / ruff / PHPStan | none | clang-tidy (+ cppcheck), `-Wall -Wextra -Werror` in CI |
| 5 | Fast-fail job ordering | rust (`detect-changes → lint → test → build`) | none | same ordering |
| 6 | Changeset-based versioning | rust/php `changelog.d` + `bump:` | nuspec version edit | `changelog.d` + `bump:` |
| 7 | Validate the actual merge result | rust `fresh-merge` | none | `fresh-merge` job |
| 8 | Pre-commit hooks | (repo-level configs) | none | `.pre-commit-config.yaml` with clang-format |
| 9 | Release automation | auto-release / manual-release | nuspec push trigger | auto + manual (`instant`, `changelog-pr`) |
| 10 | Concurrency control | js per-job + main-writer | none | js style |
| 11 | Secrets detection | rust `secrets-scan` | none | secretlint job |
| 12 | Documentation validation | `validate-docs` | Interfaces `check-cpp-docs.py` + Doxygen WARN_AS_ERROR | both |
| 13 | Container images on native runners per arch | rust/python/js docker jobs | n/a | optional (only when a Dockerfile exists) |
| 14 | Lint the workflows themselves | actionlint + zizmor | none | `workflows.yml` |
| 15 | Audit the dependency tree | cargo audit / pip-audit | none | dependency-review + OSV/`conan audit` |
| 16 | Prove you can publish before you build | `release-preflight` | none (and NuGet broke late) | `release-preflight` for each enabled registry |

---

## 19. Implications for the C++ template

Each item cites the evidence behind it.

### 19.1 Structure

1. **Five workflow files**: `release.yml`, `docs.yml`, `security.yml`,
   `links.yml` and `workflows.yml`, as in python, csharp and php
   (`data/template-workflows/{python,csharp,php}/`).
2. **`release.yml` job graph modelled on rust**
   (`data/template-workflows/rust/release.yml`):
   - detect-changes
   - validate-docs
   - release-preflight
   - changelog
   - version-check
   - secrets-scan
   - fresh-merge
   - lint (clang-format, clang-tidy, file-size)
   - test (OS × compiler matrix + ctest)
   - coverage
   - build (package smoke tests: CMake install + `find_package`, `conan create`, vcpkg overlay port)
   - auto-release
   - manual-release
   - changelog-pr
   - pipeline-status

   The Docker jobs are optional.
3. **Concurrency** as in js (`data/template-workflows/js/release.yml`, lines
   63+): per-job `check-...` groups, plus a `main-writer` group for jobs that
   write to main.
4. **Permissions**: top-level `contents: read`, per-job elevation,
   `persist-credentials: false`, `timeout-minutes` on every job, and pinned
   `ubuntu-24.04`. Evidence: sections 5 and 13; js and csharp already pin
   the runner.

### 19.2 Single- and multi-language modes

5. **Auto-detect the layout.** A root `CMakeLists.txt` means single-language
   mode. `cpp/CMakeLists.txt` means multi-language mode. This follows
   `scripts/release_naming.py` (python) and `scripts/release-naming.mjs`
   (csharp); see section 14. In multi-language mode every job uses
   `working-directory: cpp`.
6. **Tag and title**:
   - single-language: `v<ver>` / `<name> <ver>`;
   - multi-language: `cpp_v<ver>` / `[C++] <ver>`;
   - the prefix is configurable so linksplatform can keep `cpp_<ver>`.

   Evidence: `data/raw/linksplatform-release-tags-sample.txt`, and
   `conan-center-index-platform.interfaces-conandata.yml`, whose URLs depend
   on `cpp_<ver>`.
7. **Coexistence with other languages.** In multi-language repos, the
   `detect-changes` filter must ignore `csharp/**` and `rust/**`. Docs must
   deploy to a sub-path, or be merged with the other languages' docs (see
   section 10). 31 linksplatform repos have both `cpp/` and `csharp/`
   (`data/linksplatform-repos.json`).

### 19.3 Build, test, quality

8. **CMake ≥ 3.16 (3.20+ preferred), C++20 default** (linksplatform tests
   use C++20, and the recipe requires cppstd 20). The C++ standard must be
   configurable. Evidence: `Interfaces-cpp-CMakeLists.txt`,
   `conan-center-index-platform.interfaces-conanfile.py`.
9. **Header-only INTERFACE target as the example library.** This matches
   every linksplatform C++ library (`add_library(<name> INTERFACE)`). A
   compiled-library mode should also be supported.
10. **GTest via Conan 2 / vcpkg / FetchContent.** Linksplatform uses
    `gtest/cci.20210126` via `conanfile.txt` (`Interfaces-cpp-conanfile.txt`).
    **Tests must actually run** through `ctest` (section 15.2, bug 1).
11. **Optional benchmarks** (Google Benchmark via FetchContent, as in
    `Numbers-cpp-CMakeLists.txt`), built but not run as gating tests.
12. **Architecture flags opt-in only.** Put the `-march=...` flags behind an
    option that is OFF by default (section 15.2, bug 7).
13. **Conan 2 profile.** Use `conan profile detect` plus explicit `-s
    compiler.cppstd=20` / `-s build_type=Release`, never `sed` on profile
    files (section 15.2, bug 3).
14. **clang-format and clang-tidy in CI**, with a `.clang-format` compatible
    with `Settings-.clang-format`.

### 19.4 Changelog and release

15. **`changelog.d/` fragments with `bump:` frontmatter**, collected at
    release time (the rust/php format). Section 7 gives the evidence. The
    version source of truth is `project(VERSION)` in CMakeLists. The release
    script must also sync the version into every packaging manifest that
    exists:
    - `conanfile.py`
    - `vcpkg.json`
    - the `.nuspec`
16. **`version-check`**: a PR must not hand-edit the version (js/rust
    `version-check` job).
17. **`release-preflight`** for each enabled registry (Conan remote, NuGet
    API key, GitHub token), and publishing jobs ordered so that the GitHub
    release is created **last**, or rolled back when a registry push fails
    (section 15.1).

### 19.5 Distribution

18. **All distribution methods, each opt-in and each tested in CI:**
    - CMake install/export + package config
      (`find_package(<Name> CONFIG)`);
    - `add_subdirectory` / FetchContent / CPM / git submodule;
    - GitHub release archive + sha256;
    - Conan 2 recipe (`conanfile.py` + `test_package/`) with `conan create`,
      plus an optional remote upload;
    - vcpkg port (overlay + optional registry);
    - NuGet native package via `dotnet pack`/`nuget` from the .NET SDK (not
      apt).

    Linksplatform's current CMakeLists have no install rules (section 15),
    so this is new work.
19. **Linksplatform compatibility settings** (configurable, default off):
    - package id `Platform.<Repo>.TemplateLibrary`;
    - Conan name `platform.<lowercase repo>`;
    - archive `<conanname>_<ver>.zip`;
    - tag `cpp_<ver>`;
    - title `[C++] <ver>`;
    - release body with the NuGet link.

    Evidence: `Workflows-deploy-cpp.yml` lines 34-106 and
    `Workflows-get-cpp-conan-package-info.yml`.

### 19.6 Docs and security

20. **Doxygen docs**: `Doxyfile` with `WARN_IF_UNDOCUMENTED=YES` and
    `WARN_AS_ERROR=FAIL_ON_WARNINGS`, HTML (+ XML) output, deployed with
    `actions/deploy-pages@v5` and gated by `vars.DEPLOY_GITHUB_PAGES`.
    Evidence: `Interfaces-cpp-Doxyfile`, `Interfaces-cpp-docs.yml`, and the
    python/csharp `docs.yml`.
21. **Security workflow**:
    - CodeQL `[c-cpp, actions]` with `build-mode: none` (default) and
      `security-extended,security-and-quality` queries
      (`Interfaces-codeql.yml`);
    - dependency-review;
    - a C++ dependency audit (OSV-Scanner / `conan audit`) when there are
      third-party dependencies.
22. **Workflow lint and link check**: copy `workflows.yml` (actionlint +
    zizmor + status-gate-coverage from js) and `links.yml` (lychee + Web
    Archive recheck). Both are language-neutral.

### 19.7 Migration value for linksplatform

23. Linksplatform has 42 repos with a `cpp/` folder:
    - 21 run a Conan 1 workflow that no longer works;
    - 17 call the reusable workflows, whose NuGet step is broken;
    - 1 (Interfaces) has modern docs/CodeQL additions.

    Evidence: `data/linksplatform-repos.json`. A multi-language C++ template
    that fixes the problems in section 15.2 and keeps the naming in item 19
    can replace all three patterns without breaking existing consumers
    (NuGet ids, Conan recipe URLs, `cpp_<ver>` tags).
