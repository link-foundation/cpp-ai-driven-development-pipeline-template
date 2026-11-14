# Scanner transitive major migrations

The scanner previously ran through unlocked npx, with no reproducible tree.
The first fresh resolution exposed the older versions below. Registry metadata
and full upstream release notes are saved in `raw/npm-major-migrations.json`;
the final per-package resolution is in [NPM-LOCK.md](NPM-LOCK.md).

Node 26.13.1 satisfies the newer Node 22 floors and synchronous ESM imports.
The repository's own test module uses native ESM. No import compatibility layer
is added. `npm test` checks all eleven console formatters with a synthetic
finding, both positive/negative scanner exits, YAML parsing, fatal configuration
errors, Babel code frames, package/license normalization and JSON Schema URI
resolution. These check the paths affected by the dependency API changes.

| Dependency | First resolution | Latest selected | Reviewed changes / application |
| --- | --- | --- | --- |
| @babel/code-frame | 7.29.7 | 8.0.6 | [Babel 8 migration](https://babeljs.io/docs/v8-migration): ESM, Node ^22.18 / >=24.11; named codeFrameColumns API remains; diagnostic test exercises it |
| @babel/helper-validator-identifier | 7.29.7 | 8.0.6 | Same Babel migration; selected by code-frame 8's native range |
| ansi-regex | 5.0.1 | 6.6.0 | [6 release](https://github.com/chalk/ansi-regex/releases/tag/v6.0.0): pure ESM, Node 12 floor; current strip-ansi brings it naturally |
| ansi-styles | 4.3.0 | removed | Latest 7 requires Node 22; newer Chalk/slicing implementations remove this legacy subtree |
| argparse | 2.0.1 | 3.0.4 | [Migration snapshot](raw/argparse-migration.txt): remove v1 camelCase aliases/type:auto. New js-yaml uses current API; no direct argparse caller here |
| chalk | 5.6.2 | 6.0.1 | [6 release](https://github.com/chalk/chalk/releases/tag/v6.0.0): Node 22, updated color handling; tested scanner formatting |
| color-convert | 2.0.1 | removed | [3 release](https://github.com/Qix-/color-convert/releases/tag/3.0.0): ESM; native newer formatting removes this legacy subtree |
| color-name | 1.1.4 | removed | [2 release](https://github.com/colorjs/color-name/releases/tag/v2.0.0): ESM; removed with old color-convert |
| emoji-regex | 8.0.0 | removed | Upstream has no GitHub release notes; newer string-width uses its upstream grapheme implementation and removes this subtree |
| fast-uri | 3.1.9 | 4.2.3 | [4 release](https://github.com/fastify/fast-uri/releases/tag/v4.0.0): deprecated types removed, escape fix; Ajv schema URI test checks resolution |
| hosted-git-info | 9.0.3 | 10.1.1 | [10 release](https://github.com/npm/hosted-git-info/releases/tag/v10.0.0): raised Node floor; selected by new normalize-package-data |
| is-fullwidth-code-point | 3.0.0 | removed | [5 release](https://github.com/sindresorhus/is-fullwidth-code-point/releases/tag/v5.0.0): newer Unicode data; newer grapheme-aware width/slicing removes this subtree |
| js-tokens | 4.0.0 | 10.0.0 | [Complete changelog](raw/js-tokens-changelog.txt): regex-to-tokenizer API changed at 6, ESM at 10. Babel 8 uses current tokenizer natively; old Babel code is removed |
| js-yaml | 4.3.2 | 5.5.0 | [Migration snapshot](raw/js-yaml-migration.txt): named/namespace imports, CORE_SCHEMA, empty input errors, AST API changes. Loader uses load without legacy custom types; valid/invalid YAML tests pass |
| normalize-package-data | 8.0.0 | 9.0.0 | [9 release](https://github.com/npm/normalize-package-data/releases/tag/v9.0.0): Node ^22.22.2 / ^24.15 / >=26; read-pkg normalization test passes |
| pluralize | 2.0.0 | 8.0.0 | [8 notes](https://github.com/plurals/pluralize/releases/tag/v8.0.0): updated word rules; formatter's error/warning counts retain correct singular/plural output |
| slice-ansi | 4.0.0 | 10.0.1 | [10 notes](https://github.com/chalk/slice-ansi/releases/tag/v10.0.0): grapheme widths and trailing halfwidth columns; no snapshot assumes old spacing; table reporting checked |
| spdx-expression-parse | 3.0.1 | 5.0.0 | Upstream publishes no changelog/migration guide; current README retains parse(string) object API; MIT normalization and invalid schema input are tested |
| string-width | 4.2.3 | 9.0.0 | [9 notes](https://github.com/sindresorhus/string-width/releases/tag/v9.0.0): Node 22, updated Unicode/grapheme handling; native implementation removes old hand-built width subtree |
| strip-ansi | 6.0.1 | 7.2.0 | [7 notes](https://github.com/chalk/strip-ansi/releases/tag/v7.0.0): ESM/Node 12; current Node imports successfully; all formatters exercised |
| supports-color | 10.2.2 | 11.0.0 | [11 notes](https://github.com/chalk/supports-color/releases/tag/v11.0.0): Node 22, FORCE_COLOR semantics; new supports-hyperlinks selects it naturally |
| supports-hyperlinks | 4.6.0 | 5.0.0 | [5 notes](https://github.com/chalk/supports-hyperlinks/releases/tag/v5.0.0): Node 22, new terminal support; terminal-link API usage remains valid |
| type-fest | 4.41.0 | 5.10.0 | [5 notes](https://github.com/sindresorhus/type-fest/releases/tag/v5.0.0): ESM/Node 20, TypeScript 5.9, renamed/stricter type helpers; repository has no TypeScript compilation or direct helper use |

The twelve necessary root overrides in package.json are temporary range fixes
for current upstream parents; all other newer versions now follow their native
ranges. They do not patch vendored source or alter failure handling. Remove an
override when the corresponding upstream parent publishes a supporting range.
The npm CLI bundle is separate: consumer overrides cannot repair its advisories.
