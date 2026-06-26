"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./teams-admin.css";

import { useState } from "react";
import { useTranslations } from "next-intl";
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
import { Button } from "@/components/ui/Button";

const ACTION_ICON_SIZE = 16;

export default function AdminTeamsPage() {
  const t = useTranslations("admin.teams");
  const tTeams = useTranslations("teams");
  const tNav = useTranslations("nav");
  const tCommon = useTranslations("common");
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
    successMessage: tTeams("teamUpdated"),
    errorMessage: (err: any) => err?.response?.data?.detail ?? tTeams("teamUpdateFailed"),
    onSuccess: () => setEditing(null),
  });

  const deleteMutation = useApiMutation({
    mutationFn: (id: number) => deleteTeam(id),
    invalidateKeys: [["admin-teams"]],
    successMessage: t("toastTeamDeleted"),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("toastDeleteTeamFailed"),
  });

  function handleDelete(t2: AdminTeam) {
    confirm({
      title: t("deleteTeamTitle"),
      body: t("deleteTeamBody", { name: t2.name }),
      confirmLabel: tCommon("delete"),
      dangerous: true,
      onConfirm: () => deleteMutation.mutate(t2.id),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">{tNav("teams")}</h1>
        <SearchBar value={search} onChange={setSearch} placeholder={t("searchPlaceholder")} />
      </div>

      <div className="g-panel">
        <AsyncContent
          isLoading={isLoading}
          data={teams}
          empty={<EmptyCell label={t("noTeamsFound")} />}
        >
          {(teams) => (
            <table className="g-table">
              <thead>
                <tr>
                  <th>{t("colName")}</th>
                  <th>{t("colSlug")}</th>
                  <th>{tTeams("roleOwner")}</th>
                  <th>{t("colMembers")}</th>
                  <th>{tNav("deployments")}</th>
                  <th>{tTeams("personal")}</th>
                  <th>{t("colCreated")}</th>
                  <th>{tCommon("actions")}</th>
                </tr>
              </thead>
              <tbody>
                {teams.map((tm) => (
                  <tr key={tm.id}>
                    <td className="font-mono text-sm">{tm.name}</td>
                    <td className="font-mono text-11 text-muted">{tm.slug}</td>
                    <td className="text-11 text-secondary">{tm.created_by_username ?? "—"}</td>
                    <td className="text-11 text-muted">{tm.member_count}</td>
                    <td className="text-11 text-muted">{tm.deployment_count}</td>
                    <td>
                      {tm.is_personal && (
                        <span className="personal-badge text-11">{tTeams("personal")}</span>
                      )}
                    </td>
                    <td className="font-mono text-11 text-muted">
                      {formatDateTime(tm.created_at)}
                    </td>
                    <td>
                      <div className="row-actions">
                        <Button
                          icon
                          rowAction
                          tooltip={tTeams("editTeamTooltip")}
                          leftIcon={<Pencil size={ACTION_ICON_SIZE} />}
                          onClick={() => setEditing(tm)}
                        />
                        {!tm.is_personal && (
                          <Button
                            icon
                            rowAction
                            tooltip={t("deleteTeamTooltip")}
                            leftIcon={<Trash2 size={ACTION_ICON_SIZE} />}
                            onClick={() => handleDelete(tm)}
                          />
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
