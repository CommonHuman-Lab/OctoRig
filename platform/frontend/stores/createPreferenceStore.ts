"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface PreferenceState<T extends string> {
  value: T;
  _explicit: boolean;
  set: (v: T) => void;
  applyPlatformDefault: (v: string | null | undefined) => void;
  applyProfileValue: (v: string | null | undefined) => void;
  resetExplicit: () => void;
}

interface PreferenceOptions<T extends string> {
  storageKey: string;
  defaultValue: T;
  isValid: (v: string) => v is T;
  applyToDoc: (v: T) => void;
}

// Shared shape behind theme/locale (and any future "pick one, persist client-side,
// let the user's saved server profile win on login") preferences.
export function createPreferenceStore<T extends string>(opts: PreferenceOptions<T>) {
  return create<PreferenceState<T>>()(
    persist(
      (set, get) => ({
        value: opts.defaultValue,
        _explicit: false,

        set: (value) => {
          opts.applyToDoc(value);
          set({ value, _explicit: true });
        },

        // Only applies if the user has never explicitly chosen a value
        applyPlatformDefault: (v) => {
          if (get()._explicit || !v || !opts.isValid(v)) return;
          opts.applyToDoc(v);
          set({ value: v });
        },

        // Always applies — user's saved server-side preference wins
        applyProfileValue: (v) => {
          if (!v || !opts.isValid(v)) return;
          opts.applyToDoc(v);
          set({ value: v, _explicit: true });
        },

        // Called on logout so the next user's profile/platform default takes over
        resetExplicit: () => set({ _explicit: false }),
      }),
      { name: opts.storageKey }
    )
  );
}
