"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { SheetShell } from "@/components/ui/SheetShell";
import { PRESETS } from "@/lib/widgets/presets";
import { useDashboardStore } from "@/stores/dashboard.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { usePermission } from "@/hooks/usePermission";

export function PresetSheet({ onClose }: { onClose: () => void }) {
  const applyPreset = useDashboardStore((s) => s.applyPreset);
  const confirm = useConfirmStore((s) => s.confirm);
  const isAdmin = usePermission("admin.panel");

  const entries = Object.entries(PRESETS).filter(([, p]) => !p.adminOnly || isAdmin);

  function handleApply(key: string, label: string) {
    confirm({
      title: `Apply "${label}" layout?`,
      body: "This replaces your current dashboard layout. You can keep customizing it afterward, or apply a different preset later.",
      confirmLabel: "Apply",
      dangerous: true,
      onConfirm: () => {
        applyPreset(key);
        onClose();
      },
    });
  }

  return (
    <SheetShell title="Apply a Preset" onClose={onClose}>
      <div className="dash-add-list">
        {entries.map(([key, preset]) => (
          <button key={key} type="button" className="dash-add-item" onClick={() => handleApply(key, preset.label)}>
            <div>
              <div className="text-secondary text-sm">{preset.label}</div>
              <div className="text-muted text-9px">{preset.description}</div>
            </div>
          </button>
        ))}
      </div>
    </SheetShell>
  );
}
