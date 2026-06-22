"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useQuery } from "@tanstack/react-query";
import { CalendarClock } from "lucide-react";
import { getEvents } from "@/lib/api/events";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { formatDateTime } from "@/lib/utils/date";
import type { WidgetComponentProps } from "@/lib/widgets/types";
import { STALE_TIME } from "@/lib/config";

export function UpcomingEventsWidget({ widget }: WidgetComponentProps) {
  const { data, isLoading } = useQuery({ queryKey: ["events"], queryFn: () => getEvents(), staleTime: STALE_TIME.SHORT });

  const upcoming = (data ?? [])
    .filter((e) => e.status === "running" || e.status === "published")
    .sort((a, b) => (a.start_at ?? "").localeCompare(b.start_at ?? ""));

  return (
    <div className={`g-panel dash-panel-h-${widget.height}`}>
      <div className="g-panel-header">
        <span className="text-secondary text-11 font-mono flex items-center gap-1">
          <CalendarClock size={12} /> Events
        </span>
        <a href="/events" className="text-muted text-9px">View all</a>
      </div>
      <div className="dash-panel-scroll">
        <AsyncContent
          isLoading={isLoading}
          data={upcoming}
          empty={<p className="text-muted text-sm p-3">No upcoming or running events.</p>}
        >
          {(rows) => (
            <table className="g-table">
              <thead><tr><th>Event</th><th>Status</th><th>Starts</th></tr></thead>
              <tbody>
                {rows.map((e) => (
                  <tr key={e.id}>
                    <td><a href={`/events/${e.slug}`} className="text-accent">{e.title}</a></td>
                    <td className={e.status === "running" ? "text-success" : "text-warning"}>{e.status}</td>
                    <td className="text-muted font-mono text-11">{formatDateTime(e.start_at)}</td>
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
