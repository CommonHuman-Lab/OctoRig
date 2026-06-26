"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { createPreferenceStore } from "./createPreferenceStore";
import { type ThemeId, THEME_STORAGE_KEY, isThemeId } from "@/lib/themes";

function applyToDoc(t: ThemeId) {
  if (typeof document !== "undefined") {
    document.documentElement.setAttribute("data-theme", t);
  }
}

const useThemePreference = createPreferenceStore<ThemeId>({
  storageKey: THEME_STORAGE_KEY,
  defaultValue: "rose",
  isValid: isThemeId,
  applyToDoc,
});

export function useThemeStore() {
  const { value, set, applyPlatformDefault, applyProfileValue, resetExplicit } = useThemePreference();
  return {
    theme: value,
    setTheme: set,
    applyPlatformDefault,
    applyProfileTheme: applyProfileValue,
    resetExplicit,
  };
}

// Non-reactive snapshot access for call sites outside React (e.g. cleanup effects)
useThemeStore.getState = () => ({ theme: useThemePreference.getState().value });
