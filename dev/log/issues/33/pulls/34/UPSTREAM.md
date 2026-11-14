# Upstream findings and current status

Searched existing reports before posting. Full bodies and discussions for the
20 earlier reports were refreshed into `research/upstream/`; the summary retains
state and URLs. Same-day unchanged evidence was not posted repeatedly.

## New reports from this investigation

| Dependency | Minimal reproducer, proposal and local handling | Report |
| --- | --- | --- |
| Dependabot vcpkg updater | Start from registry commit 4702e381; latest monthly tag 2026.10.16 is 471 commits behind. SHA inequality alone proposes a downgrade, including tool 2026-10-29 to 2026-09-26. Compare ancestry before creating an update; add older/equal/newer/divergent tests. Keep a narrow older-tag exclusion locally. | [dependabot-core 16938](https://github.com/dependabot/dependabot-core/issues/16938) |
| Secretlint 13.1.0 config loader | Parent range retains rc-config-loader 4; ESM/TS fixtures fail there and pass with 5.0.0 on supported Node. Adopt v5's native loading, remove any obsolete defaultExtension use, and explicitly preserve/document discovery priority and CJS behavior. Keep tested root override until publication. | [secretlint 1836](https://github.com/secretlint/secretlint/issues/1836) |

Exact submitted bodies, searched issue lists and resulting URLs are in
`research/{dependabot,secretlint}-report*` and the matching issue-search JSON files.

## Existing reports rechecked

| Dependency / workaround | Current evidence and proposed upstream resolution | Report |
| --- | --- | --- |
| npm CLI | Current 12.2.2 bundle still has 21 moderate audit entries from glob/minimatch. Rebuild distribution with patched majors; root project overrides cannot alter it. | [npm/cli 10299](https://github.com/npm/cli/issues/10299), open |
| vcpkg Benchmark | Registry head still has 1.9.5. Existing 1.10.0 overlay and feature-forwarding correction remain necessary; publish official version/hash/database update and forward generated CMake options. | [microsoft/vcpkg 55056](https://github.com/microsoft/vcpkg/issues/55056), open |
| clang-tidy wheel | Wheel 23.1.4 is still latest despite LLVM 23.1.5. Publish current platform wheels and smoke-test them. | [ssciwr/clang-tidy-wheel 133](https://github.com/ssciwr/clang-tidy-wheel/issues/133), open |
| Conan Center CMake | conandata still tops out at 4.4.4; upstream binary is 4.5.0. Merge/publish the existing recipe update. | [conan-center-index PR 31443](https://github.com/conan-io/conan-center-index/pull/31443), open |
| actionlint queue syntax | 1.7.12 still lacks queue semantics; narrow validated adapter remains until parser support. | [issue 657](https://github.com/rhysd/actionlint/issues/657), [parser PR 654](https://github.com/rhysd/actionlint/pull/654), open |
| actionlint runner labels | 1.7.12 does not recognize ubuntu-26.04; retain explicit valid runner configuration. | [issue 682](https://github.com/rhysd/actionlint/issues/682), open |
| lychee connect retry | Current 0.24.2 does not retry connect-phase reset; retain bounded retry of transport failures only, with permanent-status regression checks. | [lychee 2297](https://github.com/lycheeverse/lychee/issues/2297), open |
| rc-config-loader js-yaml | Version 5 now supports js-yaml 5 and native ESM/TS. Adopted here; no loader-specific YAML compatibility shim is needed. Other parents still require the root YAML override. | [rc-config-loader 30](https://github.com/azu/rc-config-loader/issues/30), closed |
| Secretlint formatter chalk | Chalk removed on upstream main, but latest published Secretlint 13.1.0 still has the old range. Keep override until an actual release. | [secretlint 1831](https://github.com/secretlint/secretlint/issues/1831), closed, unreleased change |
| textlint formatter | Published ranges still constrain js-yaml, pluralize, string-width and strip-ansi. Widen ranges and supported engines with formatter tests; retain overrides. | [textlint 2179](https://github.com/textlint/textlint/issues/2179), open |
| parse-json | Published ranges still constrain Babel code-frame and type-fest. Adopt current APIs/engines; keep code-frame regression and overrides. | [parse-json 54](https://github.com/sindresorhus/parse-json/issues/54), open |
| table | Published ranges constrain slice-ansi, string-width and strip-ansi. Adopt current majors/engines; table formatter regression passes with overrides. | [table 246](https://github.com/gajus/table/issues/246), open |
| spdx-correct | Published range constrains spdx-expression-parse. Update range with license-normalization regression. | [spdx-correct 46](https://github.com/jslicense/spdx-correct.js/issues/46), open |
| validate-npm-package-license | Same parser range gap; keep override with metadata/license test. | [validate-npm-package-license 16](https://github.com/kemitchell/validate-npm-package-license.js/issues/16), open |
| terminal-link | Published range constrains supports-hyperlinks. Adopt current major with Node floor; formatter regressions pass. | [terminal-link 29](https://github.com/sindresorhus/terminal-link/issues/29), open |
| read-pkg | Published range constrains normalize-package-data. Upgrade range/API with package metadata checks; retain override. | [read-pkg 35](https://github.com/sindresorhus/read-pkg/issues/35), open |
| Ajv | Published range constrains fast-uri. Adopt current range with valid/invalid URI-reference tests; retain override. | [ajv 2705](https://github.com/ajv-validator/ajv/issues/2705), open |
| Old CMake action | Older HTTP/tool-cache emitted DEP0169. Prior PR already replaced this action throughout with current lukka/get-cmake; no active dependency remains. | [actions-setup-cmake 97](https://github.com/jwlawson/actions-setup-cmake/issues/97), open, local workaround removed earlier |
| zizmor action | Current 0.8.1 supports current tool hashes; native action already replaces former pipx wrappers. | [zizmor-action 175](https://github.com/zizmorcore/zizmor-action/issues/175), merged |
| Cppcheck wheel | Wheel 1.5.3 ships native 2.22.0. Prior PR corrected the mistaken version comment; no remaining gap. | [cppcheck-wheel PR 197](https://github.com/msclock/cppcheck-wheel/pull/197), merged |

Conan Audit token setup is an account prerequisite, not an upstream software bug.
No report asks maintainers to bypass authentication. Hosted image compiler lag is
a distribution constraint recorded in the inventory, not a reproducible compiler
bug requiring a speculative upstream report.
