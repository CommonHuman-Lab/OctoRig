#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
#
# make-demo-content.sh — single entry point that chains the screenshot/gif
# scripts in this directory into the two demo-content flows. All output (raw
# screenshots, gifs, the slices jpg) is written under ./content/, next to
# this script, so the whole batch of generated material lives in one place:
#
#   demo   screenshot-demo.mjs   -> screenshots-to-gif.mjs   -> content/demo.gif (non-admin pages)
#                                -> screenshots-to-gif.mjs   -> content/demo-admin.gif (admin pages)
#   themes screenshot-themes.mjs -> screenshots-to-gif.mjs   -> content/themes.gif
#                                -> screenshot-themes-slices.mjs -> content/themes-slices.jpg
#
# Usage:
#   ./scripts/make-demo-content.sh            # run both flows
#   ./scripts/make-demo-content.sh demo       # just the page-by-page demo gif
#   ./scripts/make-demo-content.sh themes     # just the themes gif + slices jpg
#
# Requires the platform stack running at BASE_URL, playwright (npx playwright
# install chromium) and ffmpeg/ffprobe on PATH. Env vars BASE_URL,
# ADMIN_USERNAME, ADMIN_PASSWORD are forwarded to the screenshot scripts as-is.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CONTENT_DIR="$SCRIPT_DIR/content"
mkdir -p "$CONTENT_DIR"

MODE="${1:-all}"

run_demo() {
  echo "==> [demo] capturing page screenshots"
  OUT_DIR="$CONTENT_DIR/screenshots" node screenshot-demo.mjs

  echo "==> [demo] stitching demo.gif (non-admin pages)"
  IN_DIR="$CONTENT_DIR/screenshots" OUT_FILE="$CONTENT_DIR/demo.gif" SKIP="admin,after-login,settings-demo-on,team-detail,challenge-detail" \
    FADE_MS="${FADE_MS:-450}" LOOP_FADE="${LOOP_FADE:-1}" FIRST_HOLD_MS="${FIRST_HOLD_MS:-${HOLD_MS:-1100}}" LAST_HOLD_MS="${LAST_HOLD_MS:-${HOLD_MS:-1100}}" \
    node screenshots-to-gif.mjs

  echo "==> [demo] stitching demo-admin.gif (admin pages)"
  IN_DIR="$CONTENT_DIR/screenshots" OUT_FILE="$CONTENT_DIR/demo-admin.gif" ONLY="admin" \
    FADE_MS="${FADE_MS:-450}" LOOP_FADE="${LOOP_FADE:-1}" FIRST_HOLD_MS="${FIRST_HOLD_MS:-${HOLD_MS:-1100}}" LAST_HOLD_MS="${LAST_HOLD_MS:-${HOLD_MS:-1100}}" \
    node screenshots-to-gif.mjs
}

run_themes() {
  echo "==> [themes] capturing per-theme screenshots"
  OUT_DIR="$CONTENT_DIR/themes" node screenshot-themes.mjs
  echo "==> [themes] stitching themes.gif"
  IN_DIR="$CONTENT_DIR/themes" OUT_FILE="$CONTENT_DIR/themes.gif" FADE_MS="${FADE_MS:-450}" LOOP_FADE="${LOOP_FADE:-1}" FIRST_HOLD_MS="${FIRST_HOLD_MS:-${HOLD_MS:-1100}}" LAST_HOLD_MS="${LAST_HOLD_MS:-${HOLD_MS:-1100}}" node screenshots-to-gif.mjs
  echo "==> [themes] building themes-slices.jpg"
  IN_DIR="$CONTENT_DIR/themes" OUT_FILE="$CONTENT_DIR/themes-slices.jpg" node screenshot-themes-slices.mjs
}

case "$MODE" in
  demo)
    run_demo
    ;;
  themes)
    run_themes
    ;;
  all)
    run_demo
    run_themes
    ;;
  *)
    echo "Usage: $0 [demo|themes|all]" >&2
    exit 1
    ;;
esac

echo "==> Done."
