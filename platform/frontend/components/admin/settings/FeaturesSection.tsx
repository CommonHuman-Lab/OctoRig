// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Save } from "lucide-react";
import type { SiteSettings } from "@/lib/api/settings";
import { SettingToggle } from "./SettingToggle";
import { Button } from "@/components/ui/Button";

export function FeaturesSection({
  features,
  onChange,
  onSave,
  isPending,
}: {
  features: Partial<SiteSettings>;
  onChange: (patch: Partial<SiteSettings>) => void;
  onSave: () => void;
  isPending: boolean;
}) {
  return (
    <section className="admin-settings-section">
      <h2 className="admin-settings-section-title">Features</h2>

      <SettingToggle
        label="Python Editor"
        description="Show an in-browser Python scratchpad on Python challenges. Runs entirely in the user's browser via Pyodide (WebAssembly) — nothing reaches the server."
        checked={features.python_editor_enabled ?? true}
        onChange={(v) => onChange({ python_editor_enabled: v })}
      />

      <SettingToggle
        label="Hide Lab Ports"
        description="Don't reveal a lab's exposed ports anywhere in the UI or API — candidates have to scan for them. Disable this to show port numbers on lab and deployment pages."
        checked={features.hide_lab_ports ?? true}
        onChange={(v) => onChange({ hide_lab_ports: v })}
      />

      <div className="settings-row-actions">
        <Button
          variant="primary"
          size="sm"
          disabled={isPending}
          onClick={onSave}
          leftIcon={<Save size={13} />}
        >
          Save Feature Settings
        </Button>
      </div>
    </section>
  );
}
