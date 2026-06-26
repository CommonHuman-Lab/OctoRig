// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
//
// check-i18n-parity.mjs — verify messages/en/<ns>.json and messages/fr/<ns>.json
// stay in sync: same namespace files, same keys, same {placeholder} tokens.
//
// Usage: node scripts/check-i18n-parity.mjs

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const MESSAGES_DIR = path.join(SCRIPT_DIR, "..", "messages");

function flatten(obj, prefix = "") {
  const out = {};
  for (const [key, value] of Object.entries(obj)) {
    const p = prefix ? `${prefix}.${key}` : key;
    if (typeof value === "string") out[p] = value;
    else if (typeof value === "object" && value !== null) Object.assign(out, flatten(value, p));
  }
  return out;
}

function placeholders(value) {
  // Only ICU argument openers: `{name,` or `{name}` — not literal text that happens to start with `{`.
  return new Set([...value.matchAll(/\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*[,}]/g)].map((m) => m[1]));
}

function setDiff(a, b) {
  return [...a].filter((x) => !b.has(x));
}

let hasErrors = false;
function fail(msg) {
  console.error(msg);
  hasErrors = true;
}

const enDir = path.join(MESSAGES_DIR, "en");
const frDir = path.join(MESSAGES_DIR, "fr");

const enFiles = new Set(fs.readdirSync(enDir).filter((f) => f.endsWith(".json")));
const frFiles = new Set(fs.readdirSync(frDir).filter((f) => f.endsWith(".json")));

for (const f of setDiff(enFiles, frFiles)) fail(`[${f}] present in en/ but missing from fr/`);
for (const f of setDiff(frFiles, enFiles)) fail(`[${f}] present in fr/ but missing from en/`);

for (const file of [...enFiles].filter((f) => frFiles.has(f))) {
  const ns = file.replace(/\.json$/, "");
  const en = flatten(JSON.parse(fs.readFileSync(path.join(enDir, file), "utf8")));
  const fr = flatten(JSON.parse(fs.readFileSync(path.join(frDir, file), "utf8")));
  const enKeys = new Set(Object.keys(en));
  const frKeys = new Set(Object.keys(fr));

  for (const k of setDiff(enKeys, frKeys)) fail(`[${ns}] missing in fr: ${k}`);
  for (const k of setDiff(frKeys, enKeys)) fail(`[${ns}] orphaned in fr (no en key): ${k}`);

  for (const k of [...enKeys].filter((x) => frKeys.has(x))) {
    const enPh = placeholders(en[k]);
    const frPh = placeholders(fr[k]);
    const missing = setDiff(enPh, frPh);
    const extra = setDiff(frPh, enPh);
    if (missing.length) fail(`[${ns}] ${k}: fr is missing placeholder(s) ${missing.join(", ")}`);
    if (extra.length) fail(`[${ns}] ${k}: fr has extra placeholder(s) ${extra.join(", ")}`);
  }
}

if (hasErrors) {
  console.error("\ni18n parity check failed.");
  process.exit(1);
}
console.log("i18n parity check passed: en/ and fr/ namespace files match.");
