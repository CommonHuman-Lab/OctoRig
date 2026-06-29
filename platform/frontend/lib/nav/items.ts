// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import {
  LayoutDashboard, FlaskConical, Rocket, Swords, Flag, Award,
  Trophy, NotebookPen, Users, KeyRound,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export interface NavItem {
  href: string;
  icon: LucideIcon;
  key: string;
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/",             icon: LayoutDashboard, key: "dashboard" },
  { href: "/challenges",   icon: Swords,          key: "challenges" },
  { href: "/events",       icon: Flag,            key: "events" },
  { href: "/scoreboard",   icon: Trophy,          key: "scoreboard" },
  { href: "/badges",       icon: Award,           key: "badges" },
  { href: "/labs",         icon: FlaskConical,    key: "labs" },
  { href: "/notes",        icon: NotebookPen,     key: "notes" },
  { href: "/deployments",  icon: Rocket,          key: "deployments" },
  { href: "/teams",        icon: Users,           key: "teams" },
  { href: "/api-keys",     icon: KeyRound,        key: "apiKeys" },
];

export const NAV_KEYS = NAV_ITEMS.map((i) => i.key);
