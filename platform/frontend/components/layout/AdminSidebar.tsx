"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  ShieldCheck, UserCog, FolderGit2, Container, ScrollText,
  Trophy, Flag, KeyRound, BarChart3, Zap, ClipboardList, Settings,
  ArrowLeft, LogOut, Boxes,
} from "lucide-react";
import { clsx } from "clsx";
import { useUserStore } from "@/stores/user.store";
import { useThemeStore } from "@/stores/theme.store";
import { useLocaleStore } from "@/stores/locale.store";
import { logout } from "@/lib/api/auth";
import { Brand } from "./Brand";

const NAV_ADMIN = [
  { href: "/admin",              icon: ShieldCheck,   key: "adminOverview" },
  { href: "/admin/users",        icon: UserCog,       key: "adminUsers" },
  { href: "/admin/roles",        icon: ShieldCheck,   key: "adminRoles" },
  { href: "/admin/teams",        icon: FolderGit2,    key: "teams" },
  { href: "/admin/labs",         icon: Boxes,         key: "labs" },
  { href: "/admin/deployments",  icon: Container,     key: "deployments" },
  { href: "/admin/audit",        icon: ScrollText,    key: "adminAuditLog" },
  { href: "/admin/challenges",   icon: Trophy,        key: "challenges" },
  { href: "/admin/events",       icon: Flag,          key: "events" },
  { href: "/admin/api-keys",     icon: KeyRound,      key: "apiKeys" },
  { href: "/admin/ranks",        icon: BarChart3,     key: "adminRanks" },
  { href: "/admin/assessments",  icon: Zap,           key: "adminAssessments" },
  { href: "/admin/content",      icon: ClipboardList, key: "adminContent" },
  { href: "/admin/settings",     icon: Settings,      key: "settings" },
] as const;

export function AdminSidebar() {
  const t = useTranslations("nav");
  const pathname = usePathname();
  const { user, clearSession } = useUserStore();
  const { resetExplicit } = useThemeStore();
  const { resetExplicit: resetLocaleExplicit } = useLocaleStore();

  function isActive(href: string) {
    if (href === "/admin") return pathname === "/admin";
    return pathname.startsWith(href);
  }

  async function handleLogout() {
    try { await logout(); } catch {}
    resetExplicit();
    resetLocaleExplicit();
    clearSession();
    window.location.href = "/login";
  }

  return (
    <aside
      className="w-52 shrink-0 flex flex-col h-full border-r"
      style={{ background: "var(--g-chrome)", borderColor: "var(--g-border)" }}
    >
      <div className="px-4 pt-2">
        <Brand />
      </div>
      {/* Back to platform */}
      <div className="p-2 border-b shrink-0" style={{ borderColor: "var(--g-border)" }}>
        <Link
          href="/"
          className="g-nav-item"
        >
          <ArrowLeft size={14} className="shrink-0" style={{ color: "var(--g-text-muted)" }} />
          <span style={{ color: "var(--g-text-muted)" }}>{t("backToPlatform")}</span>
        </Link>
      </div>

      <div className="px-3 pt-3 pb-1 shrink-0">
        <span
          className="text-9px font-mono uppercase"
          style={{ color: "var(--g-text-muted)", letterSpacing: "0.12em" }}
        >
          {t("adminSection")}
        </span>
      </div>

      {/* Admin nav */}
      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
        {NAV_ADMIN.map(({ href, icon: Icon, key }) => {
          const active = isActive(href);
          const label = t(key);
          return (
            <Link
              key={href}
              href={href}
              className={clsx("g-nav-item", active && "active")}
              style={active ? {
                background: "var(--g-accent-dim)",
                color: "var(--g-text)",
                borderColor: "var(--g-border-hover)",
              } : undefined}
              title={label}
            >
              <Icon
                size={14}
                className="shrink-0"
                style={{ color: active ? "var(--g-accent)" : "var(--g-text-muted)" }}
              />
              <span style={{ color: active ? "var(--g-text)" : "var(--g-text-muted)" }}>
                {label}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Footer — username + logout */}
      <div
        className="border-t shrink-0 flex items-center justify-between px-3 py-2"
        style={{ borderColor: "var(--g-border)" }}
      >
        <span className="text-11 font-mono truncate" style={{ color: "var(--g-text)" }}>
          {user?.username ?? "—"}
        </span>
        <button
          onClick={handleLogout}
          title={t("logOut")}
          className="flex items-center justify-center p-1 rounded hover:bg-[var(--g-accent-dim)] transition-colors"
          style={{ color: "var(--g-danger, #f85149)" }}
        >
          <LogOut size={13} />
        </button>
      </div>
    </aside>
  );
}
