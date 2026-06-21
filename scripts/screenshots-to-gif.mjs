// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
//
// screenshots-to-gif.mjs — stitch a directory of PNGs into a single looping
// crossfade GIF for the README. Generic over the source directory: point it
// at scripts/screenshots (from screenshot-demo.mjs) for the page-by-page demo
// gif, or at scripts/themes (from screenshot-themes.mjs) for a gif cycling
// through every UI theme.
//
// Usage:
//   1. Run scripts/screenshot-demo.mjs or scripts/screenshot-themes.mjs first
//      to produce the PNGs (./screenshots or ./themes respectively)
//   2. Make sure ffmpeg is on PATH (any 4.3+ build with xfade/palettegen)
//   3. Run:
//        node scripts/screenshots-to-gif.mjs
//        IN_DIR=scripts/themes OUT_FILE=scripts/themes.gif node scripts/screenshots-to-gif.mjs
//
// Env vars (all optional):
//   IN_DIR          default ./screenshots (next to this script)
//   OUT_FILE        default ./demo.gif (next to this script)
//   WIDTH           output pixel width, height auto-scaled; default 960
//   FPS             gif frame rate; default 12
//   HOLD_MS         how long each frame stays fully visible; default 1100
//   FIRST_HOLD_MS   hold time for the first frame; default HOLD_MS * 1.6
//   LAST_HOLD_MS    hold time for the last frame; default HOLD_MS * 1.6
//   FADE_MS         crossfade duration between frames; default 350, set 0 for hard cuts
//   LOOP            gif loop count; default 0 (infinite)
//   DITHER          paletteuse dither algo; default bayer
//   SKIP            comma-separated substrings — drop any filename containing one
//   ONLY            comma-separated substrings — keep only filenames containing one
//   LABELS          "1" to caption each frame with its filename, "0" to disable (default)
//   FONT_FILE       path to a .ttf/.otf used for labels; default a DejaVu Sans Mono
//                   found on the system
//
// Example — drop the login screens, slower pace, hard cuts:
//   SKIP=after-login,settings-demo-on HOLD_MS=1500 FADE_MS=0 node scripts/screenshots-to-gif.mjs
//
// Example — themes gif (files already sort alphabetically: crimson, matrix,
// nightfall, nord, obsidian, unicorn), captioned with theme names:
//   IN_DIR=scripts/themes OUT_FILE=scripts/themes.gif LABELS=1 node scripts/screenshots-to-gif.mjs

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { spawnSync } from "child_process";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));

const IN_DIR = process.env.IN_DIR ?? path.join(SCRIPT_DIR, "screenshots");
const OUT_FILE = process.env.OUT_FILE ?? path.join(SCRIPT_DIR, "demo.gif");
const WIDTH = Number(process.env.WIDTH ?? 960);
const FPS = Number(process.env.FPS ?? 12);
const HOLD_MS = Number(process.env.HOLD_MS ?? 1100);
const FIRST_HOLD_MS = Number(process.env.FIRST_HOLD_MS ?? HOLD_MS * 1.6);
const LAST_HOLD_MS = Number(process.env.LAST_HOLD_MS ?? HOLD_MS * 1.6);
const FADE_MS = Number(process.env.FADE_MS ?? 350);
const LOOP = Number(process.env.LOOP ?? 0);
const DITHER = process.env.DITHER ?? "bayer";
const SKIP = (process.env.SKIP ?? "").split(",").map((s) => s.trim()).filter(Boolean);
const ONLY = (process.env.ONLY ?? "").split(",").map((s) => s.trim()).filter(Boolean);
const LOOP_FADE = (process.env.LOOP_FADE ?? "0") !== "0";
const DUP_HOLD_MS = Number(process.env.DUP_HOLD_MS ?? 0);
const LABELS = (process.env.LABELS ?? "0") !== "0";
const FONT_FILE = process.env.FONT_FILE ?? findFont();

function findFont() {
  const candidates = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
  ];
  return candidates.find((f) => fs.existsSync(f));
}

if (LABELS && !FONT_FILE) {
  console.error("No font found for labels. Set FONT_FILE to a .ttf/.otf path, or LABELS=0 to disable captions.");
  process.exit(1);
}

let files = fs.readdirSync(IN_DIR)
  .filter((f) => f.toLowerCase().endsWith(".png"))
  .sort();

