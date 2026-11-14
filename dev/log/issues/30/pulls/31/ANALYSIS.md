# Investigation and solution decisions

## Scope and failure diagnosis

The complete issue, its follow-up, all required sub-issues (none), PR conversation
comments, inline review comments, and reviews (initially none) are saved under
`raw/`. [PLAN.md](PLAN.md) maps each acceptance requirement to implementation and
verification. [DEPENDENCIES.md](DEPENDENCIES.md), [PYTHON-LOCK.md](PYTHON-LOCK.md)
and [NPM-LOCK.md](NPM-LOCK.md) inventory direct, transitive and platform dependencies.

The merged Dependabot PRs 26 and 27 did not leave the main C++ build broken.
The latest completed main runs at 2565890 passed CI/CD, Docs and Workflows.
The failures named in the original issue were earlier PR runs. The issue's
follow-up confirms the later timestamps. Security run 43575793401 did fail:
`ci-logs/main-security-43575793401.log:595` reports the absent
`CONAN_AUDIT_PROVIDER_TOKEN_CONANCENTER`, with the aggregate failure at line 4952.
This is an external setup requirement, rather than a Python/API migration error.

Reproduction: install the pinned Conan, detect a profile, then run
`GITHUB_EVENT_NAME=push python scripts/audit_native_dependencies.py`. Without
the registered provider token, it resolves coordinates and fails with an explicit
incomplete verdict. The same script on `pull_request` warns and preserves reports.
Existing regression tests in `scripts/tests/test_audit_dependencies.py` cover both
event policies, findings, unknown packages, malformed/provider errors and missing
credentials. Changing the missing token to a clean verdict would weaken the scan.

