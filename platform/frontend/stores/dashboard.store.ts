"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { WidgetHeight, WidgetInstance, WidgetSpan, WidgetType } from "@/lib/widgets/types";
import { DEFAULT_WIDGETS, PRESETS } from "@/lib/widgets/presets";

function withIds(widgets: { type: WidgetType; span: WidgetSpan; height: WidgetHeight }[]): WidgetInstance[] {
  return widgets.map((w) => ({ ...w, id: crypto.randomUUID() }));
}

interface DashboardState {
  widgets: WidgetInstance[];
  isCustomizing: boolean;

  setCustomizing: (v: boolean) => void;
  addWidget: (type: WidgetType, span: WidgetSpan, height: WidgetHeight) => void;
  removeWidget: (id: string) => void;
  reorder: (fromId: string, toId: string) => void;
  setWidgetHeight: (id: string, height: WidgetHeight) => void;
  setWidgetSpan: (id: string, span: WidgetSpan) => void;
  applyPreset: (presetKey: string) => void;
  resetToDefault: () => void;
}

export const useDashboardStore = create<DashboardState>()(
  persist(
    (set) => ({
      widgets: withIds(DEFAULT_WIDGETS),
      isCustomizing: false,

      setCustomizing: (v) => set({ isCustomizing: v }),

      addWidget: (type, span, height) =>
        set((s) => ({ widgets: [...s.widgets, { id: crypto.randomUUID(), type, span, height }] })),

      removeWidget: (id) => set((s) => ({ widgets: s.widgets.filter((w) => w.id !== id) })),

      reorder: (fromId, toId) =>
        set((s) => {
          const widgets = [...s.widgets];
          const fromIndex = widgets.findIndex((w) => w.id === fromId);
          const toIndex = widgets.findIndex((w) => w.id === toId);
          if (fromIndex === -1 || toIndex === -1 || fromIndex === toIndex) return s;
          const [moved] = widgets.splice(fromIndex, 1);
          widgets.splice(toIndex, 0, moved);
          return { widgets };
        }),

      setWidgetHeight: (id, height) =>
        set((s) => ({ widgets: s.widgets.map((w) => (w.id === id ? { ...w, height } : w)) })),

      setWidgetSpan: (id, span) =>
        set((s) => ({ widgets: s.widgets.map((w) => (w.id === id ? { ...w, span } : w)) })),

      applyPreset: (presetKey) => {
        const preset = PRESETS[presetKey];
        if (!preset) return;
        set({ widgets: withIds(preset.widgets) });
      },

      resetToDefault: () => set({ widgets: withIds(DEFAULT_WIDGETS) }),
    }),
    { name: "octorig_dashboard_v1" }
  )
);
