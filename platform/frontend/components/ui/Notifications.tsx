"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { X } from "lucide-react";
import { clsx } from "clsx";
import { useNotificationsStore } from "@/stores/notifications.store";
import { Button } from "./Button";

export function Notifications() {
  const { items, dismiss } = useNotificationsStore();
  if (items.length === 0) return null;

  return (
    <div className="notifications-stack">
      {items.map((n) => (
        <div key={n.id} className={clsx("g-card notification", `notification--${n.kind}`)}>
          <span className="text-sm">{n.message}</span>
          <Button icon leftIcon={<X size={14} />} onClick={() => dismiss(n.id)} />
        </div>
      ))}

      <style>{`
        .notifications-stack {
          position: fixed;
          bottom: 1.5rem;
          right: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          z-index: var(--z-toast);
          max-width: 360px;
        }
        .notification {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          animation: slide-up 0.2s ease;
        }
        .notification--success { border-color: var(--g-success); }
        .notification--error   { border-color: var(--g-danger); }
        .notification--warning { border-color: var(--g-warning); }
        .notification--info    { border-color: var(--g-info); }
      `}</style>
    </div>
  );
}
