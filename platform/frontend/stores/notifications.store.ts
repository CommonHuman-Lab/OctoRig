"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { create } from "zustand";
import { TIMING } from "@/lib/config";

export type NotificationKind = "success" | "error" | "warning" | "info";

export interface Notification {
  id: string;
  kind: NotificationKind;
  message: string;
}

interface NotificationsState {
  items: Notification[];
  push: (kind: NotificationKind, message: string) => void;
  pushPersistent: (kind: NotificationKind, message: string) => string;
  update: (id: string, kind: NotificationKind, message: string) => void;
  dismiss: (id: string) => void;
}

export const useNotificationsStore = create<NotificationsState>((set) => ({
  items: [],
  push: (kind, message) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    set((s) => ({ items: [...s.items, { id, kind, message }] }));
    setTimeout(() => set((s) => ({ items: s.items.filter((n) => n.id !== id) })), TIMING.TOAST_DURATION_MS);
  },
  pushPersistent: (kind, message) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    set((s) => ({ items: [...s.items, { id, kind, message }] }));
    return id;
  },
  update: (id, kind, message) => {
    set((s) => ({ items: s.items.map((n) => n.id === id ? { ...n, kind, message } : n) }));
    setTimeout(() => set((s) => ({ items: s.items.filter((n) => n.id !== id) })), TIMING.TOAST_DURATION_MS);
  },
  dismiss: (id) => set((s) => ({ items: s.items.filter((n) => n.id !== id) })),
}));
