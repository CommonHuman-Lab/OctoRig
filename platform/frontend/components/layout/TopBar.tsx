"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Bell } from "lucide-react";
import { getHealth } from "@/lib/api/system";
import { getUnreadCount } from "@/lib/api/notifications";
import { Brand } from "@/components/layout/Brand";

export function TopBar() {
  const { data: health } = useQuery({
    queryKey: ["system-health"],
    queryFn: getHealth,
  });

  const { data: unreadCount = 0 } = useQuery({
    queryKey: ["notifications-unread"],
    queryFn: getUnreadCount,
  });

  const dockerOk = health?.docker === "ok";

  return (
    <header
      className="h-10 shrink-0 flex items-center justify-between px-4 border-b backdrop-blur-xl select-none z-20"
      style={{ background: "var(--g-overlay)", borderColor: "var(--g-border)" }}
    >
      {/* Brand */}
      <div className="flex items-center gap-2">
        <Brand />
      </div>

      {/* Status + notifications */}
      <div className="flex items-center gap-4">
        {health && (
          <div className="flex items-center gap-1.5">
            <span
              className={dockerOk ? "g-dot g-dot-success" : "g-dot g-dot-danger"}
              title={dockerOk ? "Docker connected" : "Docker error"}
            />
            <span className="font-mono text-10px" style={{ color: "var(--g-text-muted)" }}>
              {health.running_labs} running
            </span>
          </div>
        )}

        <Link
          href="/notifications"
          className="relative flex items-center"
          style={{ color: "var(--g-text-muted)" }}
          aria-label="Notifications"
        >
          <Bell size={14} />
          {unreadCount > 0 && (
            <span
              className="absolute font-mono font-bold flex items-center justify-center animate-pulse"
              style={{
                top: "-5px", right: "-6px",
                minWidth: "14px", height: "14px",
                borderRadius: "7px",
                background: "var(--g-danger)",
                color: "#fff",
                fontSize: "0.5rem",
                padding: "0 3px",
              }}
            >
              {unreadCount > 99 ? "99+" : unreadCount}
            </span>
          )}
        </Link>
      </div>
    </header>
  );
}
