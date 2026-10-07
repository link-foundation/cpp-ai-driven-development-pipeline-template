# Issues 5, 6 and 7: workflow stability and NuGet authorization

Research date: 2026-10-07. Baseline: `16bac38` on `main`, with the prepared
PR branch initially at `0ea3cee`. The issue bodies and all comments were read;
issues 5, 6 and 7 and PR 8 had no discussion or review comments at that time.

Scope: [parent issue 7](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/issues/7),
[issue 5](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/issues/5)
and [issue 6](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/issues/6),
implemented together in [PR 8](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/pull/8).

## Every requirement and its implementation plan

The table includes the parent issue's process requirements and every distinct
behavior requested by the two sub-issues, including their suggested fixes.

| ID | Requirement | Solution and verification plan |
| --- | --- | --- |
| 7.1 | Read every selected issue and its comments thoroughly. | Read all three bodies and paginated issue comments; also read PR conversation comments, inline review comments and reviews. |
| 7.2 | Implement both issues completely in one PR without follow-up deferrals. | Update only the prepared branch and PR 8; cover all five active workflows, both publishing jobs, scripts, tests and current documentation. |
| 7.3 | Close the parent and every selected issue on merge. | End the PR description with separate `Fixes #5`, `Fixes #6` and `Fixes #7` lines. |
| 7.4 | Use one closing keyword per issue and preserve the supplied closing block. | Keep `Fixes #5` followed by `Fixes #6` verbatim, then add `Fixes #7`. |
| 7.5 | Explicitly identify already resolved or unreproducible issues while retaining closing references. | Both defects are present and reproduced in tests; say so in the PR. Live wrong-owner credentials are unnecessary for the local reproduction. |
| 5.1 | Remove floating Ubuntu runner labels in every workflow job. | Replace all 27 literal job labels with `ubuntu-24.04`; enforce the policy over every `.yml` and `.yaml` active workflow. |
| 5.2 | Pin the entire compiler matrix, including Linux, macOS and Windows. | Use `ubuntu-24.04`, `macos-15` and `windows-2025`, retaining the compiler and Debug/Release coverage. |
| 5.3 | Prevent future `-latest` values in `runs-on:` and matrix `os:`. | Add policy tests covering scalar values, inline arrays and multiline runner lists. |
| 5.4 | Hash-pin lychee and zizmor, retaining readable version comments. | Resolve the existing refs using GitHub's API and use their full 40-character commit hashes; do not change tool behavior as part of pinning. |
| 5.5 | Remove the two namespaces' zizmor tag-pin exemptions so zizmor and CodeQL agree. | Remove `lycheeverse/*` and `zizmorcore/*` from `ref-pin`; assert they use the existing wildcard hash policy. Keep Dependabot action updates enabled. |
| 5.6 | Eliminate Git's default-branch hint in all workflows.yml jobs. | Add workflow-level `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_0=init.defaultBranch` and `GIT_CONFIG_VALUE_0=main`, before checkout. Test the block in all five workflows. |
| 5.7 | Recognize GitHub's macOS capacity notice as external. | Preserve it if GitHub emits it; no warning suppression or unrelated capacity changes. |
| 6.1 | Stop claiming package authorization from verification-key creation alone. | Count NuGet as verified only after checking both the temporary and original keys; correct script comments, README and distribution/CI documentation. |
| 6.2 | Finish the NuGet verification flow against a published version. | POST to create the one-time key, query the lowercase package's public version index, then GET `/api/v2/verifykey/{id}/{version}` with the temporary key and again with the original key. The original-key check is required because NuGet replaces the temporary key's package glob. Use the last index entry as nuget.org's newest published version. |
| 6.3 | Send the returned one-time Key in the second request's X-NuGet-ApiKey header. | Parse JSON with Python's standard library; use the temporary key for its verification GET and the original publishing key for POST and the final GET. Send no credential to the public index. |
| 6.4 | Treat 200 from verification as OK and 401/403 as failure. | Require both GETs to return 200; reproduce POST/temporary-key 200 followed by original-key 401/403, as well as temporary-key refusals. Enforce release-mode failure and advisory PR mode. Retain invalid/expired-key rejection at POST. |
| 6.5 | Report 404 or no published version as unknown scope, including first pushes. | Cover missing/empty indexes, verification 404, malformed JSON, unreachable services and 429/500. Never add an unknown outcome to the verified count. |
| 6.6 | Retain Content-Length: 0 on the empty POST. | Assert the header in the local HTTP mock to prevent the reported 411 regression. |
| 6.7 | Consume the one-time key through the verification endpoint. | Complete its GET when a published version is available; NuGetGallery deletes that key after evaluating it. Its subsequent original-key check does not delete the publishing credential. Do not publish a package during any probe. |
| 6.8 | Support NuGet trusted publishing with job-scoped id-token: write. | Grant OIDC issuance to the existing automatic and instant publishing jobs; preserve the existing GitHub Pages deployment's independent OIDC permission. Do not grant it to preflight or other checks. |
| 6.9 | Use hash-pinned NuGet/login with vars.NUGET_USER and pass its API-key output to push. | Add a conditional login immediately before both publishing steps. Feed its output into `NUGET_API_KEY`, already consumed and masked by `publish-release.sh`. Skip login when NuGet is disabled or an automatic retry has already published that version. |
| 6.10 | Keep the secret as a fallback and report the selected mode. | Select trusted publishing whenever `NUGET_USER` is set; otherwise use the existing secret. Preflight reports the mode. A failed OIDC login stops the job instead of silently falling back. |

