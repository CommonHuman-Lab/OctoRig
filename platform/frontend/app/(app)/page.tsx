"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { LayoutDashboard, Settings2, Plus, Sparkles } from "lucide-react";
import { useDashboardStore } from "@/stores/dashboard.store";
import { WidgetGrid } from "@/components/dashboard/WidgetGrid";
import { AddWidgetSheet } from "@/components/dashboard/AddWidgetSheet";
import { PresetSheet } from "@/components/dashboard/PresetSheet";
import { Button } from "@/components/ui/Button";

export default function Dashboard() {
  const isCustomizing = useDashboardStore((s) => s.isCustomizing);
  const setCustomizing = useDashboardStore((s) => s.setCustomizing);
  const [showAdd, setShowAdd] = useState(false);
  const [showPresets, setShowPresets] = useState(false);

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">
          <LayoutDashboard size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
          Dashboard
        </h1>
        <div className="flex items-center gap-2">
          {isCustomizing && (
            <>
              <Button size="sm" leftIcon={<Sparkles size={13} />} onClick={() => setShowPresets(true)}>
                Presets
              </Button>
              <Button size="sm" leftIcon={<Plus size={13} />} onClick={() => setShowAdd(true)}>
                Add Widget
              </Button>
            </>
          )}
          <Button
            size="sm"
            variant={isCustomizing ? "primary" : "ghost"}
            leftIcon={<Settings2 size={13} />}
            onClick={() => setCustomizing(!isCustomizing)}
          >
            {isCustomizing ? "Done" : "Customize"}
          </Button>
        </div>
      </div>

      <WidgetGrid />

      {showAdd && <AddWidgetSheet onClose={() => setShowAdd(false)} />}
      {showPresets && <PresetSheet onClose={() => setShowPresets(false)} />}
    </div>
  );
}
