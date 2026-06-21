"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./teams.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Plus, Users, Crown, Shield, Eye } from "lucide-react";
import { getTeams, createTeam, type TeamRole } from "@/lib/api/teams";
import { NewTeamSheet } from "@/components/teams/NewTeamSheet";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { Button } from "@/components/ui/Button";

const ROLE_LABEL: Record<TeamRole, { label: string; icon: React.ReactNode }> = {
  owner:   { label: "Owner",   icon: <Crown   size={11} /> },
  manager: { label: "Manager", icon: <Shield  size={11} /> },
  member:  { label: "Member",  icon: <Users   size={11} /> },
  viewer:  { label: "Viewer",  icon: <Eye     size={11} /> },
};

export default function TeamsPage() {
  const router = useRouter();
  const [sheetOpen, setSheetOpen] = useState(false);

  const { data: teams = [], isLoading } = useQuery({
    queryKey: ["teams"],
    queryFn: getTeams,
  });

  const createMutation = useApiMutation({
    mutationFn: (data: { name: string; description?: string }) => createTeam(data),
    invalidateKeys: [["teams"]],
    successMessage: (team) => `Team "${team.name}" created`,
    errorMessage: (err: any) => err?.response?.data?.detail ?? "Failed to create team",
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
          Teams
        </h1>
        <Button variant="primary" leftIcon={<Plus size={14} />} onClick={() => setSheetOpen(true)}>
          New Team
        </Button>
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={teams}
        empty={
          <div className="g-panel empty-state">
            <Users size={32} className="text-muted" />
            <p className="text-muted text-sm mt-2">No teams yet.</p>
            <button className="g-btn g-btn-primary mt-2" onClick={() => setSheetOpen(true)}>
              Create your first team
            </button>
          </div>
        }
      >
        {(teams) => (
          <div className="g-grid-auto team-grid">
            {teams.map((team) => {
              const role = ROLE_LABEL[team.my_role];
              return (
                <Link key={team.id} href={`/teams/${team.id}`} className="g-card team-card">
                  <div className="team-card-header">
                    <span className="team-name font-mono">{team.name}</span>
                    <span className={`role-badge role-badge--${team.my_role}`}>
                      {role.icon}
                      {role.label}
                    </span>
                  </div>
                  {team.description && (
                    <p className="text-muted text-11 team-desc">{team.description}</p>
                  )}
                  <div className="team-meta">
                    <span className="text-muted text-11">
                      <Users size={11} /> {team.member_count} member{team.member_count !== 1 ? "s" : ""}
                    </span>
                    {team.is_personal && (
                      <span className="personal-badge text-11">Personal</span>
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
