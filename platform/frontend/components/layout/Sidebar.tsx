"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRef, useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  LayoutDashboard, FlaskConical, Rocket, Settings, LogOut, Users,
  KeyRound, ShieldCheck, Swords, Flag, Award, ChevronUp, Zap, PenTool,
  User, Trophy, PanelLeftClose, PanelLeftOpen,
} from "lucide-react";
import { getMyRank } from "@/lib/api/ranks";
import { clsx } from "clsx";
import { useUserStore } from "@/stores/user.store";
import { useThemeStore } from "@/stores/theme.store";
import { useSidebarStore } from "@/stores/sidebar.store";
import { logout } from "@/lib/api/auth";
import { getMyProfile } from "@/lib/api/profiles";

const NAV_MAIN = [
  { href: "/",             icon: LayoutDashboard, label: "Dashboard" },
  { href: "/challenges",   icon: Swords,          label: "Challenges" },
  { href: "/events",       icon: Flag,            label: "Events" },
  { href: "/scoreboard",   icon: Trophy,          label: "Scoreboard" },
  { href: "/badges",       icon: Award,           label: "Badges" },
  { href: "/labs",         icon: FlaskConical,    label: "Labs" },
  { href: "/deployments",  icon: Rocket,          label: "Deployments" },
  { href: "/teams",        icon: Users,           label: "Teams" },
  { href: "/api-keys",     icon: KeyRound,        label: "API Keys" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, clearSession } = useUserStore();
  const { resetExplicit } = useThemeStore();
  const { collapsed, toggleCollapsed } = useSidebarStore();
  const isPrivileged = user?.permissions?.includes("admin.panel") ?? false;
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const { data: profile } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: getMyProfile,
    staleTime: 60_000,
  });

  const { data: myRank } = useQuery({
    queryKey: ["rank", "me"],
    queryFn: getMyRank,
    staleTime: 60_000,
    enabled: !!user,
  });

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, [menuOpen]);

  async function handleLogout() {
    try { await logout(); } catch {}
    resetExplicit();
    clearSession();
    window.location.href = "/login";
  }

  function isActive(href: string) {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  }

  return (
    <aside
      className="shrink-0 flex flex-col h-full border-r"
      style={{
        background: "var(--g-chrome)",
        borderColor: "var(--g-border)",
        width: collapsed ? "3.25rem" : "13rem",
        transition: "width 0.18s cubic-bezier(0.16, 1, 0.3, 1)",
      }}
    >
      {/* Collapse toggle */}
      <div className={clsx("p-2 border-b shrink-0 flex", collapsed ? "justify-center" : "justify-end")} style={{ borderColor: "var(--g-border)" }}>
        <button
          onClick={toggleCollapsed}
          className="g-nav-item"
          style={{ padding: "0.375rem", justifyContent: "center" }}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <PanelLeftOpen size={14} style={{ color: "var(--g-text-muted)" }} />
          ) : (
            <PanelLeftClose size={14} style={{ color: "var(--g-text-muted)" }} />
          )}
        </button>
      </div>

      {/* Main nav */}
      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
        {NAV_MAIN.map(({ href, icon: Icon, label }) => {
          const active = isActive(href);
          return (
            <Link
              key={href}
              href={href}
              className={clsx("g-nav-item", active && "active", collapsed && "collapsed")}
              style={active ? {
                background: "var(--g-accent-dim)",
                color: "var(--g-text)",
                borderColor: "var(--g-border-hover)",
                justifyContent: collapsed ? "center" : undefined,
              } : { justifyContent: collapsed ? "center" : undefined }}
              title={label}
            >
              <Icon
                size={14}
                className="g-nav-icon shrink-0"
                style={{ color: active ? "var(--g-accent)" : "var(--g-text-muted)" }}
              />
              {!collapsed && (
                <span style={{ color: active ? "var(--g-text)" : "var(--g-text-muted)" }}>
                  {label}
                </span>
              )}
            </Link>
          );
        })}
        {user?.permissions?.includes("creator.access") && (() => {
          const active = isActive("/creator");
          return (
            <Link
              href="/creator"
              prefetch={false}
              className={clsx("g-nav-item", active && "active", collapsed && "collapsed")}
              style={active ? {
                background: "var(--g-accent-dim)",
                color: "var(--g-text)",
                borderColor: "var(--g-border-hover)",
                justifyContent: collapsed ? "center" : undefined,
              } : { justifyContent: collapsed ? "center" : undefined }}
              title="Creator"
            >
              <PenTool
                size={14}
                className="g-nav-icon shrink-0"
                style={{ color: active ? "var(--g-accent)" : "var(--g-text-muted)" }}
              />
              {!collapsed && (
                <span style={{ color: active ? "var(--g-text)" : "var(--g-text-muted)" }}>
                  Creator
                </span>
              )}
            </Link>
          );
        })()}
      </nav>

      {/* Admin entry — opens the separate admin area (its own sidebar/layout) */}
      {isPrivileged && (
        <div className="p-2 border-t shrink-0" style={{ borderColor: "var(--g-border)" }}>
          <Link href="/admin" className={clsx("g-nav-item", collapsed && "collapsed")} style={{ justifyContent: collapsed ? "center" : undefined }} title="Admin">
            <ShieldCheck size={14} className="g-nav-icon shrink-0" style={{ color: "var(--g-text-muted)" }} />
            {!collapsed && <span style={{ color: "var(--g-text-muted)" }}>Admin</span>}
          </Link>
        </div>
      )}

      {/* Footer — user card + inline menu */}
      <div
        ref={menuRef}
        className="sidebar-footer border-t shrink-0"
        style={{ borderColor: "var(--g-border)", position: "relative" }}
      >
        {/* Menu items — float above the trigger */}
        {menuOpen && (
          <div
            className="border rounded-t-lg overflow-hidden"
            style={{
              position: "absolute",
              bottom: "100%",
              left: 0,
              width: "13rem",
              borderColor: "var(--g-border)",
              background: "var(--g-chrome)",
              boxShadow: "0 -4px 16px rgba(0, 0, 0, 0.25)",
            }}
          >
            <Link
              href={`/profile/${user?.username}`}
              onClick={() => setMenuOpen(false)}
              className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-[var(--g-accent-dim)] transition-colors"
              style={{ color: "var(--g-text-muted)" }}
            >
              <User size={13} />
              My Profile
            </Link>
            <Link
              href="/settings"
              onClick={() => setMenuOpen(false)}
              className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-[var(--g-accent-dim)] transition-colors"
              style={{ color: "var(--g-text-muted)" }}
            >
              <Settings size={13} />
              Settings
            </Link>
            <div style={{ borderTop: "1px solid var(--g-border)" }} />
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-[var(--g-accent-dim)] transition-colors"
              style={{ color: "var(--g-danger, #f85149)" }}
            >
              <LogOut size={13} />
              Log Out
            </button>
          </div>
        )}

        {/* Trigger */}
        <button
          onClick={() => setMenuOpen((o) => !o)}
          className="w-full flex items-center gap-2 px-3 py-2 hover:bg-[var(--g-accent-dim)] transition-colors text-left"
          style={{ justifyContent: collapsed ? "center" : undefined }}
          title={collapsed ? user?.username ?? undefined : undefined}
        >
          {collapsed ? (
            <div
              className="rounded-full flex items-center justify-center shrink-0 font-mono font-semibold"
              style={{ width: 22, height: 22, fontSize: 11, background: "var(--g-accent-dim)", color: "var(--g-accent)" }}
            >
              {(user?.username?.[0] ?? "?").toUpperCase()}
            </div>
          ) : (
            <>
              <div className="flex-1 min-w-0">
                <div className="text-11 font-mono truncate" style={{ color: "var(--g-text)" }}>
                  {user?.username ?? "—"}
                </div>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <Zap size={10} style={{ color: "var(--g-accent)", flexShrink: 0 }} />
                  <span className="text-9px font-mono" style={{ color: "var(--g-accent)" }}>
                    {profile?.total_points?.toLocaleString() ?? "0"} pts
                  </span>
                  {profile?.solve_count !== undefined && (
                    <span className="text-9px font-mono" style={{ color: "var(--g-text-muted)" }}>
                      · {profile.solve_count} solve{profile.solve_count !== 1 ? "s" : ""}
                    </span>
                  )}
                </div>
                {myRank?.rank && (
                  <div className="flex items-center gap-1 mt-0.5">
                    <span
                      className="text-9px font-mono font-semibold"
                      style={{ color: myRank.rank.color ?? "var(--g-text-muted)" }}
                    >
                      {myRank.rank.name}
                    </span>
                  </div>
                )}
              </div>
              <ChevronUp
                size={12}
                className="shrink-0 transition-transform duration-150"
                style={{
                  color: "var(--g-text-muted)",
                  transform: menuOpen ? "rotate(180deg)" : "rotate(0deg)",
                }}
              />
            </>
          )}
        </button>
      </div>
    </aside>
  );
}
