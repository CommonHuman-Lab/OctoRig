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
  | "parchment";

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

export const THEMES: Theme[] = [
  {
    id: "nightfall",
    name: "Nightfall",
    hint: "Deep void · Emerald · OctoRig",
    preview: { bg: "#020c09", surface: "rgba(16,185,129,0.07)", border: "rgba(16,185,129,0.18)", accent: "#10b981", text: "#f0fff8", dim: "#4e7568" },
  },
  {
    id: "obsidian",
    name: "Obsidian",
    hint: "Pure black · Cyan · Terminal sharp",
    preview: { bg: "#030303", surface: "rgba(6,182,212,0.06)", border: "rgba(6,182,212,0.20)", accent: "#22d3ee", text: "#f0feff", dim: "#0891b2" },
  },
  {
    id: "crimson",
    name: "Crimson",
    hint: "Dark blood · Rose · Aggressive",
    preview: { bg: "#0c0408", surface: "rgba(244,63,94,0.06)", border: "rgba(244,63,94,0.20)", accent: "#f43f5e", text: "#fff1f2", dim: "#881337" },
  },
  {
    id: "matrix",
    name: "Matrix",
    hint: "Void black · Emerald · Classic hacker",
    preview: { bg: "#000100", surface: "rgba(34,197,94,0.05)", border: "rgba(34,197,94,0.22)", accent: "#22c55e", text: "#f0fdf4", dim: "#15803d" },
  },
  {
    id: "nord",
    name: "Nord",
    hint: "Slate blue · Arctic sky · Calm",
    preview: { bg: "#0d1220", surface: "rgba(136,192,208,0.06)", border: "rgba(136,192,208,0.17)", accent: "#88c0d0", text: "#eceff4", dim: "#5e7290" },
  },
  {
    id: "unicorn",
    name: "Unicorn",
    hint: "Violet night · Vivid fuchsia · Rainbow",
    preview: { bg: "#0c0618", surface: "rgba(168,85,247,0.08)", border: "rgba(217,70,239,0.22)", accent: "#d946ef", text: "#fae8ff", dim: "#a21caf" },
  },
  {
    id: "dracula",
    name: "Dracula",
    hint: "Slate purple · Lavender · Classic vampire",
    preview: { bg: "#282a36", surface: "rgba(189,147,249,0.06)", border: "rgba(189,147,249,0.20)", accent: "#bd93f9", text: "#f8f8f2", dim: "#6272a4" },
  },
  {
    id: "gruvbox",
    name: "Gruvbox",
    hint: "Warm olive · Burnt orange · Retro terminal",
    preview: { bg: "#282828", surface: "rgba(254,128,25,0.06)", border: "rgba(254,128,25,0.20)", accent: "#fe8019", text: "#ebdbb2", dim: "#a89984" },
  },
  {
    id: "parchment",
    name: "Parchment",
    hint: "Warm cream · Forest emerald · Paper & ink",
    preview: { bg: "#f4ecdc", surface: "rgba(15,122,92,0.06)", border: "rgba(58,52,43,0.16)", accent: "#0f7a5c", text: "#3a342b", dim: "#8a8068" },
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
    "parchment",
  ].includes(v);
}

export function getTheme(id: ThemeId): Theme {
  return THEMES.find((t) => t.id === id) ?? THEMES[0];
}
