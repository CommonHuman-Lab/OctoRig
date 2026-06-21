// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { ChallengeDifficulty } from "@/lib/api/challenges";

export const DIFF_COLOR: Record<ChallengeDifficulty, string> = {
  easy:   "var(--g-success)",
  medium: "var(--g-warning)",
  hard:   "var(--g-orange)",
  insane: "var(--g-danger)",
};

export const DIFF_CLASS: Record<ChallengeDifficulty, string> = {
  easy:   "g-diff-badge--easy",
  medium: "g-diff-badge--medium",
  hard:   "g-diff-badge--hard",
  insane: "g-diff-badge--insane",
};
