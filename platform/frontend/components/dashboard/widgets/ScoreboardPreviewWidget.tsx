"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useQuery } from "@tanstack/react-query";
import { Trophy } from "lucide-react";
import { getGlobalScoreboard } from "@/lib/api/challenges";
import { AsyncContent } from "@/components/ui/AsyncContent";
import type { WidgetComponentProps } from "@/lib/widgets/types";

export function ScoreboardPreviewWidget({ widget }: WidgetComponentProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["scoreboard", "global", "preview"],
    queryFn: () => getGlobalScoreboard(8),
    staleTime: 30_000,
  });

  return (
    <div className={`g-panel dash-panel-h-${widget.height}`}>
      <div className="g-panel-header">
        <span className="text-secondary text-11 font-mono flex items-center gap-1">
          <Trophy size={12} /> Global Scoreboard
        </span>
        <a href="/scoreboard" className="text-muted text-9px">View all</a>
      </div>
      <div className="dash-panel-scroll">
        <AsyncContent
          isLoading={isLoading}
          data={data}
          empty={<p className="text-muted text-sm p-3">No scores yet.</p>}
        >
          {(rows) => (
            <table className="g-table">
              <thead><tr><th>#</th><th>User</th><th>Points</th><th>Solves</th></tr></thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={`${r.rank}-${r.user_id ?? r.team_id}`}>
                    <td className="text-muted font-mono">{r.rank}</td>
                    <td className="text-accent">{r.username ?? `Team #${r.team_id}`}</td>
                    <td className="font-mono">{r.total}</td>
                    <td className="text-muted">{r.solve_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </AsyncContent>
      </div>
    </div>
  );
}
