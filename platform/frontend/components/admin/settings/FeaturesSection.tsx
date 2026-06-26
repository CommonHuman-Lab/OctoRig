// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useTranslations } from "next-intl";
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
  const t = useTranslations("admin.settings");
  return (
    <section className="admin-settings-section">
      <h2 className="admin-settings-section-title">{t("featuresTitle")}</h2>

      <SettingToggle
        label={t("pythonEditorLabel")}
        description={t("pythonEditorDesc")}
        checked={features.python_editor_enabled ?? true}
        onChange={(v) => onChange({ python_editor_enabled: v })}
      />

      <SettingToggle
        label={t("hideLabPortsLabel")}
        description={t("hideLabPortsDesc")}
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
          {t("saveFeaturesBtn")}
        </Button>
      </div>
    </section>
  );
}
