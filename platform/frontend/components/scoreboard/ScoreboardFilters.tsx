// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Crosshair } from "lucide-react";
import { useTranslations } from "next-intl";
import type { ScoreboardEntry } from "@/lib/api/challenges";
import { Button } from "@/components/ui/Button";

export const SCOREBOARD_LIMITS = [25, 50, 100] as const;

export function ScoreboardFilters({
  events,
  eventSlug,
  limit,
  myEntry,
  onEventChange,
  onLimitChange,
  onScrollToMe,
}: {
  events: { slug: string; title: string; status: string }[];
  eventSlug: string;
  limit: number;
  myEntry: ScoreboardEntry | null | undefined;
  onEventChange: (slug: string) => void;
  onLimitChange: (limit: number) => void;
  onScrollToMe: () => void;
}) {
  const t = useTranslations("scoreboard");
  return (
    <div className="sb-filters">
      <select
        className="sb-select"
        value={eventSlug}
        onChange={(e) => onEventChange(e.target.value)}
      >
        <option value="">{t("global")}</option>
        {events
          .filter((ev) => ev.status !== "draft")
          .map((ev) => (
            <option key={ev.slug} value={ev.slug}>{ev.title}</option>
          ))}
      </select>

      <select
        className="sb-select"
        value={limit}
        onChange={(e) => onLimitChange(Number(e.target.value))}
      >
        {SCOREBOARD_LIMITS.map((l) => (
          <option key={l} value={l}>{t("topN", { count: l })}</option>
        ))}
      </select>

      {myEntry && (
        <Button variant="ghost" className="sb-highlight-btn" onClick={onScrollToMe} leftIcon={<Crosshair size={12} />}>
          {t("myRank", { rank: myEntry.rank })}
        </Button>
      )}
    </div>
  );
}
