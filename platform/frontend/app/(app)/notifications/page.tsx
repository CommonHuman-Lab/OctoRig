"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./notifications.css";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Bell, CheckCheck, Check, X, Trash2 } from "lucide-react";
import {
  getNotifications, markAllRead, markRead, deleteNotification,
  type AppNotification,
} from "@/lib/api/notifications";
import { acceptInvitation, declineInvitation } from "@/lib/api/teams";
import { useNotificationsStore } from "@/stores/notifications.store";
import { AsyncContent } from "@/components/ui/AsyncContent";

function timeAgo(created_at: string) {
  const ms = Date.now() - new Date(created_at).getTime();
  const m = Math.floor(ms / 60_000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

function TeamInviteActions({
  n,
  onDone,
}: {
  n: AppNotification;
  onDone: () => void;
}) {
  const { push } = useNotificationsStore();
  const token = n.data.invitation_token as string | undefined;

  const acceptMutation = useMutation({
    mutationFn: () => acceptInvitation(token!),
    onSuccess: () => {
      push("success", `Joined ${n.data.team_name as string}`);
      onDone();
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to accept"),
  });

  const declineMutation = useMutation({
    mutationFn: () => declineInvitation(token!),
    onSuccess: () => {
      push("info", "Invitation declined");
      onDone();
    },
    onError: () => push("error", "Failed to decline"),
  });

  if (!token) return null;

  return (
    <div style={{ display: "flex", gap: "0.4rem", marginTop: "0.5rem" }}>
      <button
        className="g-btn g-btn-primary g-btn-sm"
        onClick={() => acceptMutation.mutate()}
        disabled={acceptMutation.isPending || declineMutation.isPending}
      >
        <Check size={12} />
        Accept
      </button>
      <button
        className="g-btn g-btn-ghost g-btn-sm"
        onClick={() => declineMutation.mutate()}
        disabled={acceptMutation.isPending || declineMutation.isPending}
      >
        <X size={12} />
        Decline
      </button>
    </div>
  );
}

function NotificationRow({
  n,
  onRead,
  onDelete,
  onInviteResolved,
}: {
  n: AppNotification;
  onRead: (id: number) => void;
  onDelete: (id: number) => void;
  onInviteResolved: () => void;
}) {
  const isUnread = !n.read_at;

  return (
    <div className={`notif-row ${isUnread ? "notif-row--unread" : ""}`}>
      {isUnread && <span className="notif-dot" />}
      <div className="notif-content" onClick={() => isUnread && onRead(n.id)} style={{ cursor: isUnread ? "pointer" : "default" }}>
        <div className="notif-title">{n.title}</div>
        {n.body && <p className="notif-body">{n.body}</p>}
        {n.type === "team_invite" && (
          <TeamInviteActions n={n} onDone={() => { onDelete(n.id); onInviteResolved(); }} />
        )}
      </div>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "0.4rem", flexShrink: 0 }}>
        <span className="notif-time">{timeAgo(n.created_at)}</span>
        {!isUnread && (
          <button
            className="g-btn g-btn-ghost g-btn-icon"
            style={{ padding: "0.2rem" }}
            onClick={() => onDelete(n.id)}
            title="Delete"
          >
            <Trash2 size={12} />
          </button>
        )}
      </div>
    </div>
  );
}

export default function NotificationsPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => getNotifications(false, 100),
  });

  const readMutation = useApiMutation({
    mutationFn: markRead,
    invalidateKeys: [["notifications"], ["notifications-unread"]],
  });

  const deleteMutation = useApiMutation({
    mutationFn: deleteNotification,
    invalidateKeys: [["notifications"], ["notifications-unread"]],
    errorMessage: "Failed to delete notification",
  });

  const readAllMutation = useApiMutation<number, void>({
    mutationFn: markAllRead,
    invalidateKeys: [["notifications"], ["notifications-unread"]],
    successMessage: (count) => `Marked ${count} notification${count !== 1 ? "s" : ""} as read`,
    errorMessage: "Failed to mark all as read",
  });

  const unread = notifications.filter((n) => !n.read_at).length;

  return (
    <div className="page">
      <div className="page-header page-header--top">
        <div>
          <h1 className="page-title font-mono">
            <Bell size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
            Notifications
          </h1>
          {!isLoading && unread > 0 && (
            <p className="page-sub">{unread} unread</p>
          )}
        </div>
        {unread > 0 && (
          <button
            className="g-btn g-btn-ghost"
            onClick={() => readAllMutation.mutate()}
            disabled={readAllMutation.isPending}
          >
            <CheckCheck size={13} />
            Mark all read
          </button>
        )}
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={notifications}
        empty={
          <div className="empty-state g-card">
            <Bell size={24} style={{ color: "var(--g-text-muted)" }} />
            <p className="text-muted text-sm">No notifications yet.</p>
          </div>
        }
      >
        {(notifications) => (
          <div className="notif-list g-panel">
            {notifications.map((n) => (
              <NotificationRow
                key={n.id}
                n={n}
                onRead={(id) => readMutation.mutate(id)}
                onDelete={(id) => deleteMutation.mutate(id)}
                onInviteResolved={() => {
                  qc.invalidateQueries({ queryKey: ["notifications"] });
                  qc.invalidateQueries({ queryKey: ["notifications-unread"] });
                }}
              />
            ))}
          </div>
        )}
      </AsyncContent>
    </div>
  );
}
