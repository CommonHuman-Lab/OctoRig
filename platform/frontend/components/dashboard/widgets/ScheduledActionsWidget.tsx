"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useQuery } from "@tanstack/react-query";
import { Timer } from "lucide-react";
import { getScheduledActions } from "@/lib/api/scheduler";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { formatDateTime } from "@/lib/utils/date";
import type { WidgetComponentProps } from "@/lib/widgets/types";
import { STALE_TIME } from "@/lib/config";

export function ScheduledActionsWidget({ widget }: WidgetComponentProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["scheduled-actions", "pending"],
    queryFn: () => getScheduledActions("pending"),
    staleTime: STALE_TIME.SHORT,
  });

  const upcoming = (data ?? []).sort((a, b) => a.scheduled_at.localeCompare(b.scheduled_at));

  return (
    <div className={`g-panel dash-panel-h-${widget.height}`}>
      <div className="g-panel-header">
        <span className="text-secondary text-11 font-mono flex items-center gap-1">
          <Timer size={12} /> My Scheduled Actions
        </span>
      </div>
      <div className="dash-panel-scroll">
        <AsyncContent
          isLoading={isLoading}
          data={upcoming}
          empty={<p className="text-muted text-sm p-3">Nothing scheduled.</p>}
        >
          {(rows) => (
            <table className="g-table">
              <thead><tr><th>Action</th><th>When</th></tr></thead>
              <tbody>
                {rows.map((a) => (
                  <tr key={a.id}>
                    <td className="text-secondary text-11">{a.action.replace(/_/g, " ")}</td>
                    <td className="text-muted font-mono text-11">{formatDateTime(a.scheduled_at)}</td>
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
