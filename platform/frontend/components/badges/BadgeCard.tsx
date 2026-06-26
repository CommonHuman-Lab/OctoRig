// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { CheckCircle2 } from "lucide-react";
import { useTranslations } from "next-intl";
import type { Badge } from "@/lib/api/badges";
import { formatDate } from "@/lib/utils/date";
import { ICON_MAP } from "@/lib/utils/badge-icons";

export function BadgeCard({ badge }: { badge: Badge }) {
  const t = useTranslations("badges");
  return (
    <div className={`badge-card g-card ${badge.earned ? "badge-earned" : "badge-locked"}`}>
      <div className="badge-icon">{ICON_MAP[badge.icon] ?? "🏅"}</div>
      <div className="badge-info">
        <div className="badge-name">
          {badge.name}
          {badge.earned && <CheckCircle2 size={12} className="badge-check" />}
        </div>
        <p className="badge-desc">{badge.description}</p>
        <div className="badge-meta">
          {badge.points_value > 0 && (
            <span className="badge-pts">{t("pointsValue", { count: badge.points_value })}</span>
          )}
          {badge.earned_at && (
            <span className="badge-date">{t("earnedOn", { date: formatDate(badge.earned_at) })}</span>
          )}
        </div>
      </div>
    </div>
  );
}
