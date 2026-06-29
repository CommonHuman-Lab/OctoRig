"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { NAV_KEYS } from "@/lib/nav/items";

interface SidebarState {
  collapsed: boolean;
  order: string[];
  hidden: string[];

  toggleCollapsed: () => void;
  reorderNav: (fromKey: string, toKey: string) => void;
  toggleNavHidden: (key: string) => void;
  resetNav: () => void;
}

export const useSidebarStore = create<SidebarState>()(
  persist(
    (set) => ({
      collapsed: false,
      order: NAV_KEYS,
      hidden: [],

      toggleCollapsed: () => set((s) => ({ collapsed: !s.collapsed })),

      reorderNav: (fromKey, toKey) =>
        set((s) => {
          const order = [...s.order];
          const fromIndex = order.indexOf(fromKey);
          const toIndex = order.indexOf(toKey);
          if (fromIndex === -1 || toIndex === -1 || fromIndex === toIndex) return s;
          const [moved] = order.splice(fromIndex, 1);
          order.splice(toIndex, 0, moved);
          return { order };
        }),

      toggleNavHidden: (key) =>
        set((s) => ({
          hidden: s.hidden.includes(key)
            ? s.hidden.filter((k) => k !== key)
            : [...s.hidden, key],
        })),

      resetNav: () => set({ order: NAV_KEYS, hidden: [] }),
    }),
    { name: "octorig_sidebar" }
  )
);
