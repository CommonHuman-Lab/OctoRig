"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useQuery } from "@tanstack/react-query";
import { Flag } from "lucide-react";
import { getChallenges } from "@/lib/api/challenges";
import { AsyncContent } from "@/components/ui/AsyncContent";
import type { WidgetComponentProps } from "@/lib/widgets/types";
import { STALE_TIME } from "@/lib/config";

export function RecentChallengesWidget({ widget }: WidgetComponentProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["challenges", "recent"],
    queryFn: () => getChallenges(),
    staleTime: STALE_TIME.SHORT,
  });

  const recent = (data ?? [])
    .filter((c) => c.is_active && !c.solved_by_me)
    .sort((a, b) => b.id - a.id)
    .slice(0, 8);

  return (
    <div className={`g-panel dash-panel-h-${widget.height}`}>
      <div className="g-panel-header">
        <span className="text-secondary text-11 font-mono flex items-center gap-1">
          <Flag size={12} /> New Challenges
        </span>
        <a href="/challenges" className="text-muted text-9px">View all</a>
      </div>
      <div className="dash-panel-scroll">
        <AsyncContent
          isLoading={isLoading}
          data={recent}
          empty={<p className="text-muted text-sm p-3">No unsolved challenges right now.</p>}
        >
          {(rows) => (
            <table className="g-table">
              <thead><tr><th>Challenge</th><th>Category</th><th>Difficulty</th><th>Points</th></tr></thead>
              <tbody>
                {rows.map((c) => (
                  <tr key={c.id}>
                    <td><a href={`/challenges/${c.slug}`} className="text-accent">{c.title}</a></td>
                    <td className="text-muted text-11">{c.category}</td>
                    <td className="text-muted text-11">{c.difficulty}</td>
                    <td className="font-mono">{c.points}</td>
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
