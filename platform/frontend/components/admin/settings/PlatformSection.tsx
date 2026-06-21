// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Save } from "lucide-react";
import type { SiteSettings } from "@/lib/api/settings";
import { SettingToggle } from "./SettingToggle";
import { SettingRow } from "./SettingRow";

export function PlatformSection({
  platform,
  onChange,
  onSave,
  isPending,
}: {
  platform: Partial<SiteSettings>;
  onChange: (patch: Partial<SiteSettings>) => void;
  onSave: () => void;
  isPending: boolean;
}) {
  return (
    <section className="admin-settings-section">
      <h2 className="admin-settings-section-title">Platform</h2>

      <SettingToggle
        label="Open Registration"
        description={<>Allow new users to self-register at <code>/register</code>. Disable to lock down signups.</>}
        checked={platform.registration_open ?? true}
        onChange={(v) => onChange({ registration_open: v })}
      />

      <SettingToggle
        label="Maintenance Mode"
        description="Show a maintenance screen to all non-admin users. Admins see a banner and can still access everything."
        checked={platform.maintenance_mode ?? false}
        onChange={(v) => onChange({ maintenance_mode: v })}
      />

      {platform.maintenance_mode && (
        <SettingRow
          label="Maintenance Message"
          description="Shown to users on the maintenance screen."
          indent
          control={
            <textarea
              className="g-input"
              style={{ width: 280, height: 72, resize: "vertical" }}
              placeholder="We'll be back shortly."
              value={platform.maintenance_message ?? ""}
              onChange={(e) => onChange({ maintenance_message: e.target.value || null })}
            />
          }
        />
      )}

      <SettingRow
        label="Max Flag Attempts"
        description="Maximum wrong flag submissions per challenge (global default). Leave blank for unlimited."
        control={
          <input
            type="number"
            className="g-input"
            style={{ width: 100, textAlign: "right" }}
            min={1}
            placeholder="∞"
            value={platform.max_flag_attempts ?? ""}
            onChange={(e) =>
              onChange({ max_flag_attempts: e.target.value ? parseInt(e.target.value) : null })
            }
          />
        }
      />

      <div className="settings-row-actions">
        <button
          className="g-btn g-btn-primary g-btn-sm"
          disabled={isPending}
          onClick={onSave}
        >
          <Save size={13} />
          Save Platform Settings
        </button>
      </div>
    </section>
  );
}
