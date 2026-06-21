// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
//
// screenshot-themes.mjs — log in, enable demo mode, then capture the main
// dashboard once per available UI theme, for README/marketing screenshots.
//
// Usage:
//   1. Make sure the platform stack is running
//   2. Install dependencies once:
//        npm install playwright && npx playwright install chromium
//   3. Run:
//        node scripts/screenshot-themes.mjs
//
// Env vars (all optional):
//   BASE_URL        default http://localhost:3000
//   ADMIN_USERNAME  default admin
//   ADMIN_PASSWORD  default change-me   (see platform/.env ADMIN_PASSWORD)
//   OUT_DIR         default ./themes (next to this script)

import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));

const BASE_URL = process.env.BASE_URL ?? "http://localhost:3000";
const ADMIN_USERNAME = process.env.ADMIN_USERNAME ?? "admin";
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD ?? "change-me";
const OUT = process.env.OUT_DIR ?? path.join(SCRIPT_DIR, "themes");

// Keep in sync with platform/frontend/lib/themes.ts
const THEMES = [
  { id: "nightfall", name: "Nightfall" },
  { id: "obsidian", name: "Obsidian" },
  { id: "crimson", name: "Crimson" },
  { id: "matrix", name: "Matrix" },
  { id: "nord", name: "Nord" },
  { id: "unicorn", name: "Unicorn" },
  { id: "dracula", name: "Dracula" },
  { id: "gruvbox", name: "Gruvbox" },
  { id: "folio", name: "Folio" },
  { id: "tokyo", name: "Tokyo" },
  { id: "catppuccin", name: "Catppuccin" },
  { id: "synthwave", name: "Synthwave" },
  { id: "rose", name: "Rosé" },
  { id: "frost", name: "Frost" },
];

fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
const consoleErrors = [];
page.on("console", (msg) => {
  if (msg.type() === "error") consoleErrors.push(msg.text());
});
page.on("pageerror", (err) => consoleErrors.push("pageerror: " + err.message));

async function shot(name) {
  await page.waitForTimeout(600);
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: true });
  console.log("shot:", name);
}

// Login
await page.goto(`${BASE_URL}/login`);
await page.fill('input[type="text"]', ADMIN_USERNAME);
await page.fill('input[type="password"]', ADMIN_PASSWORD);
await page.click('button[type="submit"]');
await page.waitForURL(`${BASE_URL}/`, { timeout: 15000 }).catch(() => {});

// Enable demo mode: Settings -> Demo tab -> toggle
await page.goto(`${BASE_URL}/settings`);
await page.click('text="Demo"');
await page.waitForTimeout(300);
await page.click("label.demo-toggle");
await page.waitForTimeout(800);

for (const { id, name } of THEMES) {
  // Appearance tab holds the theme switcher
  await page.goto(`${BASE_URL}/settings`, { waitUntil: "networkidle" });
  await page.click('text="Appearance"');
  await page.waitForTimeout(300);
  await page.click(`button.theme-card:has(span:has-text("${name}"))`);
  await page.waitForTimeout(300);

  await page.goto(`${BASE_URL}/`, { waitUntil: "networkidle" }).catch(() => {});
  await shot(id);
}

await browser.close();

fs.writeFileSync(`${OUT}/console-errors.json`, JSON.stringify(consoleErrors, null, 2));
console.log(`\nScreenshots written to ${OUT}`);
console.log("console/page errors:", consoleErrors.length);
if (consoleErrors.length > 0) {
  console.log(consoleErrors.join("\n"));
  process.exit(1);
}
