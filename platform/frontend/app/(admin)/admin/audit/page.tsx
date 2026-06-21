"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./audit.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, Filter } from "lucide-react";
import { getAdminAuditLogs, type AdminAuditLog } from "@/lib/api/admin";
import { EmptyCell } from "@/components/ui/TableStates";
import { formatDateTime } from "@/lib/utils/date";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { Button } from "@/components/ui/Button";

const ACTION_GROUPS = [
  { label: "All", value: "" },
  { label: "Auth", value: "auth." },
  { label: "Teams", value: "team." },
  { label: "Labs", value: "lab." },
  { label: "Keys", value: "api_key." },
  { label: "Admin", value: "admin." },
  { label: "Schedule", value: "schedule." },
];

function ActionBadge({ action }: { action: string }) {
  const prefix = action.split(".")[0];
  const colorMap: Record<string, string> = {
    auth: "badge--auth",
    team: "badge--team",
    lab: "badge--lab",
    api_key: "badge--key",
    admin: "badge--admin",
    schedule: "badge--schedule",
  };
  return (
    <span className={`action-badge ${colorMap[prefix] ?? ""}`}>{action}</span>
  );
}

export default function AdminAuditPage() {
  const [actionFilter, setActionFilter] = useState("");
  const [userFilter, setUserFilter] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [offset, setOffset] = useState(0);
  const LIMIT = 50;

  const { data = [], isLoading } = useQuery({
    queryKey: ["admin-audit", actionFilter, userFilter, fromDate, toDate, offset],
    queryFn: () =>
      getAdminAuditLogs({
        action: actionFilter || undefined,
        user_id: userFilter ? Number(userFilter) : undefined,
        from_date: fromDate || undefined,
        to_date: toDate || undefined,
        limit: LIMIT,
        offset,
      }),
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Audit Log</h1>
      </div>

      {/* Filter bar */}
      <div className="audit-filter-bar g-panel">
        <div className="audit-filter-group">
          <label className="text-11 text-muted">Action</label>
          <div className="action-pills">
            {ACTION_GROUPS.map((g) => (
              <button
                key={g.value}
                className={`action-pill ${actionFilter === g.value ? "action-pill--active" : ""}`}
                onClick={() => { setActionFilter(g.value); setOffset(0); }}
              >
                {g.label}
              </button>
            ))}
          </div>
        </div>
        <div className="filter-row">
          <div className="filter-field">
            <label className="text-11 text-muted">From</label>
            <input
              type="date"
              className="g-input g-input-sm"
              value={fromDate}
              onChange={(e) => { setFromDate(e.target.value); setOffset(0); }}
            />
          </div>
          <div className="filter-field">
            <label className="text-11 text-muted">To</label>
            <input
              type="date"
              className="g-input g-input-sm"
              value={toDate}
              onChange={(e) => { setToDate(e.target.value); setOffset(0); }}
            />
          </div>
          {(actionFilter || fromDate || toDate) && (
            <Button
              size="sm"
              style={{ alignSelf: "flex-end" }}
              onClick={() => { setActionFilter(""); setFromDate(""); setToDate(""); setOffset(0); }}
            >
              Clear
            </Button>
          )}
        </div>
      </div>

      {/* Log table */}
      <div className="g-panel log-panel">
        <AsyncContent
          isLoading={isLoading}
          data={data}
          empty={<EmptyCell label="No entries match your filters." />}
        >
          {(data) => (
            <>
              <table className="g-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Action</th>
                    <th>User</th>
                    <th>Team</th>
                    <th>Detail</th>
                    <th>IP</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((entry) => (
                    <tr key={entry.id}>
                      <td className="font-mono text-11 text-muted nowrap">
                        {formatDateTime(entry.created_at)}
                      </td>
                      <td>
                        <ActionBadge action={entry.action} />
                      </td>
                      <td className="text-11 text-secondary">{entry.username ?? "—"}</td>
                      <td className="text-11 text-muted">{entry.team_name ?? "—"}</td>
                      <td className="text-11 text-muted detail-cell">
                        {entry.detail
                          ? typeof entry.detail === "object"
                            ? JSON.stringify(entry.detail)
                            : String(entry.detail)
                          : "—"}
                      </td>
                      <td className="font-mono text-11 text-muted">{entry.ip_address ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Pagination */}
              <div className="pagination">
                <Button
                  size="sm"
                  disabled={offset === 0}
                  onClick={() => setOffset(Math.max(0, offset - LIMIT))}
                >
                  ← Prev
                </Button>
                <span className="text-muted text-11">
                  Showing {offset + 1}–{offset + data.length}
                </span>
                <Button
                  size="sm"
                  disabled={data.length < LIMIT}
                  onClick={() => setOffset(offset + LIMIT)}
                >
                  Next →
                </Button>
              </div>
            </>
          )}
        </AsyncContent>
      </div>
    </div>
  );
}
