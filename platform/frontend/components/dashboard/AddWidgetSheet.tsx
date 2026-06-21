"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { SheetShell } from "@/components/ui/SheetShell";
import { WIDGET_REGISTRY, WIDGET_TYPES } from "@/lib/widgets/registry";
import { useDashboardStore } from "@/stores/dashboard.store";
import { usePermission } from "@/hooks/usePermission";

export function AddWidgetSheet({ onClose }: { onClose: () => void }) {
  const widgets = useDashboardStore((s) => s.widgets);
  const addWidget = useDashboardStore((s) => s.addWidget);
  const isAdmin = usePermission("admin.panel");

  const presentTypes = new Set(widgets.map((w) => w.type));
  const available = WIDGET_TYPES.filter((t) => {
    const entry = WIDGET_REGISTRY[t];
    if (presentTypes.has(t)) return false;
    if (entry.adminOnly && !isAdmin) return false;
    return true;
  });

  return (
    <SheetShell title="Add Widget" onClose={onClose}>
      <div className="dash-add-list">
        {available.length === 0 && (
          <p className="text-muted text-sm">All available widgets are already on your dashboard.</p>
        )}
        {available.map((t) => {
          const entry = WIDGET_REGISTRY[t];
          const Icon = entry.icon;
          return (
            <button
              key={t}
              type="button"
              className="dash-add-item"
              onClick={() => {
                addWidget(t, entry.defaultSpan, entry.defaultHeight);
                onClose();
              }}
            >
              <Icon size={14} />
              <div>
                <div className="text-secondary text-sm">{entry.label}</div>
                <div className="text-muted text-9px">{entry.description}</div>
              </div>
            </button>
          );
        })}
      </div>
    </SheetShell>
  );
}
