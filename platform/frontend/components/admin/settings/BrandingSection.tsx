// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useTranslations } from "next-intl";
import { Save } from "lucide-react";
import type { SiteSettings } from "@/lib/api/settings";
import { SettingRow } from "./SettingRow";
import { Button } from "@/components/ui/Button";

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
  const t = useTranslations("admin.settings");
  const tAssessments = useTranslations("admin.assessments");
  return (
    <section className="admin-settings-section">
      <h2 className="admin-settings-section-title">{t("brandingTitle")}</h2>
      <p className="settings-section-desc">
        {t("brandingDesc")}
      </p>

      <SettingRow
        label={tAssessments("companyNameLabel")}
        description={t("companyNameDesc")}
        control={
          <input
            className="g-input g-input-sm"
            style={{ width: 220 }}
            placeholder={t("companyNamePlaceholder")}
            value={branding.company_name ?? ""}
            onChange={(e) => onChange({ company_name: e.target.value || null })}
          />
        }
      />

      <SettingRow
        label={tAssessments("companyLogoUrlLabel")}
        description={t("companyLogoUrlDesc")}
        control={
          <input
            className="g-input g-input-sm"
            style={{ width: 220 }}
            placeholder={tAssessments("companyLogoUrlPlaceholder")}
            value={branding.company_logo_url ?? ""}
            onChange={(e) => onChange({ company_logo_url: e.target.value || null })}
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
          {t("saveBrandingBtn")}
        </Button>
      </div>
    </section>
  );
}
