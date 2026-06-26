// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

export type LocaleId = "en" | "fr";

export interface Locale {
  id: LocaleId;
  name: string;
  nativeName: string;
}

export const LOCALES: Locale[] = [
  { id: "en", name: "English", nativeName: "English" },
  { id: "fr", name: "French", nativeName: "Français" },
];

export const DEFAULT_LOCALE: LocaleId = "en";

export const LOCALE_STORAGE_KEY = "octorig_locale";

export function isLocaleId(v: string): v is LocaleId {
  return LOCALES.some((l) => l.id === v);
}

export function getLocale(id: LocaleId): Locale {
  return LOCALES.find((l) => l.id === id) ?? LOCALES.find((l) => l.id === DEFAULT_LOCALE)!;
}
