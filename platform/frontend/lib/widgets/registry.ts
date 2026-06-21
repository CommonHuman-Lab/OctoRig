// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { ComponentType } from "react";
import { Server, Boxes, HardDrive, Database, LayoutGrid, Trophy, Star, Flame, CalendarClock, Timer, Award, Flag, ShieldCheck } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { WidgetCategory, WidgetComponentProps, WidgetHeight, WidgetSpan, WidgetType } from "./types";
import { StatWidget } from "@/components/dashboard/widgets/StatWidget";
import { ActiveDeploymentsWidget } from "@/components/dashboard/widgets/ActiveDeploymentsWidget";
import { ExternalContainersWidget } from "@/components/dashboard/widgets/ExternalContainersWidget";
import { ScoreboardPreviewWidget } from "@/components/dashboard/widgets/ScoreboardPreviewWidget";
import { RecentBadgesWidget } from "@/components/dashboard/widgets/RecentBadgesWidget";
import { UpcomingEventsWidget } from "@/components/dashboard/widgets/UpcomingEventsWidget";
import { RecentChallengesWidget } from "@/components/dashboard/widgets/RecentChallengesWidget";
import { ScheduledActionsWidget } from "@/components/dashboard/widgets/ScheduledActionsWidget";
import { AdminActivityWidget } from "@/components/dashboard/widgets/AdminActivityWidget";

export interface WidgetRegistryEntry {
  label: string;
  description: string;
  icon: LucideIcon;
  category: WidgetCategory;
  defaultSpan: WidgetSpan;
  defaultHeight: WidgetHeight;
  adminOnly?: boolean;
  component: ComponentType<WidgetComponentProps>;
}

export const WIDGET_REGISTRY: Record<WidgetType, WidgetRegistryEntry> = {
  stat_running_labs: {
    label: "Running Labs", description: "How many lab containers are running right now.",
    icon: Server, category: "stat", defaultSpan: 1, defaultHeight: "sm", component: StatWidget,
  },
  stat_total_containers: {
    label: "Total Containers", description: "Total OctoRig containers across all deployments.",
    icon: Boxes, category: "stat", defaultSpan: 1, defaultHeight: "sm", component: StatWidget,
  },
  stat_docker: {
    label: "Docker Status", description: "Health of the Docker daemon.",
    icon: HardDrive, category: "stat", defaultSpan: 1, defaultHeight: "sm", component: StatWidget,
  },
  stat_database: {
    label: "Database Status", description: "Health of the platform database.",
    icon: Database, category: "stat", defaultSpan: 1, defaultHeight: "sm", component: StatWidget,
  },
  stat_labs_available: {
    label: "Labs Available", description: "Number of lab templates in the catalog.",
    icon: LayoutGrid, category: "stat", defaultSpan: 1, defaultHeight: "sm", component: StatWidget,
  },
  stat_my_solves: {
    label: "My Solves", description: "Challenges you've solved.",
    icon: Trophy, category: "stat", defaultSpan: 1, defaultHeight: "sm", component: StatWidget,
  },
  stat_total_points: {
    label: "Total Points", description: "Your total scored points.",
    icon: Star, category: "stat", defaultSpan: 1, defaultHeight: "sm", component: StatWidget,
  },
  stat_first_bloods: {
    label: "First Bloods", description: "Challenges you were first to solve.",
    icon: Flame, category: "stat", defaultSpan: 1, defaultHeight: "sm", component: StatWidget,
  },
  stat_active_events: {
    label: "Active Events", description: "CTF events currently running.",
    icon: CalendarClock, category: "stat", defaultSpan: 1, defaultHeight: "sm", component: StatWidget,
  },
  stat_pending_actions: {
    label: "Pending Auto-Destroys", description: "Your deployments queued for automatic teardown.",
    icon: Timer, category: "stat", defaultSpan: 1, defaultHeight: "sm", component: StatWidget,
  },
  panel_active_deployments: {
    label: "Active Deployments", description: "Your running labs, with quick stop actions.",
    icon: Server, category: "panel", defaultSpan: 4, defaultHeight: "md", component: ActiveDeploymentsWidget,
  },
  panel_external_containers: {
    label: "Externally Managed", description: "Containers started via the CLI, outside the platform.",
    icon: Boxes, category: "panel", defaultSpan: 4, defaultHeight: "md", component: ExternalContainersWidget,
  },
  panel_scoreboard: {
    label: "Global Scoreboard", description: "Top-ranked players across the platform.",
    icon: Trophy, category: "panel", defaultSpan: 2, defaultHeight: "md", component: ScoreboardPreviewWidget,
  },
  panel_badges: {
    label: "Recent Badges", description: "Badges you've recently earned.",
    icon: Award, category: "panel", defaultSpan: 2, defaultHeight: "md", component: RecentBadgesWidget,
  },
  panel_events: {
    label: "Events", description: "Upcoming and running CTF events.",
    icon: CalendarClock, category: "panel", defaultSpan: 2, defaultHeight: "md", component: UpcomingEventsWidget,
  },
  panel_challenges: {
    label: "New Challenges", description: "Active challenges you haven't solved yet.",
    icon: Flag, category: "panel", defaultSpan: 2, defaultHeight: "md", component: RecentChallengesWidget,
  },
  panel_scheduled_actions: {
    label: "My Scheduled Actions", description: "Your upcoming auto-destroy and scheduled actions.",
    icon: Timer, category: "panel", defaultSpan: 2, defaultHeight: "md", component: ScheduledActionsWidget,
  },
  panel_admin_activity: {
    label: "Admin: Recent Activity", description: "Latest audit log entries across the platform.",
    icon: ShieldCheck, category: "panel", defaultSpan: 2, defaultHeight: "md", adminOnly: true, component: AdminActivityWidget,
  },
};

export const WIDGET_TYPES = Object.keys(WIDGET_REGISTRY) as WidgetType[];
