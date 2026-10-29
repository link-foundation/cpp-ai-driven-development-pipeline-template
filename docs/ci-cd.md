# CI/CD

The pipeline is five workflows. `release.yml` (**CI/CD Pipeline**) builds,
tests and releases; the other four check documentation, security, links and
the workflows themselves. Every workflow ends with a **Pipeline Status** job,
the one check to require in the branch protection of `main`.

The job graph, triggers, release model and hardening are the same as in the
[Rust](https://github.com/link-foundation/rust-ai-driven-development-pipeline-template),
[Python](https://github.com/link-foundation/python-ai-driven-development-pipeline-template),
[JavaScript](https://github.com/link-foundation/js-ai-driven-development-pipeline-template)
and [PHP](https://github.com/link-foundation/php-ai-driven-development-pipeline-template)
templates, which follow the
[CI/CD best practices](https://github.com/link-assistant/hive-mind/blob/main/docs/CI-CD-BEST-PRACTICES.md).
The file-by-file comparison is in
[docs/case-studies/issue-1/CICD-COMPARISON.md](case-studies/issue-1/CICD-COMPARISON.md).

## CI/CD Pipeline (release.yml)

Triggers: pull requests, pushes to `main`, and `workflow_dispatch` (manual
release).

| Job | Runs on | What it does |
| --- | --- | --- |
| Detect Changes | PRs, pushes | `detect_code_changes.py`: did code, C++ sources or docs change? Markdown, `docs/`, `changelog.d/` and `experiments/` are not code. |
| Validate Documentation | docs changed | `check-required-docs.sh`: README, CONTRIBUTING and the changelog exist and keep the sections other documents link to. |
| Release Preflight | always | `preflight-credentials.sh`: checks credentials and reports verified, refused or unknown access (advisory on PRs, refusals block releases). |
| Changelog Fragment Check | PRs with code changes | `check_changelog_fragment.py`: the PR adds a fragment to `changelog.d/`. |
| Version Modification Check | PRs | `check_version_modification.py`: the PR does not edit the version by hand. |
| Secrets Scan | PRs, pushes | secretlint over the tracked files. |
| Fresh Merge Simulation | PRs with code changes | merges the latest base branch and builds and tests the result (`dev` preset). |
| Lint and Format Check | code changed | clang-format, clang-tidy and cppcheck (`lint_cpp.py`) at the versions pinned in `scripts/requirements-ci.txt`; file size limits of the changed files. |
| Test | code changed | GCC and Clang on Ubuntu, Apple Clang on macOS, MSVC on Windows; `dev` (Debug) and `release` (Release + benchmarks) workflow presets; `check_consumers.py` builds every consumer example. |
| Sanitizers | code changed | the tests under AddressSanitizer and UndefinedBehaviorSanitizer (`asan` preset). |
| Release Script Tests | code changed | pytest over `scripts/tests`. |
| Code Coverage | C++ changed | `coverage` preset and gcovr with a 90 % line floor (`gcovr.cfg`); uploads to Codecov when `CODECOV_TOKEN` is set. |
| Build Packages | lint, test, sanitizers and script tests passed | every release asset (`package_release.py`), a real NuGet restore, `conan create`, and a real `vcpkg install` of the rendered port; uploads the assets as an artifact. |
| Auto Release | pushes to `main` | see [Release flow](#release-flow). |
| Instant Release | manual, `instant` | bumps the chosen version part and publishes. |
| Create Changelog PR | manual, `changelog-pr` | opens a PR that adds a fragment for the chosen bump. |
| Pipeline Status | always | fails when any needed job failed or was cancelled (`check-pipeline-status.sh`). |

Long steps run under `run-with-budget-warning.sh`: it warns at 70 % of the
step's time budget and stops the step when the budget runs out, so a hang
fails with a clear message before the job timeout.

### Design rules

- **Least privilege**: the workflow default is `contents: read`; only the
  jobs that push, release or deploy get write scopes.
- **No credentials in branch code**: `persist-credentials: false` on every
  checkout except the release jobs that push, and publishing secrets are set
  on the steps that need them, never at the workflow level (CMake runs
  arbitrary code of the branch).
- **Pinned actions**: every remote action uses a full commit hash and Docker
  images use digests. Zizmor enforces this without namespace exemptions;
  Dependabot proposes updates to the pins.
- **Explicit runner images**: all five workflows use `ubuntu-24.04`; the
  compiler matrix also uses `macos-15` and `windows-2025`. These labels fix
  the OS generation while GitHub continues updating tools within the images.
  Policy tests reject floating `-latest` runner labels and require the Git
  initial-branch environment configuration before checkout in every workflow.
- **Job-scoped concurrency**: read-only jobs cancel their superseded run on
  branches, never on `main`. Release, changelog and Pages writers across
  workflows share `repository-main-write` with `cancel-in-progress: false`
  and `queue: max`, retaining up to 100 waiting jobs. Read-only checks use
  separate groups. Push recovery remains bounded and never force-pushes.
- **`!cancelled()` instead of `always()`** on jobs that need skipped jobs
  ([actions/runner#491](https://github.com/actions/runner/issues/491)), so
  a cancelled run cancels them too.
- **Fail before building**: the credential preflight runs in parallel with
  the build, and releases need it to pass.

## Release flow

1. Every pull request with code changes adds a changelog fragment,
   `changelog.d/*.md`, whose front matter sets the bump (`major`, `minor` or
   `patch`). See [CONTRIBUTING.md](../CONTRIBUTING.md#changelog-management).
2. When the pull request is merged, **Auto Release** runs after **Build
   Packages** and **Release Preflight** passed:
   1. `get_bump_type.py` takes the highest bump of the pending fragments.
   2. `check_release_needed.py` decides whether to release. Without fragments
      it checks that the current version was fully published (the GitHub
      release and, with `NUGET_PUBLISH=true`, the NuGet package) and re-runs
      the publication for the same version when something is missing, so a
      release that failed half-way heals on the next push.
   3. `version_and_commit.py` bumps `project(VERSION)` in `CMakeLists.txt`
      and `vcpkg.json` (`bump_version.py`), moves the fragments into
      `CHANGELOG.md` (`collect_changelog.py`), commits, tags (`v1.2.3`, or
      `cpp_v1.2.3` in a multi-language repository) and pushes.
   4. `publish-release.sh` builds the assets from the tag, pushes to NuGet
      and the Conan remote when configured, then creates the GitHub release
      (`create_github_release.py`). Each step skips what is already
      published, so re-runs are safe.
      When `NUGET_USER` is set, the publishing job first obtains a temporary
      API key through hash-pinned `NuGet/login`. Only the automatic and
      instant publishing jobs receive `id-token: write`. When `NUGET_USER`
      is unset, the existing `NUGET_API_KEY` secret remains the fallback.
3. A release can also be started from the Actions tab (**CI/CD Pipeline** →
   **Run workflow**): `instant` releases the chosen bump immediately, and
   `changelog-pr` opens a pull request with a fragment first.

The channels and the assets are described in
[distribution.md](distribution.md).

## Documentation

`docs.yml` (**Docs**) runs Doxygen on every push and pull request. The
`Doxyfile` sets `WARN_IF_UNDOCUMENTED` and `WARN_AS_ERROR =
FAIL_ON_WARNINGS`, so an undocumented public symbol, an undocumented
parameter or a broken reference fails the pull request. The input is
`include/` and `docs/mainpage.md` (the main page), and the version comes from
`CMakeLists.txt`.

The HTML and the XML (for Sphinx with Breathe, or other generators) are kept
as the `api-reference` workflow artifact. To publish the HTML to GitHub
Pages:

1. Settings → Pages → Source: **GitHub Actions**.
2. Set the repository variable `DEPLOY_GITHUB_PAGES` to `true`.

Pushes to `main` then deploy to `https://<owner>.github.io/<repo>/`. In a
multi-language repository the reference is published under `/cpp/` with a
redirect from the root. A Pages site has a single source, so when another
language also publishes Pages, build every site into one artifact in one
workflow instead.

Locally: `doxygen Doxyfile` (output in `docs/api/`), or build the
`my_package_docs` CMake target.

## Other workflows

| Workflow | Triggers | Checks |
| --- | --- | --- |
| `security.yml` (**Security**) | PRs, main pushes, weekly, manual | Fatal CodeQL SARIF gate for C/C++ and workflows; full Python/native dependency audits; additional PR dependency review. |
| `links.yml` (**Broken Link Checker**) | markdown or HTML changes | lychee, a re-check of links that never answered, and a Web Archive fallback. `.lycheeignore` lists the exceptions. |
| `workflows.yml` (**Workflows**) | workflow changes | actionlint, independent concurrency queue validation and zizmor; every remote action uses a full commit SHA (Docker uses a digest). |

The security workflow retains CodeQL SARIF and requires explicit successful
invocations, complete reports and no findings at any result level. Failed or
unknown execution state and warning/error tool diagnostics fail the job and
the terminal Pipeline Status. Analysis/upload success alone is insufficient.

Full audits run independently of dependency review. `pip-audit --strict`
resolves all pinned CI/audit requirements and their transitive dependencies;
its JSON validator rejects findings, skipped packages and incomplete reports.
The native audit resolves the Conan host/build graphs, CMake test/benchmark
dependencies and every vcpkg manifest feature, including transitive build
helpers, plus the CPM consumer's pinned bootstrap version and integrity hash.
It retains raw graphs, exact vcpkg versions/port revisions, a provider
SBOM and coverage status under `security-reports/`. No packages are compiled.

ConanCenter's supported audit provider requires a free token from
[Conan Audit](https://audit.conan.io/register). Configure the Actions secret
`CONAN_AUDIT_PROVIDER_TOKEN_CONANCENTER`. Without it, PRs explicitly warn and
record **incomplete** native coverage; main, weekly and manual runs fail with
setup instructions. This permits reviewing a new template before an owner
configures the provider. With credentials, provider refusals, unresolved or
unknown packages (including unsupported vcpkg helpers or CPM), missing verdicts and
vulnerabilities fail on every event. A missing token never produces a clean
verdict. The native NuGet package declares no dependencies, verified in the
packaging tests; adding NuGet dependencies requires a locked restore with
transitive auditing and warnings as errors.

The pinned actionlint 1.7.12 predates `queue`. Before linting, the helper
`check_workflow_concurrency.py --actionlint-compat` validates block-style queue
placement, literal values and cancellation compatibility, then comments out
only those validated lines in the disposable checkout. Every other line goes
unchanged to actionlint, including unsupported inline/quoted queue forms.
No diagnostic category is suppressed; shell checks remain enabled.
Dependabot maintains action pins.

The dependency review needs the dependency graph: enable it in Settings →
Advanced Security → **Dependency graph**. Until then
`scripts/check-dependency-review-support.sh` sees the API refuse the
comparison (HTTP 403) and the job skips the review with a
"Dependency review skipped" warning instead of failing every pull request.

## Variables and secrets

Publishing credentials are optional; native security auditing requires the
provider token above. See the table in the
[README](../README.md#configuration). The credential preflight reports each
configured channel on pull requests and fails releases on refused credentials
or when no credential could be verified. An unknown channel does not block a
release if another channel was verified; it is never counted as verified:

- **NuGet API key**: first obtains a one-time verification key, which checks
  key validity and general push scope only. It then looks up the newest
  published version in the public flat-container index and calls
  `GET /api/v2/verifykey/{id}/{version}` with the one-time key, consuming it
  and checking its owner scope. NuGet replaces the original package glob
  with the requested ID when creating that key, so preflight calls the same
  endpoint again with the original API key to check its actual push scopes,
  package glob and owner. Both verification calls must return HTTP 200
  before NuGet is counted as verified. HTTP 401/403
  fails; no published version, HTTP 404, malformed responses, rate limits
  and network errors report `unknown`. The gallery deletes the one-time key
  after verification. No package is pushed. `NUGET_FLAT_CONTAINER_URL` and
  `NUGET_GALLERY_URL` can override the endpoints for testing.
- **NuGet trusted publishing**: `NUGET_USER` takes priority, even when an old
  API-key secret exists. Preflight reports the mode and `unknown`, because
  the OIDC exchange runs later in the publishing job. A login failure stops
  that job; it does not silently switch to the secret. See
  [setup instructions](distribution.md#nuget).
- **Conan**: logs in to `CONAN_REMOTE_URL` with `CONAN_LOGIN_USERNAME` and
  `CONAN_PASSWORD`; a refused login fails, while a successful login is
  `unknown` because the API offers no dry-run upload.
- **GitHub**: tries to create an invalid ref with the workflow's
  `GITHUB_TOKEN`; the validation error (422) proves write access without
  writing anything.

Set `PREFLIGHT_VERBOSE=true` for HTTP status/URL diagnostics; headers and
response bodies containing keys are never printed.

## Running the checks locally

```bash
cmake --workflow --preset dev                 # Test (Debug)
cmake --workflow --preset release             # Test (Release)
cmake --workflow --preset asan                # Sanitizers
cmake --workflow --preset coverage && gcovr --object-directory build/coverage
cmake --preset lint && python3 scripts/lint_cpp.py
python3 scripts/check_consumers.py            # consumer examples
python3 -m pytest scripts/tests               # Release Script Tests
python3 scripts/check_workflow_concurrency.py # queue policy (before actionlint)
python3 -m pip install -r scripts/requirements-security.txt
python3 -m pip_audit --strict -r scripts/requirements-ci.txt -r scripts/requirements-security.txt
python3 scripts/audit_native_dependencies.py  # Conan profile, vcpkg and provider token required
python3 scripts/package_release.py --out-dir dist --nuget   # Build Packages
bash scripts/check-required-docs.sh           # Validate Documentation
doxygen Doxyfile                              # Docs
```
