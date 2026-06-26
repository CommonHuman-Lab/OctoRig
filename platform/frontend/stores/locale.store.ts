"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { createPreferenceStore } from "./createPreferenceStore";
import { type LocaleId, DEFAULT_LOCALE, LOCALE_STORAGE_KEY, isLocaleId } from "@/lib/i18n";

function applyToDoc(l: LocaleId) {
  if (typeof document !== "undefined") {
    document.documentElement.setAttribute("lang", l);
  }
}

const useLocalePreference = createPreferenceStore<LocaleId>({
  storageKey: LOCALE_STORAGE_KEY,
  defaultValue: DEFAULT_LOCALE,
  isValid: isLocaleId,
  applyToDoc,
});

export function useLocaleStore() {
  const { value, set, applyPlatformDefault, applyProfileValue, resetExplicit } = useLocalePreference();
  return {
    locale: value,
    setLocale: set,
    applyPlatformDefault,
    applyProfileLocale: applyProfileValue,
    resetExplicit,
  };
}
