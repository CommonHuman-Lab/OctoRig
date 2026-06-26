// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useTranslations } from "next-intl";
import { Save } from "lucide-react";
import type { SiteSettings } from "@/lib/api/settings";
import { SettingToggle } from "./SettingToggle";
import { SettingRow } from "./SettingRow";
import { Button } from "@/components/ui/Button";

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
  const t = useTranslations("admin.settings");
  return (
    <section className="admin-settings-section">
      <h2 className="admin-settings-section-title">{t("platformTitle")}</h2>

      <SettingToggle
        label={t("openRegLabel")}
        description={t.rich("openRegDesc", { code: (chunks) => <code>{chunks}</code> })}
        checked={platform.registration_open ?? true}
        onChange={(v) => onChange({ registration_open: v })}
      />

      <SettingToggle
        label={t("maintenanceModeLabel")}
        description={t("maintenanceModeDesc")}
        checked={platform.maintenance_mode ?? false}
        onChange={(v) => onChange({ maintenance_mode: v })}
      />

      {platform.maintenance_mode && (
        <SettingRow
          label={t("maintenanceMessageLabel")}
          description={t("maintenanceMessageDesc")}
          indent
          control={
            <textarea
              className="g-input"
              style={{ width: 280, height: 72, resize: "vertical" }}
              placeholder={t("maintenanceMessagePlaceholder")}
              value={platform.maintenance_message ?? ""}
              onChange={(e) => onChange({ maintenance_message: e.target.value || null })}
            />
          }
        />
      )}

      <SettingRow
        label={t("maxFlagAttemptsLabel")}
        description={t("maxFlagAttemptsDesc")}
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
        <Button
          variant="primary"
          size="sm"
          disabled={isPending}
          onClick={onSave}
          leftIcon={<Save size={13} />}
        >
          {t("savePlatformBtn")}
        </Button>
      </div>
    </section>
  );
}
