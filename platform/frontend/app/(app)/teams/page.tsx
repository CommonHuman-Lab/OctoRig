"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./teams.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useApiMutation } from "@/hooks/useApiMutation";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Plus, Users, Crown, Shield, Eye } from "lucide-react";
import { getTeams, createTeam, type TeamRole } from "@/lib/api/teams";
import { NewTeamSheet } from "@/components/teams/NewTeamSheet";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { Button } from "@/components/ui/Button";

const ROLE_ICON: Record<TeamRole, React.ReactNode> = {
  owner:   <Crown   size={11} />,
  manager: <Shield  size={11} />,
  member:  <Users   size={11} />,
  viewer:  <Eye     size={11} />,
};
const ROLE_KEY: Record<TeamRole, string> = {
  manager: "roleManager", member: "roleMember", viewer: "roleViewer",
} as Record<TeamRole, string>;

export default function TeamsPage() {
  const t = useTranslations("teams");
  const tn = useTranslations("nav");
  const tc = useTranslations("common");
  const router = useRouter();
  const [sheetOpen, setSheetOpen] = useState(false);

  const { data: teams = [], isLoading } = useQuery({
    queryKey: ["teams"],
    queryFn: getTeams,
  });

  const createMutation = useApiMutation({
    mutationFn: (data: { name: string; description?: string }) => createTeam(data),
    invalidateKeys: [["teams"]],
    successMessage: (team) => t("createdToast", { name: team.name }),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("createFailed"),
    onSuccess: (team) => {
      setSheetOpen(false);
      router.push(`/teams/${team.id}`);
    },
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">
          <Users size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
          {tn("teams")}
        </h1>
        <Button variant="primary" leftIcon={<Plus size={14} />} onClick={() => setSheetOpen(true)}>
          {t("newTeam")}
        </Button>
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={teams}
        empty={
          <div className="g-panel empty-state">
            <Users size={32} className="text-muted" />
            <p className="text-muted text-sm mt-2">{t("noTeams")}</p>
            <Button variant="primary" className="mt-2" onClick={() => setSheetOpen(true)}>
              {t("createFirst")}
            </Button>
          </div>
        }
      >
        {(teams) => (
          <div className="g-grid-auto team-grid">
            {teams.map((team) => {
              return (
                <Link key={team.id} href={`/teams/${team.id}`} className="g-card team-card">
                  <div className="team-card-header">
                    <span className="team-name font-mono">{team.name}</span>
                    <span className={`role-badge role-badge--${team.my_role}`}>
                      {ROLE_ICON[team.my_role]}
                      {team.my_role === "owner" ? tc("owner") : t(ROLE_KEY[team.my_role] as any)}
                    </span>
                  </div>
                  {team.description && (
                    <p className="text-muted text-11 team-desc">{team.description}</p>
                  )}
                  <div className="team-meta">
                    <span className="text-muted text-11">
                      <Users size={11} /> {t("memberCount", { count: team.member_count })}
                    </span>
                    {team.is_personal && (
                      <span className="personal-badge text-11">{t("personal")}</span>
                    )}
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </AsyncContent>

      <NewTeamSheet
        open={sheetOpen}
        createMutation={createMutation}
        onClose={() => setSheetOpen(false)}
      />
    </div>
  );
}
