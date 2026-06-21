// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

export type ThemeId =
  | "nightfall"
  | "obsidian"
  | "crimson"
  | "matrix"
  | "nord"
  | "unicorn"
  | "dracula"
  | "gruvbox"
  | "folio"
  | "tokyo"
  | "catppuccin"
  | "synthwave"
  | "rose"
  | "frost";

export interface Theme {
  id: ThemeId;
  name: string;
  hint: string;
  preview: {
    bg: string;
    surface: string;
    border: string;
    accent: string;
    text: string;
    dim: string;
  };
}

// Sorted a-z by name — this is the order the theme pickers render in.
export const THEMES: Theme[] = [
  {
    id: "catppuccin",
    name: "Catppuccin",
    hint: "Warm dark · Pastel mauve · Soft & calm",
    preview: { bg: "#1e1e2e", surface: "rgba(203,166,247,0.06)", border: "rgba(203,166,247,0.20)", accent: "#cba6f7", text: "#cdd6f4", dim: "#6c7086" },
  },
  {
    id: "crimson",
    name: "Crimson",
    hint: "Dark blood · Rose · Aggressive",
    preview: { bg: "#0c0408", surface: "rgba(244,63,94,0.06)", border: "rgba(244,63,94,0.20)", accent: "#f43f5e", text: "#fff1f2", dim: "#881337" },
  },
  {
    id: "dracula",
    name: "Dracula",
    hint: "Slate purple · Lavender · Classic vampire",
    preview: { bg: "#282a36", surface: "rgba(189,147,249,0.06)", border: "rgba(189,147,249,0.20)", accent: "#bd93f9", text: "#f8f8f2", dim: "#6272a4" },
  },
  {
    id: "folio",
    name: "Folio",
    hint: "Warm cream · Forest emerald · Paper & ink",
    preview: { bg: "#f4ecdc", surface: "rgba(15,122,92,0.06)", border: "rgba(58,52,43,0.16)", accent: "#0f7a5c", text: "#3a342b", dim: "#8a8068" },
  },
  {
    id: "frost",
    name: "Frost",
    hint: "Icy white · Glacier blue · Crisp & clinical",
    preview: { bg: "#eef3f7", surface: "rgba(47,127,209,0.06)", border: "rgba(29,43,58,0.14)", accent: "#2f7fd1", text: "#1d2b3a", dim: "#7c93a5" },
  },
  {
    id: "gruvbox",
    name: "Gruvbox",
    hint: "Warm olive · Burnt orange · Retro terminal",
    preview: { bg: "#282828", surface: "rgba(254,128,25,0.06)", border: "rgba(254,128,25,0.20)", accent: "#fe8019", text: "#ebdbb2", dim: "#a89984" },
  },
  {
    id: "matrix",
    name: "Matrix",
    hint: "Void black · Emerald · Classic hacker",
    preview: { bg: "#000100", surface: "rgba(34,197,94,0.05)", border: "rgba(34,197,94,0.22)", accent: "#22c55e", text: "#f0fdf4", dim: "#15803d" },
  },
  {
    id: "nightfall",
    name: "Nightfall",
    hint: "Deep void · Emerald · OctoRig",
    preview: { bg: "#020c09", surface: "rgba(16,185,129,0.07)", border: "rgba(16,185,129,0.18)", accent: "#10b981", text: "#f0fff8", dim: "#4e7568" },
  },
  {
    id: "nord",
    name: "Nord",
    hint: "Slate blue · Arctic sky · Calm",
    preview: { bg: "#0d1220", surface: "rgba(136,192,208,0.06)", border: "rgba(136,192,208,0.17)", accent: "#88c0d0", text: "#eceff4", dim: "#5e7290" },
  },
  {
    id: "obsidian",
    name: "Obsidian",
    hint: "Pure black · Cyan · Terminal sharp",
    preview: { bg: "#030303", surface: "rgba(6,182,212,0.06)", border: "rgba(6,182,212,0.20)", accent: "#22d3ee", text: "#f0feff", dim: "#0891b2" },
  },
  {
    id: "rose",
    name: "Rosé",
    hint: "Muted charcoal · Dusty rose · Elegant calm",
    preview: { bg: "#191724", surface: "rgba(235,188,186,0.06)", border: "rgba(235,188,186,0.18)", accent: "#ebbcba", text: "#e0def4", dim: "#6e6a86" },
  },
  {
    id: "synthwave",
    name: "Synthwave",
    hint: "Outrun purple · Hot magenta · Neon cyan",
    preview: { bg: "#1a0b2e", surface: "rgba(249,42,173,0.07)", border: "rgba(249,42,173,0.24)", accent: "#f92aad", text: "#fdeff9", dim: "#8b7a9e" },
  },
  {
    id: "tokyo",
    name: "Tokyo",
    hint: "Deep navy · Electric blue · Pro editor",
    preview: { bg: "#1a1b26", surface: "rgba(122,162,247,0.06)", border: "rgba(122,162,247,0.20)", accent: "#7aa2f7", text: "#c0caf5", dim: "#565f89" },
  },
  {
    id: "unicorn",
    name: "Unicorn",
    hint: "Violet night · Vivid fuchsia · Rainbow",
    preview: { bg: "#0c0618", surface: "rgba(168,85,247,0.08)", border: "rgba(217,70,239,0.22)", accent: "#d946ef", text: "#fae8ff", dim: "#a21caf" },
  },
];

export const THEME_STORAGE_KEY = "octorig_theme";

export function isThemeId(v: string): v is ThemeId {
  return [
    "nightfall",
    "obsidian",
    "crimson",
    "matrix",
    "nord",
    "unicorn",
    "dracula",
    "gruvbox",
    "folio",
    "tokyo",
    "catppuccin",
    "synthwave",
    "rose",
    "frost",
  ].includes(v);
}

export function getTheme(id: ThemeId): Theme {
  return THEMES.find((t) => t.id === id) ?? THEMES.find((t) => t.id === "nightfall")!;
}
