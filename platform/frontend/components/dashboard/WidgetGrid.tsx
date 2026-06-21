"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { useDashboardStore } from "@/stores/dashboard.store";
import { usePermission } from "@/hooks/usePermission";
import { WIDGET_REGISTRY } from "@/lib/widgets/registry";
import { WidgetShell } from "./WidgetShell";

export function WidgetGrid() {
  const widgets = useDashboardStore((s) => s.widgets);
  const isCustomizing = useDashboardStore((s) => s.isCustomizing);
  const removeWidget = useDashboardStore((s) => s.removeWidget);
  const setWidgetHeight = useDashboardStore((s) => s.setWidgetHeight);
  const reorder = useDashboardStore((s) => s.reorder);
  const isAdmin = usePermission("admin.panel");
  const [dragId, setDragId] = useState<string | null>(null);

  const visible = widgets.filter((w) => {
    const entry = WIDGET_REGISTRY[w.type];
    return Boolean(entry) && (!entry.adminOnly || isAdmin);
  });

  return (
    <div className="dash-grid">
      {visible.map((w) => {
        const entry = WIDGET_REGISTRY[w.type];
        const Component = entry.component;
        return (
          <div
            key={w.id}
            className={`dash-cell dash-span-${w.span}`}
            draggable={isCustomizing}
            onDragStart={() => setDragId(w.id)}
            onDragOver={(e) => {
              if (isCustomizing) e.preventDefault();
            }}
            onDrop={(e) => {
              e.preventDefault();
              if (dragId && dragId !== w.id) reorder(dragId, w.id);
              setDragId(null);
            }}
          >
            <WidgetShell
              widget={w}
              category={entry.category}
              customizing={isCustomizing}
              onRemove={() => removeWidget(w.id)}
              onSetHeight={entry.category === "panel" ? (h) => setWidgetHeight(w.id, h) : undefined}
            >
              <Component widget={w} />
            </WidgetShell>
          </div>
        );
      })}
    </div>
  );
}
