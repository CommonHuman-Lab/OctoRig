"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../admin.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getPendingQueue, getApprovedQueue } from "@/lib/api/content";
import { PendingRow } from "@/components/admin/content/PendingRow";
import { ApprovedRow } from "@/components/admin/content/ApprovedRow";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { FilterPills } from "@/components/ui/FilterPills";

type Tab = "pending" | "approved";

export default function AdminContentPage() {
  const [tab, setTab] = useState<Tab>("pending");

  const { data: pending = [], isLoading: loadingPending } = useQuery({
    queryKey: ["content", "queue", "pending"],
    queryFn: getPendingQueue,
    enabled: tab === "pending",
  });

  const { data: approved = [], isLoading: loadingApproved } = useQuery({
    queryKey: ["content", "queue", "approved"],
    queryFn: getApprovedQueue,
    enabled: tab === "approved",
  });

  const isLoading = tab === "pending" ? loadingPending : loadingApproved;
  const rows = tab === "pending" ? pending : approved;

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Content Review</h1>
      </div>

      <div className="filter-bar">
        <FilterPills
          groups={[
            {
              options: ["pending", "approved"],
              value: tab,
              onChange: (v) => setTab(v as Tab),
            },
          ]}
        />
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={rows}
        empty={<div className="text-muted text-sm mt-4">No submissions in this queue.</div>}
      >
        {() => (
          <table className="g-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Type</th>
                <th>Author</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tab === "pending"
                ? pending.map((sub) => <PendingRow key={sub.id} sub={sub} />)
                : approved.map((sub) => <ApprovedRow key={sub.id} sub={sub} />)
              }
            </tbody>
          </table>
        )}
      </AsyncContent>
    </div>
  );
}
