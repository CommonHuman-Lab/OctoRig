// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

export type WidgetCategory = "stat" | "panel";
export type WidgetSpan = 1 | 2 | 4 | 8;
export type WidgetHeight = "sm" | "md" | "lg";

export type WidgetType =
  | "stat_running_labs"
  | "stat_total_containers"
  | "stat_docker"
  | "stat_database"
  | "stat_labs_available"
  | "stat_my_solves"
  | "stat_total_points"
  | "stat_first_bloods"
  | "stat_active_events"
  | "stat_pending_actions"
  | "panel_active_deployments"
  | "panel_external_containers"
  | "panel_scoreboard"
  | "panel_badges"
  | "panel_events"
  | "panel_challenges"
  | "panel_scheduled_actions"
  | "panel_admin_activity";

export interface WidgetInstance {
  id: string;
  type: WidgetType;
  span: WidgetSpan;
  height: WidgetHeight;
}

export interface WidgetComponentProps {
  widget: WidgetInstance;
}
