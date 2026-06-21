"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./teams-admin.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Pencil, Trash2 } from "lucide-react";
import { SearchBar } from "@/components/ui/SearchBar";
import { getAdminTeams, type AdminTeam } from "@/lib/api/admin";
import { updateTeam, deleteTeam } from "@/lib/api/teams";
import { EmptyCell } from "@/components/ui/TableStates";
import { formatDateTime } from "@/lib/utils/date";
import { useConfirmStore } from "@/stores/confirm.store";
import { TeamEditSheet } from "@/components/admin/teams/TeamEditSheet";
import { AsyncContent } from "@/components/ui/AsyncContent";

const ACTION_ICON_SIZE = 16;

export default function AdminTeamsPage() {
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<AdminTeam | null>(null);
  const { confirm } = useConfirmStore();

  const { data: teams = [], isLoading } = useQuery({
    queryKey: ["admin-teams", search],
    queryFn: () => getAdminTeams({ search: search || undefined }),
  });

  const updateMutation = useApiMutation({
    mutationFn: (payload: { name: string }) => updateTeam(editing!.id, payload),
    invalidateKeys: [["admin-teams"]],
    successMessage: "Team updated.",
    errorMessage: (err: any) => err?.response?.data?.detail ?? "Failed to update team.",
    onSuccess: () => setEditing(null),
  });

  const deleteMutation = useApiMutation({
    mutationFn: (id: number) => deleteTeam(id),
    invalidateKeys: [["admin-teams"]],
    successMessage: "Team deleted.",
    errorMessage: (err: any) => err?.response?.data?.detail ?? "Failed to delete team.",
  });

  function handleDelete(t: AdminTeam) {
    confirm({
      title: "Delete team",
      body: `Delete "${t.name}"? This removes all memberships and cannot be undone.`,
      confirmLabel: "Delete",
      dangerous: true,
      onConfirm: () => deleteMutation.mutate(t.id),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Teams</h1>
        <SearchBar value={search} onChange={setSearch} placeholder="Search teams…" />
      </div>

      <div className="g-panel">
        <AsyncContent
          isLoading={isLoading}
          data={teams}
          empty={<EmptyCell label="No teams found." />}
        >
          {(teams) => (
            <table className="g-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Slug</th>
                  <th>Owner</th>
                  <th>Members</th>
                  <th>Deployments</th>
                  <th>Personal</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {teams.map((t) => (
                  <tr key={t.id}>
                    <td className="font-mono text-sm">{t.name}</td>
                    <td className="font-mono text-11 text-muted">{t.slug}</td>
                    <td className="text-11 text-secondary">{t.created_by_username ?? "—"}</td>
                    <td className="text-11 text-muted">{t.member_count}</td>
                    <td className="text-11 text-muted">{t.deployment_count}</td>
                    <td>
                      {t.is_personal && (
                        <span className="personal-badge text-11">Personal</span>
                      )}
                    </td>
                    <td className="font-mono text-11 text-muted">
                      {formatDateTime(t.created_at)}
                    </td>
                    <td>
                      <div className="row-actions">
                        <button
                          className="g-btn g-btn-ghost g-btn-icon row-action-icon"
                          title="Edit team"
                          onClick={() => setEditing(t)}
                        >
                          <Pencil size={ACTION_ICON_SIZE} />
                        </button>
                        {!t.is_personal && (
                          <button
                            className="g-btn g-btn-ghost g-btn-icon row-action-icon"
                            title="Delete team"
                            onClick={() => handleDelete(t)}
                          >
                            <Trash2 size={ACTION_ICON_SIZE} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </AsyncContent>
      </div>

      <TeamEditSheet
        open={!!editing}
        team={editing}
        saveMutation={updateMutation}
        onClose={() => setEditing(null)}
      />
    </div>
  );
}
