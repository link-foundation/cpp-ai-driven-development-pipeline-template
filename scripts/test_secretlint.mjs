import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { after, test } from "node:test";

// Synthetic content only: exercise detection and formatting after major updates
// without storing a credential or scanning an unbounded input.
mkdirSync("build", { recursive: true });
const scratch = mkdtempSync(resolve("build/secretlint-test-"));
after(() => rmSync(scratch, { recursive: true, force: true }));
const clean = join(scratch, "clean.txt");
const finding = join(scratch, "finding.txt");
writeFileSync(clean, "No credentials here.\n");
writeFileSync(finding, "-----BEGIN " + "PRIVATE KEY-----\nMI" + "a".repeat(118)
  + "\n-----END " + "PRIVATE KEY-----\n");
const scan = (...args) => spawnSync(process.execPath,
  ["node_modules/secretlint/bin/secretlint.js", "--no-gitignore", ...args],
  { encoding: "utf8", timeout: 15000, maxBuffer: 1024 * 1024 });

test("clean content passes", () => {
  const result = scan(clean);
  assert.equal(result.status, 0, result.stderr);
});

for (const format of ["checkstyle", "compact", "github", "jslint-xml", "junit",
  "pretty-error", "stylish", "tap", "unix", "json", "table"]) {
  test(`${format} reports a finding and preserves the failure status`, () => {
    const result = scan(finding, "--format", format);
    assert.equal(result.status, 1, result.stderr);
    assert.ok(result.stdout.length > 0);
    // JSON and pretty-error intentionally include source context. Check the
    // masked diagnostic itself in JSON, and the default console output below.
    if (format === "json") {
      const message = JSON.parse(result.stdout)[0].messages[0];
      assert.equal(message.data.KEY.includes("MI" + "a".repeat(118)), false);
    }
    if (format === "stylish") {
      assert.equal(result.stdout.includes("MI" + "a".repeat(118)), false);
    }
  });
}

test("YAML configuration loads with the updated parser", () => {
  const config = join(scratch, ".secretlintrc.yml");
  writeFileSync(config, "rules:\n  - id: '@secretlint/secretlint-rule-preset-recommend'\n");
  const result = scan(finding, "--secretlintrc", config, "--format", "json");
  assert.equal(result.status, 1, result.stderr);
  assert.equal(JSON.parse(result.stdout)[0].messages[0].messageId, "PrivateKey");
});

test("malformed configuration remains a fatal error", () => {
  const config = join(scratch, "invalid.yml");
  writeFileSync(config, "rules: [\n");
  const result = scan(clean, "--secretlintrc", config);
  assert.equal(result.status, 2, result.stderr);
});

test("invalid JSON retains the Babel code-frame diagnostic", async () => {
  const { default: parseJson } = await import("parse-json");
  assert.throws(() => parseJson('{"rules": [],}'), error => {
    assert.match(error.message, /JSON|Unexpected|Expected/);
    assert.doesNotMatch(error.message, /TypeError|is not a function/);
    assert.ok(error.codeFrame.includes('"rules"'));
    return true;
  });
});

test("package metadata and SPDX normalization still accept an MIT package", async () => {
  const { readPackage } = await import("read-pkg");
  writeFileSync(join(scratch, "package.json"), JSON.stringify({
    name: "dependency-migration-fixture", version: "1.0.0", license: "MIT",
    repository: "https://github.com/secretlint/secretlint",
  }));
  const result = await readPackage({ cwd: scratch, normalize: true });
  assert.equal(result.license, "MIT");
  assert.equal(result.repository.type, "git");
});

test("schema URI resolution retains validation and rejection", async () => {
  const { default: Ajv } = await import("ajv");
  const ajv = new Ajv();
  ajv.addSchema({ $id: "https://example.invalid/schema/value", type: "integer" });
  const validate = ajv.compile({
    $id: "https://example.invalid/schema/root",
    type: "object", properties: { value: { $ref: "value" } }, required: ["value"],
  });
  assert.equal(validate({ value: 1 }), true);
  assert.equal(validate({ value: "wrong type" }), false);
});
