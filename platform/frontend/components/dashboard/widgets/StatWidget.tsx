"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useQuery } from "@tanstack/react-query";
import type { LucideIcon } from "lucide-react";
import { Server, Boxes, HardDrive, Database, LayoutGrid, Trophy, Star, Flame, CalendarClock, Timer } from "lucide-react";
import { getHealth } from "@/lib/api/system";
import { getLabs } from "@/lib/api/labs";
import { getMyProfile } from "@/lib/api/profiles";
import { getEvents } from "@/lib/api/events";
import { getScheduledActions } from "@/lib/api/scheduler";
import type { WidgetComponentProps, WidgetType } from "@/lib/widgets/types";

interface StatData {
  value: string | number;
  accentClass?: string;
  isLoading: boolean;
}

export const STAT_META: Partial<Record<WidgetType, { label: string; icon: LucideIcon }>> = {
  stat_running_labs: { label: "Running Labs", icon: Server },
  stat_total_containers: { label: "Total Containers", icon: Boxes },
  stat_docker: { label: "Docker", icon: HardDrive },
  stat_database: { label: "Database", icon: Database },
  stat_labs_available: { label: "Labs Available", icon: LayoutGrid },
  stat_my_solves: { label: "My Solves", icon: Trophy },
  stat_total_points: { label: "Total Points", icon: Star },
  stat_first_bloods: { label: "First Bloods", icon: Flame },
  stat_active_events: { label: "Active Events", icon: CalendarClock },
  stat_pending_actions: { label: "Pending Auto-Destroys", icon: Timer },
};

function useStatData(type: WidgetType): StatData {
  const health = useQuery({ queryKey: ["health"], queryFn: getHealth, refetchInterval: 30_000 });
  const labs = useQuery({ queryKey: ["labs"], queryFn: () => getLabs(), staleTime: 60_000 });
  const profile = useQuery({ queryKey: ["profile", "me"], queryFn: getMyProfile, staleTime: 60_000 });
  const events = useQuery({ queryKey: ["events", "running"], queryFn: () => getEvents("running"), staleTime: 30_000 });
  const pending = useQuery({
    queryKey: ["scheduled-actions", "pending"],
    queryFn: () => getScheduledActions("pending"),
    staleTime: 30_000,
  });

  switch (type) {
    case "stat_running_labs":
      return { value: health.data?.running_labs ?? "—", accentClass: "text-accent", isLoading: health.isLoading };
    case "stat_total_containers":
      return { value: health.data?.total_containers ?? "—", isLoading: health.isLoading };
    case "stat_docker":
      return {
        value: health.data?.docker === "ok" ? "Healthy" : "-",
        accentClass: health.data?.docker === "ok" ? "text-success" : "text-danger",
        isLoading: health.isLoading,
      };
    case "stat_database":
      return {
        value: health.data?.database === "ok" ? "Healthy" : "-",
        accentClass: health.data?.database === "ok" ? "text-success" : "text-danger",
        isLoading: health.isLoading,
      };
    case "stat_labs_available":
      return { value: labs.data?.length ?? "—", isLoading: labs.isLoading };
    case "stat_my_solves":
      return { value: profile.data?.solve_count ?? "—", accentClass: "text-accent", isLoading: profile.isLoading };
    case "stat_total_points":
      return { value: profile.data?.total_points ?? "—", accentClass: "text-accent", isLoading: profile.isLoading };
    case "stat_first_bloods":
      return { value: profile.data?.first_bloods ?? "—", accentClass: "text-danger", isLoading: profile.isLoading };
    case "stat_active_events":
      return { value: events.data?.length ?? "—", accentClass: "text-accent", isLoading: events.isLoading };
    case "stat_pending_actions":
      return { value: pending.data?.length ?? "—", isLoading: pending.isLoading };
    default:
      return { value: "—", isLoading: false };
  }
}

export function StatWidget({ widget }: WidgetComponentProps) {
  const meta = STAT_META[widget.type];
  const { value, accentClass, isLoading } = useStatData(widget.type);
  const Icon = meta?.icon;

  return (
    <div className="g-card stat-card">
      <span className="text-muted text-11 flex items-center gap-1">
        {Icon && <Icon size={11} />}
        {meta?.label ?? widget.type}
      </span>
      <span className={`stat-value ${accentClass ?? ""}`}>{isLoading ? "—" : value}</span>
    </div>
  );
}
