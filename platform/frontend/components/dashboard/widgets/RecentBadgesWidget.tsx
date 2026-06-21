"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useQuery } from "@tanstack/react-query";
import { Award } from "lucide-react";
import { getMyBadges } from "@/lib/api/badges";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { ICON_MAP } from "@/lib/utils/badge-icons";
import { formatDate } from "@/lib/utils/date";
import type { WidgetComponentProps } from "@/lib/widgets/types";

export function RecentBadgesWidget({ widget }: WidgetComponentProps) {
  const { data, isLoading } = useQuery({ queryKey: ["badges", "me"], queryFn: getMyBadges, staleTime: 30_000 });

  const earned = (data ?? [])
    .filter((b) => b.earned && b.earned_at)
    .sort((a, b) => new Date(b.earned_at!).getTime() - new Date(a.earned_at!).getTime())
    .slice(0, 8);

  return (
    <div className={`g-panel dash-panel-h-${widget.height}`}>
      <div className="g-panel-header">
        <span className="text-secondary text-11 font-mono flex items-center gap-1">
          <Award size={12} /> Recent Badges
        </span>
      </div>
      <div className="dash-panel-scroll">
        <AsyncContent
          isLoading={isLoading}
          data={earned}
          empty={<p className="text-muted text-sm p-3">No badges earned yet.</p>}
        >
          {(rows) => (
            <>
              {rows.map((b) => (
                <div
                  key={b.id}
                  className="flex items-center gap-2 px-3 py-2"
                  style={{ borderBottom: "1px solid var(--g-border)" }}
                >
                  <span style={{ fontSize: "1.1rem" }}>{ICON_MAP[b.icon] ?? "🏅"}</span>
                  <div className="flex-1">
                    <div className="text-secondary text-11">{b.name}</div>
                    <div className="text-muted text-9px">{formatDate(b.earned_at)}</div>
                  </div>
                  {b.points_value > 0 && <span className="text-accent text-9px font-mono">+{b.points_value}</span>}
                </div>
              ))}
            </>
          )}
        </AsyncContent>
      </div>
    </div>
  );
}
