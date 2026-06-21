// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import Link from "next/link";
import { ShieldCheck, ShieldOff, RotateCcw, UserCog, LockOpen, KeyRound } from "lucide-react";
import type { AdminUser } from "@/lib/api/admin";

const ACTION_ICON_SIZE = 16;

function isLocked(u: AdminUser): boolean {
  return !!u.locked_until && new Date(u.locked_until) > new Date();
}

function RolePill({ label }: { label: string }) {
  return <span className="g-badge g-badge--accent">{label}</span>;
}

export function UsersTable({
  users,
  isLoading,
  onActivate,
  onManageRoles,
  onResetPassword,
  onResetPoints,
  onUnlock,
  isPending,
  currentUserId,
}: {
  users: AdminUser[];
  isLoading: boolean;
  onActivate: (user: AdminUser) => void;
  onManageRoles: (user: AdminUser) => void;
  onResetPassword: (user: AdminUser) => void;
  onResetPoints: (user: AdminUser) => void;
  onUnlock: (user: AdminUser) => void;
  isPending: boolean;
  currentUserId?: number;
}) {
  if (isLoading) {
    return <div className="loading-cell text-muted text-sm">Loading…</div>;
  }

  return (
    <table className="g-table">
      <thead>
        <tr>
          <th>Username</th>
          <th>Email</th>
          <th>Roles</th>
          <th>Teams</th>
          <th>Deployments</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {users.map((u) => (
          <tr key={u.id} className={!u.is_active ? "row-inactive" : ""}>
            <td className="font-mono text-sm">
              <Link href={`/profile/${u.username}`} style={{ color: "var(--g-accent)" }}>
                {u.username}
              </Link>
            </td>
            <td className="text-11 text-muted">{u.email}</td>
            <td>
              <div className="role-pills">
                {u.platform_roles.length === 0 && <RolePill label="None" />}
                {u.platform_roles.map((slug) => (
                  <RolePill key={slug} label={slug} />
                ))}
              </div>
            </td>
            <td className="text-11 text-muted">{u.team_count}</td>
            <td className="text-11 text-muted">{u.deployment_count}</td>
            <td>
              <span className={`g-status-dot ${u.is_active ? "g-status-dot--active" : "g-status-dot--inactive"}`}>
                {u.is_active ? "Active" : "Inactive"}
              </span>
              {isLocked(u) && <span className="g-badge g-badge--muted" style={{ marginLeft: 6 }}>Locked</span>}
              {u.is_owner && <span className="g-badge g-badge--accent" style={{ marginLeft: 6 }}>Owner</span>}
            </td>
            <td>
              <div className="row-actions">
                {!u.is_owner && !(u.is_active && u.id === currentUserId) && (
                  <button
                    className="g-btn g-btn-ghost g-btn-icon row-action-icon"
                    title={u.is_active ? "Deactivate" : "Activate"}
                    onClick={() => onActivate(u)}
                  >
                    {u.is_active ? <ShieldOff size={ACTION_ICON_SIZE} /> : <ShieldCheck size={ACTION_ICON_SIZE} />}
                  </button>
                )}
                {isLocked(u) && (
                  <button
                    className="g-btn g-btn-ghost g-btn-icon row-action-icon"
                    title="Unlock account"
                    onClick={() => onUnlock(u)}
                  >
                    <LockOpen size={ACTION_ICON_SIZE} />
                  </button>
                )}
                {!u.is_owner && u.id !== currentUserId && (
                  <button
                    className="g-btn g-btn-ghost g-btn-icon row-action-icon"
                    title="Manage roles"
                    onClick={() => onManageRoles(u)}
                  >
                    <UserCog size={ACTION_ICON_SIZE} />
                  </button>
                )}
                <button
                  className="g-btn g-btn-ghost g-btn-icon row-action-icon"
                  title="Reset password"
                  onClick={() => onResetPassword(u)}
                >
                  <KeyRound size={ACTION_ICON_SIZE} />
                </button>
                <button
                  className="g-btn g-btn-ghost g-btn-icon row-action-icon"
                  title="Reset points &amp; submissions"
                  disabled={isPending}
                  onClick={() => onResetPoints(u)}
                >
                  <RotateCcw size={ACTION_ICON_SIZE} />
                </button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
