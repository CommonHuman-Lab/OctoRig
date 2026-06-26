// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import type { TeamMember, TeamRole } from "@/lib/api/teams";
import { TEAM_ROLES } from "@/lib/api/teams";
import { formatDate } from "@/lib/utils/date";
import { Button } from "@/components/ui/Button";

export function MembersTable({
  members,
  canManage,
  currentUserId,
  onRemove,
  onChangeRole,
  isPending,
}: {
  members: TeamMember[];
  canManage: boolean;
  currentUserId: number;
  onRemove: (userId: number) => void;
  onChangeRole: (userId: number, role: TeamRole) => void;
  isPending: boolean;
}) {
  const t = useTranslations("teams");
  const tc = useTranslations("common");
  return (
    <table className="g-table">
      <thead>
        <tr>
          <th>{t("colUser")}</th>
          <th>{t("colRole")}</th>
          <th>{t("colJoined")}</th>
          {canManage && <th>{tc("actions")}</th>}
        </tr>
      </thead>
      <tbody>
        {members.map((m) => {
          const isSelf = m.user_id === currentUserId;
          return (
            <tr key={m.id}>
              <td>
                <span className="font-mono text-sm">{m.username}</span>
                <span className="text-muted text-11 ml-1">{m.email}</span>
              </td>
              <td>
                {canManage && !isSelf ? (
                  <select
                    className="g-select g-select-sm"
                    value={m.role}
                    onChange={(e) => onChangeRole(m.user_id, e.target.value as TeamRole)}
                  >
                    {TEAM_ROLES.map((r) => (
                      <option key={r} value={r}>
                        {r.charAt(0).toUpperCase() + r.slice(1)}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className={`role-badge role-badge--${m.role}`}>{m.role}</span>
                )}
              </td>
              <td className="font-mono text-11 text-muted">{formatDate(m.joined_at)}</td>
              {canManage && (
                <td>
                  {!isSelf && (
                    <Button
                      variant="danger"
                      icon
                      leftIcon={<Trash2 size={13} />}
                      onClick={() => onRemove(m.user_id)}
                      disabled={isPending}
                      tooltip={t("removeMemberTooltip")}
                    />
                  )}
                </td>
              )}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