[Conan's supported audit documentation](https://docs.conan.io/2.25/devops/audit.html)
requires registration at [Conan Audit](https://audit.conan.io/register). No credential
is available in this workspace. Configuring a repository secret or merging to main
cannot be accomplished by a code-only PR on the authorized branch. Main remains
unverified/unfinished; this PR must remain unmerged.

## Python and hooks

All original direct Python pins already matched PyPI's latest stable releases.
The gap was unconstrained transitives, unpinned pre-commit/toolchain tools and the
20.1.8 hook formatter conflicting with CI's 23.1.5. The new regression test fails
against the original baseline and passes after alignment; its reproducible probe
is `experiments/reproduce_issue_30_formatter_drift.py`.

The selected solution is canonical `.in` inputs, generated direct manifests,
and one portable, fully pinned constraints resolution. Every existing pip
requirements install imports the shared constraints; Conan's extracted install
explicitly applies them too. Python 3.15.2 is used in configured Python jobs,
`.python-version` and local final verification. Hook environments pin ruamel.yaml
0.19.1, and the same hook package is included in the audited Python resolution.

Components considered:

| Component | Benefit | Decision |
| --- | --- | --- |
| [uv pip compile](https://docs.astral.sh/uv/pip/compile/) | Native universal/platform-marker resolution, fast cached installs | Selected; avoids home-grown platform lock merging |
| [pip-tools](https://github.com/jazzband/pip-tools) | Established requirements compilation | Researched current 7.6.2; not added alongside a second solver |
| [pre-commit](https://pre-commit.com/) | Managed hook environments and autoupdate | Upgrade to 4.7.0, hooks 6.0.0 and formatter 23.1.5 |
| [Dependabot](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories) | Existing updater; now supports pre-commit and vcpkg | Cover pip/scripts, Actions, hooks, vcpkg and new npm manifest |
| [Renovate](https://docs.renovatebot.com/) | Regex/custom managers could update remaining CMake/tool literals | Alternative documented; avoid competing bots and unsolicited automerge |

Major migration review:

- [Python 3.14 porting](https://docs.python.org/3.15/whatsnew/3.14.html)
  and [3.15 porting](https://docs.python.org/3.15/whatsnew/3.15.html): deferred
  annotations, process changes, UTF-8 defaults and removed APIs were reviewed.
  The scripts use standard-library APIs and explicit subprocess arguments; the
  complete suite runs on 3.15.2. No warning filter or test skip was introduced.
- [pre-commit-hooks 6 changelog](https://github.com/pre-commit/pre-commit-hooks/blob/v6.0.0/CHANGELOG.md):
  Python >=3.9 and removal of two unused hooks require no product changes.
  The current pre-commit `unsupported` language replaces the old `system` alias.
- [clang-format style reference](https://clang.llvm.org/docs/ClangFormatStyleOptions.html):
  migrate the deprecated template-declaration key and structured SortIncludes
  syntax. The complete tracked C++ source set passes the latest formatter.
- [ruamel.yaml release notes](https://yaml.dev/doc/ruamel.yaml/): 0.19.1 removes
  the unconditional compiled YAML dependency. Default round-trip parsing used
  by the hooks requires no optional extension or local compatibility shim.

## Actions, native dependencies and toolchains

Every action commit was compared with the latest upstream stable release.
Most existing SHAs were current already; update create-pull-request to 8.1.3
and label unchanged references precisely. Newly used setup-node, setup-cmake
and zizmor-action are also pinned to immutable current-release commits.

The current zizmor-action 0.8.1 now includes the pinned 1.32.0 wheel in its hash
table. Use that upstream feature and delete the two pipx installation wrappers.
Retain both regular findings and the narrow high-confidence/high-severity
pedantic gate, with annotation output and failing exit codes. A regression test
executes version extraction and checks both action invocations follow the same
manifest, including failure when the pin is absent.

The Actions major runtimes from the merged updates already pass on the default
branch; none is downgraded. setup-node 7's ESM/authentication behavior was reviewed
in its [release notes](https://github.com/actions/setup-node/releases/tag/v7.1.0):
this workflow uses neither registry authentication nor package-manager caching.

GoogleTest stays at 1.18.0. Benchmark moves to 1.10.0 with a verified source hash;
CPM moves to 0.43.2 with its bootstrap hash verified. The Benchmark API used by our
two cases is unchanged. The latest vcpkg baseline still contains Benchmark 1.9.5,
so a small overlay updates its version/hash while retaining the official port's
build/packaging logic. The native dry-run proves both Conan and vcpkg select 1.10.0.
The overlay is removable when [vcpkg issue 55056](https://github.com/microsoft/vcpkg/issues/55056)
is resolved. Check out the same manifest baseline in packaging/audit jobs; its
metadata pins the latest vcpkg tool. Upstream checkout replaces the old unpinned
git-clone fallback.

[CMake 4 migration notes](https://cmake.org/cmake/help/latest/release/4.0.html)
remove obsolete compatibility behavior. Our own minimum 3.25 is already modern;
declare tested policy compatibility through 4.5 rather than overriding old
policies to make dependencies compile. Install upstream CMake 4.5.0 because the
PyPI/Conan distributions currently lag at 4.4.4. Conan's Benchmark build graph
still resolves 4.4.4; keep the real audited coordinate and record the upstream
registry limitation instead of falsifying it.

Use current GA Ubuntu 26.04/macOS 26/Windows 2025 images, not preview labels.
Compiler versions follow those curated vendor distributions; exact snapshots
and the gap to newer upstream GCC/LLVM are recorded in DEPENDENCIES.md.
The [GCC 16 migration notes](https://gcc.gnu.org/gcc-16/changes.html) were reviewed;
we do not claim the GA image has GCC 16 merely because it is the newest OS image.
The portable PyPI clang-tidy wheel also lags upstream LLVM by one patch release.

[.NET 11 release](https://dotnet.microsoft.com/en-us/download/dotnet/11.0)
and [breaking changes](https://learn.microsoft.com/en-us/dotnet/core/compatibility/11)
were reviewed. Only NuGet client pack/restore is used, with no managed application
API migration. Pin SDK 11.0.100 in global.json; the selected Ubuntu image ships it.
The project/package release version remains automatic; a patch changelog fragment
prepares the next release as required by CONTRIBUTING.md.

## npm and security limits

The scanner was previously hidden behind unpinned `npx` arguments. Give secretlint
and its recommended rules exact 13.1.0 pins and commit their full lock. Node 26.13.1
is the newest stable official release (exclude 27 alpha); its archive checksum was
verified. Pin npm 12.2.2 as the package-manager toolchain. npm 12's supported Node
patch floor is met. [secretlint 13 release notes](https://github.com/secretlint/secretlint/releases/tag/v13.1.0)
were reviewed; the recommended preset configuration continues to work.

The unconstrained scanner initially resolved 23 packages below their latest major.
A bounded Node 26 probe and the committed `scripts/test_secretlint.mjs` verify
latest-major detection, all console formatters, YAML configuration, JSON
code-frame errors, SPDX/package metadata and schema URI resolution. Twelve
root overrides update the upstream parents' still-old ranges; newer upstream
implementations remove obsolete child packages, reducing 83 resolved packages
to 76, all current. [NPM-MIGRATIONS.md](NPM-MIGRATIONS.md) records each migration
and its reviewed source. No shim, skipped test or advisory suppression is used.

The secretlint tree has zero reported advisories. A separate metadata/install
audit of npm 12.2.2 itself finds **two public advisory families**, propagated as
21 moderate package findings: [glob cancellation](https://github.com/advisories/GHSA-3g3m-2fjr-6pw4)
and [minimatch amplification](https://github.com/advisories/GHSA-g3hv-75wg-m249).
Consumer overrides to current patched major versions and `npm audit fix` do not
replace npm's bundled copies. The published CLI must be rebuilt upstream; an old
CLI downgrade suggested by audit is not accepted. Existing report
[npm/cli#10299](https://github.com/npm/cli/issues/10299) has the exact reproducer,
affected versions, repair proposal and override limitation. The original audit
is retained as `raw/npm-cli-audit.json`. This is a remaining blocker to the
"no unresolved advisories in all tooling" acceptance criterion, even though
Python and project npm dependency audits pass.

Conan Audit was compared with [OSV](https://google.github.io/osv.dev/api/): an
empty result for an unmapped Conan/vcpkg/CPM coordinate cannot establish coverage.
Replacing the supported provider with an unverified coordinate translation would
weaken the existing fail-closed audit. Registration/token and unknown-coordinate
coverage therefore remain explicit prerequisites, with no invented clean verdict.

## Existing dependency workarounds

- [actionlint queue support](https://github.com/rhysd/actionlint/issues/657),
  [proposed parser fix](https://github.com/rhysd/actionlint/pull/654) and
  [Ubuntu runner label](https://github.com/rhysd/actionlint/issues/682): latest
  1.7.12 still needs the queue adapter and narrow documented label extension.
  Preserve enum/policy regression tests and all remaining syntax checks.
- [lychee connect-reset retries](https://github.com/lycheeverse/lychee/issues/2297):
  0.24.2 still has the reported classifier gap. Preserve the bounded retry adapter
  and its permanent-error regression tests. The upstream report already includes
  a minimal HTTPS reset server and suggested retry.rs fix; no duplicate issue or
  resource-exhaustion probe is needed.
- npm bundled dependency advisories and vcpkg registry lag are linked above;
  upstream comments/reports and exact URLs are recorded in UPSTREAM.md.

The first research commit exposed eight broken relative links inside a verbatim
download of another repository's Markdown guide (links run 43578484004, errors
at lines 289-318). Store upstream Markdown snapshots as `.txt`, preserving their
bytes and source URL, so they are not misrepresented as local repository docs.
No live documentation URL is ignored to pass the checker. Pre-commit similarly
preserves archived investigation evidence rather than rewriting source snapshots.

The general logic that belongs upstream remains bounded locally until a supported
release replaces it. Current PR CI and reproducible local evidence are recorded
in VERIFICATION.md. Passing PR CI alone does not complete the external blockers.
