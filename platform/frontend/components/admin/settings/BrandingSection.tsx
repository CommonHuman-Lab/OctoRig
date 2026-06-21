// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Save } from "lucide-react";
import type { SiteSettings } from "@/lib/api/settings";
import { SettingRow } from "./SettingRow";

export function BrandingSection({
  branding,
  onChange,
  onSave,
  isPending,
}: {
  branding: Partial<SiteSettings>;
  onChange: (patch: Partial<SiteSettings>) => void;
  onSave: () => void;
  isPending: boolean;
}) {
  return (
    <section className="admin-settings-section">
      <h2 className="admin-settings-section-title">Branding</h2>
      <p className="settings-section-desc">
        Global platform branding shown on the candidate-facing assessment pages.
        Individual assessments can override these with their own company name and logo.
      </p>

      <SettingRow
        label="Company Name"
        description="Displayed on assessment landing pages and the candidate workspace header."
        control={
          <input
            className="g-input g-input-sm"
            style={{ width: 220 }}
            placeholder="e.g. Acme Security"
            value={branding.company_name ?? ""}
            onChange={(e) => onChange({ company_name: e.target.value || null })}
          />
        }
      />

      <SettingRow
        label="Company Logo URL"
        description="Public URL to a PNG or SVG logo. Displayed next to the company name on assessment pages."
        control={
          <input
            className="g-input g-input-sm"
            style={{ width: 220 }}
            placeholder="https://example.com/logo.png"
            value={branding.company_logo_url ?? ""}
            onChange={(e) => onChange({ company_logo_url: e.target.value || null })}
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
          Save Branding
        </button>
      </div>
    </section>
  );
}