if (ONLY.length > 0) files = files.filter((f) => ONLY.some((s) => f.includes(s)));
if (SKIP.length > 0) files = files.filter((f) => !SKIP.some((s) => f.includes(s)));

if (files.length < 2) {
  console.error(`Need at least 2 PNGs in ${IN_DIR} (found ${files.length}). Run screenshot-demo.mjs first.`);
  process.exit(1);
}

if (LOOP_FADE) files = [...files, files[0]];

console.log(`Frames (${files.length}${LOOP_FADE ? ", last is a loop-fade duplicate of the first" : ""}):`);
files.forEach((f) => console.log("  " + f));

const fadeSec = Math.max(0, FADE_MS) / 1000;
const lastRealIdx = LOOP_FADE ? files.length - 2 : files.length - 1;
const holdSeconds = files.map((_, i) => {
  if (LOOP_FADE && i === files.length - 1) return DUP_HOLD_MS / 1000;
  if (i === 0) return FIRST_HOLD_MS / 1000;
  if (i === lastRealIdx) return LAST_HOLD_MS / 1000;
  return HOLD_MS / 1000;
});
// Each per-image input clip is held fully visible for holdSeconds[i], plus an
// extra fadeSec tail so the next clip has overlap to crossfade into.
const clipLen = holdSeconds.map((h) => h + fadeSec);

const args = ["-y"];
for (let i = 0; i < files.length; i++) {
  args.push("-loop", "1", "-t", clipLen[i].toFixed(3), "-i", path.join(IN_DIR, files[i]));
}

const outHeight = Math.round(WIDTH * 9 / 16); // approximation, only used to size label text

const scaleLabels = [];
let filter = "";
for (let i = 0; i < files.length; i++) {
  const scaled = `v${i}`;
  filter += `[${i}:v]scale=${WIDTH}:-2:flags=lanczos,fps=${FPS},setsar=1[${scaled}];`;
  if (!LABELS) {
    scaleLabels.push(scaled);
    continue;
  }
  const label = `vl${i}`;
  const text = path
    .basename(files[i], path.extname(files[i]))
    .replace(/^\d+[a-z]?-/, "")
    .replace(/[-_]/g, " ")
    .toUpperCase()
    .replace(/'/g, "\\'");
  filter +=
    `[${scaled}]drawtext=fontfile='${FONT_FILE}':text='${text}':` +
    `fontcolor=white:fontsize=${Math.round(outHeight * 0.06)}:` +
    `x=(w-text_w)/2:y=h-text_h-${Math.round(outHeight * 0.03)}:` +
    `box=1:boxcolor=black@0.55:boxborderw=${Math.round(outHeight * 0.02)}[${label}];`;
  scaleLabels.push(label);
}

let voutLabel;
if (fadeSec > 0 && files.length > 1) {
  // Chain xfade across all clips. offsets[i] is the cumulative hold time of
  // every clip before i, i.e. when the transition into clip i begins.
  let prev = scaleLabels[0];
  let cumulative = 0;
  for (let i = 1; i < files.length; i++) {
    cumulative += holdSeconds[i - 1];
    const out = i === files.length - 1 ? "vout" : `vx${i}`;
    filter += `[${prev}][${scaleLabels[i]}]xfade=transition=fade:duration=${fadeSec.toFixed(3)}:offset=${cumulative.toFixed(3)}[${out}];`;
    prev = out;
  }
  voutLabel = "vout";
} else {
  filter += `${scaleLabels.map((l) => `[${l}]`).join("")}concat=n=${files.length}:v=1:a=0[vout];`;
  voutLabel = "vout";
}

filter += `[${voutLabel}]split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=${DITHER}[out]`;

args.push(
  "-filter_complex", filter,
  "-map", "[out]",
  "-loop", String(LOOP),
  OUT_FILE,
);

console.log(`\nRunning ffmpeg -> ${OUT_FILE}`);
const result = spawnSync("ffmpeg", args, { stdio: ["ignore", "inherit", "inherit"] });
if (result.status !== 0) {
  console.error("ffmpeg failed");
  process.exit(result.status ?? 1);
}

const { size } = fs.statSync(OUT_FILE);
console.log(`\nWrote ${OUT_FILE} (${(size / 1024 / 1024).toFixed(2)} MB)`);
