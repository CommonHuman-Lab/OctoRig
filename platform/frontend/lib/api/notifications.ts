// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { apiClient } from "./client";
import { PAGINATION } from "@/lib/config";

export interface AppNotification {
  id: number;
  type: string;
  title: string;
  body: string | null;
  data: Record<string, unknown>;
  read_at: string | null;
  created_at: string;
}

export interface NotificationPreferences {
  in_app: boolean;
  email: boolean;
  discord_webhook_url: string | null;
  slack_webhook_url: string | null;
  event_filter: Record<string, boolean>;
}

export async function getNotifications(unreadOnly = false, limit: number = PAGINATION.DEFAULT_LIMIT): Promise<AppNotification[]> {
  const { data } = await apiClient.get<AppNotification[]>("/notifications/", {
    params: { unread_only: unreadOnly, limit },
  });
  return data;
}

export async function getUnreadCount(): Promise<number> {
  const { data } = await apiClient.get<{ count: number }>("/notifications/unread-count");
  return data.count;
}

export async function markRead(id: number): Promise<void> {
  await apiClient.post(`/notifications/${id}/read`);
}

export async function markAllRead(): Promise<number> {
  const { data } = await apiClient.post<{ marked: number }>("/notifications/read-all");
  return data.marked;
}

export async function deleteNotification(id: number): Promise<void> {
  await apiClient.delete(`/notifications/${id}`);
}

export async function getNotificationPreferences(): Promise<NotificationPreferences> {
  const { data } = await apiClient.get<NotificationPreferences>("/notifications/preferences");
  return data;
}
