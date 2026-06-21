// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
//
// screenshot-url.mjs — log in to the OctoRig platform and screenshot a single
// page, for quick visual checks while iterating on UI changes.
//
// Usage:
//   node scripts/screenshot-url.mjs <path-or-url> [output.png]
//
// Examples:
//   node scripts/screenshot-url.mjs /challenges
//   node scripts/screenshot-url.mjs http://localhost:3000/labs labs.png
//
// Env vars (all optional):
//   BASE_URL        default http://localhost:3000
//   ADMIN_USERNAME  default admin
//   ADMIN_PASSWORD  default change-me   (see platform/.env ADMIN_PASSWORD)
//   FULL_PAGE       default true; set to "false" for viewport-only capture

import { chromium } from "playwright";
import path from "path";
import { fileURLToPath } from "url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));

const BASE_URL = process.env.BASE_URL ?? "http://localhost:3000";
const ADMIN_USERNAME = process.env.ADMIN_USERNAME ?? "admin";
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD ?? "change-me";
const FULL_PAGE = process.env.FULL_PAGE !== "false";

const target = process.argv[2];
if (!target) {
  console.error("Usage: node scripts/screenshot-url.mjs <path-or-url> [output.png]");
  process.exit(1);
}
const url = /^https?:\/\//.test(target) ? target : `${BASE_URL}${target}`;
const outPath = process.argv[3]
  ? path.resolve(process.argv[3])
  : path.join(SCRIPT_DIR, "screenshots", "url-shot.png");

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });

await page.goto(`${BASE_URL}/login`, { waitUntil: "networkidle" }).catch(() => {});
if (await page.locator('input[type="text"]').count() > 0) {
  await page.fill('input[type="text"]', ADMIN_USERNAME);
  await page.fill('input[type="password"]', ADMIN_PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForURL(`${BASE_URL}/`, { timeout: 15000 }).catch(() => {});
}

await page.goto(url, { waitUntil: "networkidle" });
await page.waitForTimeout(600);
await page.screenshot({ path: outPath, fullPage: FULL_PAGE });
await browser.close();

console.log("Saved screenshot to", outPath);
