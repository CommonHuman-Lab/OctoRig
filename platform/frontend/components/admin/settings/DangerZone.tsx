// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useTranslations } from "next-intl";
import { AlertTriangle, Power, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function DangerZone({
  onResetDb,
  isPending,
  onRestartPlatform,
  isRestartPending,
}: {
  onResetDb: () => void;
  isPending: boolean;
  onRestartPlatform: () => void;
  isRestartPending: boolean;
}) {
  const t = useTranslations("admin.settings");
  return (
    <div className="danger-zone">
      <div className="danger-zone-header">
        <AlertTriangle size={14} />
        <span>{t("dangerZoneTitle")}</span>
      </div>
      <div className="danger-action">
        <div className="danger-action-info">
          <span className="danger-action-title">{t("resetDbTitle")}</span>
          <span className="danger-action-desc">
            {t("resetDbDesc")}
          </span>
        </div>
        <Button
          variant="danger"
          disabled={isPending}
          onClick={onResetDb}
          leftIcon={<RotateCcw size={13} />}
        >
          {isPending ? t("resettingBtn") : t("resetDbTitle")}
        </Button>
      </div>
      <div className="danger-action">
        <div className="danger-action-info">
          <span className="danger-action-title">{t("restartPlatformTitle")}</span>
          <span className="danger-action-desc">
            {t("restartPlatformDesc")}
          </span>
        </div>
        <Button
          variant="danger"
          disabled={isRestartPending}
          onClick={onRestartPlatform}
          leftIcon={<Power size={13} />}
        >
          {isRestartPending ? t("restartingBtn") : t("restartPlatformTitle")}
        </Button>
      </div>
    </div>
  );
}
