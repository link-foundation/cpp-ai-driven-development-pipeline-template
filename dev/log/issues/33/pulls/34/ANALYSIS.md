# Issue 33 analysis, decisions and evidence

## Scope and requirement inventory

The complete issue, its one initial comment, PR conversation, inline comments,
reviews and sub-issue endpoint are saved alongside this file. No required
sub-issues or screenshots were present. [PLAN.md](PLAN.md) maps every issue
requirement and the additional execution requirements to implementation and
verification. The branch begins after PR 32 and the earlier full dependency
migration in PR 31; their historical evidence stays unchanged.

## Default-branch investigation

The issue comment's observed main runs were checked by SHA and creation time,
not inferred from stale PR checks. Docs and CI/CD passed at main commit
657ef4059bb0fdf86cd03fa1124ca178859c8fb5. Security run
[43623795378](https://github.com/link-foundation/cpp-ai-driven-development-pipeline-template/actions/runs/43623795378)
failed only its native dependency audit and terminal status gate.
The complete log is `ci-logs/security-main-43623795378.log`:
line 5050 reports `Native audit credentials unavailable` and the missing
`CONAN_AUDIT_PROVIDER_TOKEN_CONANCENTER`; line 5051 records exit 1.
This credential prerequisite also failed before PR 32 and is not a new
compiler, parser or deprecation regression from that merge. Other main
workflows were successful (`research/main-runs-initial.json`).

[Conan's supported audit service](https://docs.conan.io/2/devops/audit.html)
requires registration and a provider token. The repository's secret-name
listing was empty. A usable token cannot be derived from source or a GitHub
credential. Existing audit code already resolves FetchContent, CPM, Conan
and vcpkg, retains SBOM/coordinates on missing credentials, warns on PRs,
and fails main/scheduled/manual runs with the exact setup action. Findings,
unknown coordinates, authentication failures and malformed reports fail on
all events. Existing mocked regressions exercise these paths for both Conan
graph layouts; the full script suite passes. No gate was weakened.

Unfinished criterion: main cannot become green and the native advisory audit
cannot be completed until the registered provider token is configured as that
repository secret. Main is not modified or merged by this PR. After configuring
the secret, rerun Security on main and the PR and inspect the complete report.

## vcpkg update and downgrade prevention

PR 32 selected monthly release 2026.10.16 at baseline 9eec002, which carries
vcpkg-tool 2026-09-26. The current registry head 4702e381 is 471 commits ahead
and carries the latest tool 2026-10-29, with platform hashes in upstream metadata.
Updating to that head advances the merged dependency and restores current tooling;
it does not revert the merged update. CI reads the baseline from `vcpkg.json`
for checkout, bootstrap, consumer builds and audit resolution.

The newest Dependabot vcpkg checker compares SHA inequality against the latest
monthly tag without checking ancestry. Source and GitHub compare responses are
saved in `research/`. The narrow `<=2026.10.16` exclusion prevents the known
backward update and leaves future monthly releases eligible. The upstream
proposal adds ancestry checks and tests for older/equal/newer/divergent commits:
[dependabot-core issue 16938](https://github.com/dependabot/dependabot-core/issues/16938).

The registry's Benchmark port remains 1.9.5. Keep the existing tested 1.10.0
overlay and its corrected feature forwarding until the upstream port is released;
GoogleTest and helper-port versions are already current. The full native matrix
must verify Linux/macOS/Windows, sanitizers, benchmark and all consumer paths.

## Major npm migration and removal of obsolete upstream logic

The only newly available transitive major is rc-config-loader 4.1.4 to 5.0.0.
Read the upstream [release and migration guide](https://github.com/azu/rc-config-loader/releases/tag/v5.0.0)
and current README, saved in `research/rc-config-loader-*`. Node >=22.18 is
required; this repository already pins 26.13.1. Version 5 loads ESM and erasable
TypeScript through Node, unwraps default exports upstream, stops retaining loaded
modules, uses js-yaml 5, and removes its require-from-string loader. No local
module-loading or default-export shim is necessary. Ajv still depends on
require-from-string, so the overall scanner tree remains 76 entries.

The removed `defaultExtension` option is not used by Secretlint's loader.
Default extension search now covers JSON/YAML/JS/TS with JSON taking precedence;
auto-discovered `.cjs` is no longer an upstream default. Explicit CommonJS,
ESM and TypeScript paths work and are documented. The repository's existing
JSON config and YAML regression retain their behavior. A parent-range request
records these compatibility considerations upstream:
[secretlint issue 1836](https://github.com/secretlint/secretlint/issues/1836).

Reproduction: run `node --test scripts/test_secretlint.mjs` with the original
rc-config-loader 4.1.4 tree and the three new configuration cases. CommonJS
passes, while ESM and TypeScript fail (18 pass / 2 fail overall). With 5.0.0,
all 20 cases pass, followed by the full repository secrets scan. Synthetic
fixtures are bounded, scanner subprocesses have 15-second limits, and tests
verify findings survive loading rather than merely accepting exit 0.
`research/rc-loader-before.log` and `npm-test-after.log` retain both outcomes.

All other overrides are still required by published parent ranges. In particular,
Secretlint's chalk removal is only on upstream main, and textlint still requires
older js-yaml, so neither override can yet be removed. Upstream issue statuses
and full discussions were refreshed before retaining these workarounds.

## Resolutions, updater coverage and alternatives researched

[DEPENDENCIES.md](DEPENDENCIES.md) links every before/final/latest table and
records every distribution exception. Python direct and transitive versions,
hooks, Actions, official Node/.NET indexes, container digest and native registry
metadata were queried live. No stale floors or conflicting active pins were found
beyond the npm engine floor, now raised to 12.2.2. Python locks regenerated without
version changes. No pyproject or managed TargetFramework exists to update.

| Requirement / gap | Existing component and possible solution | Selected plan and reason |
| --- | --- | --- |
| Cross-platform Python resolution | [uv universal compilation](https://docs.astral.sh/uv/pip/compile/), pip-tools, Poetry project lock | Keep pinned uv and shared requirements constraints; universal resolution already covers all supported platforms without introducing a second project model |
| npm direct majors and transitive graph | [npm-check-updates](https://github.com/raineorshine/npm-check-updates), npm lock/overrides, Secretlint upstream ranges | Run ncu, refresh lock, adopt current majors with end-to-end scanner checks; remove each override when the published parent supports it |
| Automatic SDK and manifest updates | [Dependabot supported ecosystems](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories) includes dotnet-sdk, pip, npm, pre-commit, Actions and vcpkg | Keep the existing updater and add missing global.json coverage; no NuGet dependency manifest exists, so do not add a nonfunctional NuGet entry |
| Arbitrary CMake/CPM/Doxygen literals | [Renovate regex managers](https://docs.renovatebot.com/modules/manager/regex/) and [git-refs datasource](https://docs.renovatebot.com/modules/datasource/git-refs/) can cover literal pins | Periodically query their official releases in the retained experiment; a second bot/account migration is unnecessary for this dependency refresh |
| Native advisory coverage | Conan Audit provider, CycloneDX inventory, OSV databases | Retain supported Conan graph/provider integration and complete coordinates; OSV alone cannot certify Conan/vcpkg coverage or replace missing authentication |
| Latest CMake binary across OSes | Existing lukka/get-cmake, PyPI wheel, Conan build-tool package | Keep checksum-verified upstream CMake 4.5.0; PyPI and Conan lag and must not downgrade CI |
| Compiler/tool publication lag | Current GA hosted images, source builds, third-party compiler repositories | Keep supported vendor images and explicitly report lag; rebuilding/mixing OS toolchains would add unrequested maintenance and cannot make upstream distributions publish missing versions |
| Missing native audit credential | Configure the free registered provider token, or disable the gate | Credential configuration is required; disabling the audit would violate the security acceptance criterion |

The linked dependency-update practices were read; a byte-for-byte source copy
is in `research/dependency-update-best-practices.md.txt`. Major migration notes
from the previous same-day update remain in issue 30 evidence; only rc-config-loader
crosses a major in this PR. No obsolete local shim had a newly released replacement;
this update removes the loader's old upstream loader path through the new release.

## Audits and remaining external limits

Python strict pip-audit reports no findings or coverage gaps; the complete npm
scanner lock audit reports zero findings. These results do not describe the npm
CLI's separate distribution. A fresh audit of the current published npm 12.2.2
bundle reports 21 moderate entries originating from two advisory families:
[glob cancellation](https://github.com/advisories/GHSA-3g3m-2fjr-6pw4) and
[minimatch amplification](https://github.com/advisories/GHSA-g3hv-75wg-m249).
The earlier [npm issue 10299](https://github.com/npm/cli/issues/10299) remains open.
Root scanner overrides cannot replace npm's bundled packages; editing the installed
CLI would produce a private fork instead of the requested current published release.
The bundle table records every lagging package's upstream distribution constraint.

The zero-advisory criterion and literal latest upstream toolchain criterion are
unfinished. Conan Center CMake, clang-tidy wheels and hosted compilers also lag
their upstream releases; evidence and existing reports are linked in the inventory
and [UPSTREAM.md](UPSTREAM.md). No skipped test or relaxed constraint disguises
these limits. The PR remains unmerged.
