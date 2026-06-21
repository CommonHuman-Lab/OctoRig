"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../teams.css";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { ArrowLeft, UserPlus, Pencil, Check, X } from "lucide-react";
import Link from "next/link";
import {
  getTeam, getTeamMembers, inviteMember, removeMember, changeMemberRole, updateTeam,
  type TeamRole, type Team,
} from "@/lib/api/teams";
import { useUserStore } from "@/stores/user.store";
import { useNotificationsStore } from "@/stores/notifications.store";
import { InviteForm } from "@/components/teams/InviteForm";
import { MembersTable } from "@/components/teams/MembersTable";

export default function TeamDetailPage() {
  const { id } = useParams<{ id: string }>();
  const teamId = Number(id);
  const qc = useQueryClient();
  const { user } = useUserStore();
  const { push } = useNotificationsStore();

  const [showInvite, setShowInvite] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDesc, setEditDesc] = useState("");

  const { data: team, isLoading: teamLoading } = useQuery({
    queryKey: ["team", teamId],
    queryFn: () => getTeam(teamId),
  });

  const { data: members = [], isLoading: membersLoading } = useQuery({
    queryKey: ["team-members", teamId],
    queryFn: () => getTeamMembers(teamId),
  });

  const inviteMutation = useMutation({
    mutationFn: ({ username, role }: { username: string; role: TeamRole }) =>
      inviteMember(teamId, { username, role }),
    onSuccess: (_, { username }) => {
      push("success", `Invitation sent to ${username}`);
      setShowInvite(false);
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to send invitation"),
  });

  const removeMutation = useApiMutation({
    mutationFn: (userId: number) => removeMember(teamId, userId),
    invalidateKeys: [["team-members", teamId]],
    successMessage: "Member removed",
    errorMessage: (err: any) => err?.response?.data?.detail ?? "Failed to remove member",
  });

  const roleMutation = useApiMutation({
    mutationFn: ({ userId, role }: { userId: number; role: TeamRole }) =>
      changeMemberRole(teamId, userId, role),
    invalidateKeys: [["team-members", teamId]],
    successMessage: "Role updated",
    errorMessage: (err: any) => err?.response?.data?.detail ?? "Failed to update role",
  });

  const editMutation = useApiMutation<Team, void>({
    mutationFn: () => updateTeam(teamId, { name: editName.trim(), description: editDesc.trim() || undefined }),
    invalidateKeys: [["team", teamId]],
    successMessage: "Team updated",
    errorMessage: (err: any) => err?.response?.data?.detail ?? "Failed to update team",
    onSuccess: () => setEditing(false),
  });

  function startEdit() {
    setEditName(team?.name ?? "");
    setEditDesc(team?.description ?? "");
    setEditing(true);
  }

  const canManage =
    team?.my_role === "owner" || team?.my_role === "manager" ||
    (user?.permissions?.includes("admin.panel") ?? false);

  if (teamLoading) return <div className="page text-muted text-sm">Loading…</div>;
  if (!team) return <div className="page text-muted text-sm">Team not found.</div>;

  return (
    <div className="page">
      <div className="page-header">
        <Link href="/teams" className="back-link text-muted text-sm">
          <ArrowLeft size={14} />
          Teams
        </Link>
      </div>

      <div className="team-header g-panel">
        <div className="g-panel-header">
          {editing ? (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <input
                className="g-input g-input-sm font-mono"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                placeholder="Team name"
                autoFocus
              />
              <input
                className="g-input g-input-sm"
                value={editDesc}
                onChange={(e) => setEditDesc(e.target.value)}
                placeholder="Description (optional)"
              />
              <div style={{ display: "flex", gap: "0.4rem" }}>
                <button
                  className="g-btn g-btn-primary g-btn-sm"
                  onClick={() => editMutation.mutate()}
                  disabled={!editName.trim() || editMutation.isPending}
                >
                  <Check size={12} />
                  {editMutation.isPending ? "Saving…" : "Save"}
                </button>
                <button className="g-btn g-btn-ghost g-btn-sm" onClick={() => setEditing(false)}>
                  <X size={12} />
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <>
              <div>
                <h1 className="font-mono" style={{ fontSize: "1rem" }}>{team.name}</h1>
                {team.description && (
                  <p className="text-muted text-11 mt-1">{team.description}</p>
                )}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span className={`role-badge role-badge--${team.my_role}`}>{team.my_role}</span>
                {canManage && (
                  <button className="g-btn g-btn-ghost g-btn-icon" onClick={startEdit} title="Edit team">
                    <Pencil size={13} />
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <div className="members-panel g-panel mt-3">
        <div className="g-panel-header">
          <span className="font-mono text-sm">Members ({members.length})</span>
          {canManage && (
            <button
              className="g-btn g-btn-ghost g-btn-sm"
              onClick={() => setShowInvite(!showInvite)}
            >
              <UserPlus size={13} />
              Invite
            </button>
          )}
        </div>

        {showInvite && (
          <InviteForm
            onSubmit={(username, role) => inviteMutation.mutate({ username, role })}
            isPending={inviteMutation.isPending}
            onCancel={() => setShowInvite(false)}
          />
        )}

        {membersLoading ? (
          <div className="members-loading text-muted text-11">Loading members…</div>
        ) : (
          <MembersTable
            members={members}
            canManage={!!canManage}
            currentUserId={user?.id ?? -1}
            onRemove={(userId) => removeMutation.mutate(userId)}
            onChangeRole={(userId, role) => roleMutation.mutate({ userId, role })}
            isPending={removeMutation.isPending || roleMutation.isPending}
          />
        )}
      </div>
    </div>
  );
}
