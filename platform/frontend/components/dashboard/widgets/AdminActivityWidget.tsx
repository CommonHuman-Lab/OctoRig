"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useQuery } from "@tanstack/react-query";
import { ShieldCheck } from "lucide-react";
import { getAdminAuditLogs } from "@/lib/api/admin";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { formatDateTime } from "@/lib/utils/date";
import type { WidgetComponentProps } from "@/lib/widgets/types";
import { STALE_TIME } from "@/lib/config";

export function AdminActivityWidget({ widget }: WidgetComponentProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "audit-logs", "recent"],
    queryFn: () => getAdminAuditLogs({ limit: 10 }),
    staleTime: STALE_TIME.SHORT,
  });

  return (
    <div className={`g-panel dash-panel-h-${widget.height}`}>
      <div className="g-panel-header">
        <span className="text-secondary text-11 font-mono flex items-center gap-1">
          <ShieldCheck size={12} /> Recent Activity
        </span>
        <a href="/admin/audit-logs" className="text-muted text-9px">View all</a>
      </div>
      <div className="dash-panel-scroll">
        <AsyncContent
          isLoading={isLoading}
          data={data}
          empty={<p className="text-muted text-sm p-3">No recent activity.</p>}
        >
          {(rows) => (
            <table className="g-table">
              <thead><tr><th>User</th><th>Action</th><th>When</th></tr></thead>
              <tbody>
                {rows.map((l) => (
                  <tr key={l.id}>
                    <td className="text-secondary text-11">{l.username ?? "—"}</td>
                    <td className="text-muted text-11">{l.action}</td>
                    <td className="text-muted font-mono text-11">{formatDateTime(l.created_at)}</td>
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
