"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { type ThemeId, THEME_STORAGE_KEY, isThemeId } from "@/lib/themes";

interface ThemeState {
  theme: ThemeId;
  _explicit: boolean;
  setTheme: (t: ThemeId) => void;
  applyPlatformDefault: (t: string | null | undefined) => void;
  applyProfileTheme: (t: string | null | undefined) => void;
  resetExplicit: () => void;
}

function applyToDoc(t: ThemeId) {
  if (typeof document !== "undefined") {
    document.documentElement.setAttribute("data-theme", t);
  }
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: "rose",
      _explicit: false,

      setTheme: (theme) => {
        applyToDoc(theme);
        set({ theme, _explicit: true });
      },

      // Only applies if the user has never explicitly chosen a theme
      applyPlatformDefault: (t) => {
        if (get()._explicit || !t || !isThemeId(t)) return;
        applyToDoc(t);
        set({ theme: t });
      },

      // Always applies — user's saved server-side preference wins
      applyProfileTheme: (t) => {
        if (!t || !isThemeId(t)) return;
        applyToDoc(t);
        set({ theme: t, _explicit: true });
      },

      // Called on logout so the next user's profile/platform default takes over
      resetExplicit: () => set({ _explicit: false }),
    }),
    { name: THEME_STORAGE_KEY }
  )
);
