// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { WidgetHeight, WidgetSpan, WidgetType } from "./types";

export interface PresetWidget {
  type: WidgetType;
  span: WidgetSpan;
  height: WidgetHeight;
}

export interface Preset {
  label: string;
  description: string;
  adminOnly?: boolean;
  widgets: PresetWidget[];
}

const stat = (type: WidgetType): PresetWidget => ({ type, span: 1, height: "sm" });
const panel = (type: WidgetType, span: WidgetSpan, height: WidgetHeight): PresetWidget => ({ type, span, height });

export const DEFAULT_PRESET_KEY = "default";

export const PRESETS: Record<string, Preset> = {
  default: {
    label: "Default",
    description: "The standard dashboard: system health, your stats, and your running labs.",
    widgets: [
      stat("stat_running_labs"),
      stat("stat_total_containers"),
      stat("stat_docker"),
      stat("stat_database"),
      stat("stat_labs_available"),
      stat("stat_my_solves"),
      stat("stat_total_points"),
      stat("stat_first_bloods"),
      panel("panel_active_deployments", 4, "md"),
      panel("panel_external_containers", 4, "md"),
    ],
  },
  competitor: {
    label: "Competitor",
    description: "Leaderboard, events, and fresh challenges front and centre.",
    widgets: [
      stat("stat_my_solves"),
      stat("stat_total_points"),
      stat("stat_first_bloods"),
      stat("stat_active_events"),
      panel("panel_scoreboard", 2, "md"),
      panel("panel_events", 2, "md"),
      panel("panel_challenges", 2, "md"),
      panel("panel_badges", 2, "md"),
    ],
  },
  minimal: {
    label: "Minimal",
    description: "Just the essentials — what's running, what's available, your progress.",
    widgets: [
      stat("stat_running_labs"),
      stat("stat_labs_available"),
      stat("stat_my_solves"),
      panel("panel_active_deployments", 4, "md"),
    ],
  },
  admin_overview: {
    label: "Admin Overview",
    description: "System health, active deployments, and recent platform activity.",
    adminOnly: true,
    widgets: [
      stat("stat_running_labs"),
      stat("stat_total_containers"),
      stat("stat_docker"),
      stat("stat_database"),
      panel("panel_active_deployments", 4, "md"),
      panel("panel_admin_activity", 2, "lg"),
      panel("panel_scheduled_actions", 2, "lg"),
    ],
  },
};

export const DEFAULT_WIDGETS = PRESETS[DEFAULT_PRESET_KEY].widgets;