The patch changelog fragment triggers the existing automatic version bump.
The version sources remain unchanged, as required by the repository's version
modification check. No library features or distribution channels are removed.

## Root cause and additional research

The GitHub API confirmed two open `actions/unpinned-tag` alerts at the
baseline: lychee in `links.yml:52` and zizmor in `workflows.yml:93`. The
existing test dynamically trusted the same namespaces as zizmor, so it
accepted both mutable tags. Runner and initial-branch policies had no tests.

[GitHub's hosted-runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
confirms the explicit labels used here. Fixing an OS label avoids automatic
OS-generation migration; GitHub still updates software inside that image.
This is not a promise of a byte-identical runner filesystem.

[NuGetGallery's ApiController at the issue's source revision](https://github.com/NuGet/NuGetGallery/blob/2f271fb8651906ecd841d0a658f9afc670e7021d/src/NuGetGallery/Controllers/ApiController.cs#L328-L414)
explicitly defers package/owner validation from key creation to verification.
The previous script stopped after creation, so any valid push key could
produce a false positive. The verification path loads the existing package
and evaluates the presented key's scopes and owner permissions, then deletes
it if it is a one-time key.

The restart audit found an additional limitation in the issue's suggested
two-call fix. [CredentialBuilder.CreatePackageVerificationApiKey](https://github.com/NuGet/NuGetGallery/blob/2f271fb8651906ecd841d0a658f9afc670e7021d/src/NuGetGallery.Services/Authentication/CredentialBuilder.cs#L71-L101)
copies only the original key's owner keys, replacing its package glob with
the requested package ID and its action with `PackageVerify`. A key scoped to
`Some.Other.*` can therefore obtain and successfully verify a temporary key
for a package owned by the same account. That temporary-key result cannot
prove the original key's package glob permits the push. This behavior remains
in the current NuGetGallery source checked on 2026-10-07.

`VerifyPackageKeyInternalAsync` also accepts the original API key; in that
case it checks `PackagePush`/`PackagePushVersion` against the original scopes.
The completed preflight consumes the temporary key first, then checks the
original key at the same endpoint. It records success only after both checks
return 200. This adds a request to the suggested fix because otherwise the
wrong-glob false positive in issue 6 remains reproducible.

[NuGet's flat-container documentation](https://learn.microsoft.com/en-us/nuget/api/package-base-address-resource)
describes the lowercase ID version index, including unlisted versions and
404 for packages with no versions. This provides an existing version without
downloading an archive or attempting a push. A lookup failure cannot establish
package authorization, and a first push has no package version to check.

[Microsoft's trusted-publishing instructions](https://learn.microsoft.com/en-us/nuget/nuget-org/trusted-publishing)
describe registering a repository/workflow policy and exchanging OIDC for a
short-lived key. [NuGet/login](https://github.com/NuGet/login) supplies the
exchange and `NUGET_API_KEY` output. The preflight job deliberately does not
request that key: it would belong to a different job and could expire while
builds run. It reports the deferred exchange as unknown. The publishing job
requests its own key shortly before invoking the existing publisher.

The issue's 365-day API-key lifetime is outdated. Microsoft's
[2026-08-03 lifetime announcement](https://devblogs.microsoft.com/dotnet/strengthening-nuget-supply-chain-security-reducing-api-key-lifetime/)
states that keys created from 2026-08-17 have a 30-day maximum, and older
keys expire on 2026-11-01. The secret fallback remains useful for existing
setups, but trusted publishing avoids this recurring rotation requirement.
Multi-language setup instructions also cover registering a policy for the
actual workflow filename after renaming `release.yml` (for example `cpp.yml`).

The closely related [Interfaces PR 151](https://github.com/linksplatform/Interfaces/pull/151)
implements these policies and the suggested temporary-key probe in JavaScript;
the original-key check above is needed to cover the glob limitation in that
suggestion.
Its code and tests were inspected through authenticated GitHub API requests.
This template keeps its existing Bash entry point and Python standard-library
JSON parsing rather than adding Node or another production dependency.

## Existing components and alternatives

| Requirement | Existing component or alternative | Decision |
| --- | --- | --- |
| Workflow reproducibility | Explicit hosted-runner labels; alternatively container images or custom runners. | Explicit labels match the requested platforms without changing the toolchain or maintenance model. |
| Action immutability | Full commit SHA pins and the existing Dependabot configuration. | Keep readable version comments and automated update PRs. |
| Security audit | Existing [zizmor](https://docs.zizmor.sh/audits/#unpinned-uses) and CodeQL. | Align their policies; add tests to prevent a future trust exemption from restoring the alerts. |
| Workflow schema/shell validation | Existing [actionlint](https://github.com/rhysd/actionlint), whose pinned Docker image bundles shellcheck. | Run the same image locally and in CI; no duplicate linter implementation. |
| Package-scope preflight | NuGetGallery's existing verification API, which accepts temporary and ordinary push keys; alternatively a real package push. | Consume the temporary key, then verify the original key's actual scopes. No package is published. Temporary-key verification alone loses the original glob and is insufficient. |
| Minimal reporting-only fix | Label key-creation success as general push access, leaving scope unknown. | Insufficient for the requested complete flow; complete both verification requests. |
| Passwordless publishing | Official NuGet/login; alternatively a custom HTTP OIDC exchange. | Use the existing maintained action with a verified hash, avoiding custom token handling. |
| JSON/URL processing | Python standard library; alternatively jq, a NuGet SDK or third-party HTTP/JSON packages. | Python is already required; no new runtime dependency is needed. |
| Regression reproduction | Existing pytest and local ThreadingHTTPServer fixture. | Extend the fixture to reproduce successful key creation followed by denied package access without real credentials. |

Resolved refs, verified via `gh api repos/OWNER/REPO/commits/REF`:

| Action | Ref | Commit |
| --- | --- | --- |
| lycheeverse/lychee-action | v2 (also v2.9.0) | `e7477775783ea5526144ba13e8db5eec57747ce8` |
| zizmorcore/zizmor-action | v0.6.4 | `cc914d7f3750a2d13d75c7f184a1060aa0e9d482` |
| NuGet/login | v1 | `8d196754b4036150537f80ac539e15c2f1028841` |

## Reproduction and verification

Before implementation, the expanded focused suite produced **32 failures and
44 passes**. The smallest false-positive reproduction is
`test_valid_key_with_wrong_package_glob_or_owner_fails`: the mock issues a
verification key with HTTP 200 but refuses verification with 401 or 403.
The old script exits successfully; the fixed script reports refused scope
and exits 1 in release mode. No live key or package push is required.

The restart added a more precise wrong-glob reproduction,
`test_temporary_key_cannot_prove_original_package_glob`: POST and temporary-key
verification both return 200, while verification with the original key
returns 401/403. Before the final correction, the expanded focused cases had
**7 failures**: the remaining false positive, missing original-key request,
and original-key uncertainty were all demonstrated. The final script checks
the original credential and preserves unknown results for its 404, 429, 500
and disconnected responses. The mock records both verification headers and
checks that the temporary key is consumed before the original key is tested.

```bash
python3 -m pytest -q scripts/tests/test_preflight_credentials.py scripts/tests/test_workflows.py
python3 -m pytest -q scripts/tests
cmake --workflow --preset dev
cmake --workflow --preset release
cmake --workflow --preset asan
cmake --preset lint && python3 scripts/lint_cpp.py
python3 scripts/check_consumers.py
docker run --rm -v "$PWD:/repo" -w /repo \
  rhysd/actionlint@sha256:b1934ee5f1c509618f2508e6eb47ee0d3520686341fec936f3b79331f9315667
zizmor --offline --min-confidence medium --persona regular \
  --config .github/zizmor.yml .github/workflows
zizmor --offline --persona pedantic --min-severity high --min-confidence high \
  --config .github/zizmor.yml .github/workflows
```

Large local outputs and reproduction logs are retained under
`experiments/issue-7/` (ignored `*.log` files); downloaded CI logs are kept
in `ci-logs/`. CI verification must match the latest branch SHA and run
timestamp, not a previously passing run.

Local validation completed successfully:

| Check | Result |
| --- | --- |
| All release/script tests | 306 passed, including six additional original-key regression cases |
| C++ Debug, Release, ASan + UBSan, coverage presets | 10 tests passed in each preset |
| Coverage | 100% lines, 100% functions, 93.3% branches |
| clang-format, clang-tidy, cppcheck | All passed at the pinned versions |
| Consumer examples | All five consumption methods passed |
| Release packaging and real NuGet restore | Passed |
| Conan create and test_package | Passed |
| vcpkg overlay-port install and CMake consumer | Passed |
| actionlint Docker image with shellcheck | Passed |
| shellcheck on both publishing/preflight scripts | Passed |
| zizmor regular and high-severity/high-confidence pedantic passes | No findings |
| Required documents, file size and diff whitespace | Passed |

The workflow tests include every active `.yml`/`.yaml` file. The old workflow
copies under `docs/case-studies/issue-1/data/` describe other repositories at
the time of the initial research; they remain historical evidence. Current
setup instructions in README, CI/CD, distribution and multi-language docs
are updated.

## Limits and configuration

NuGet's first-push authorization cannot be verified against a nonexistent
version. OIDC preflight reports the selected mode without claiming that the
future exchange is proven. As before, unknown channels may proceed if another
credential is verified; known refusals block a release. Pull requests report
refusals without blocking because forks can have no publishing secrets.

Trusted publishing requires a nuget.org policy and `NUGET_USER` configured by
the repository owner; see [NuGet setup](../../distribution.md#nuget). This PR
adds the supported path without changing external account configuration or
publishing a package during testing.
