"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { clsx } from "clsx";
import { useTranslations } from "next-intl";
import { Server, LayoutDashboard, FileText } from "lucide-react";

export const SECTIONS = [
  { id: "overview", labelKey: "tabOverview", icon: LayoutDashboard },
  { id: "labs", labelKey: "tabLabs", icon: Server },
  { id: "report", labelKey: "tabReport", icon: FileText },
] as const;

export type SectionId = (typeof SECTIONS)[number]["id"];

export function WorkspaceSidebar({ active, onSelect }: { active: SectionId; onSelect: (id: SectionId) => void }) {
  const t = useTranslations("assessment");
  const tn = useTranslations("nav");
  return (
    <aside
      className="w-44 shrink-0 flex flex-col"
      style={{ borderRight: "1px solid var(--g-border)", background: "var(--g-chrome)" }}
    >
      <nav className="p-2 space-y-0.5">
        {SECTIONS.map(({ id, labelKey, icon: Icon }) => {
          const label = labelKey === "tabLabs" ? tn("labs") : t(labelKey);
          const isActive = active === id;
          return (
            <button
              key={id}
              onClick={() => onSelect(id)}
              className={clsx("g-nav-item w-full text-left", isActive && "active")}
              style={isActive ? {
                background: "var(--g-accent-dim)",
                color: "var(--g-text)",
                borderColor: "var(--g-border-hover)",
              } : undefined}
            >
              <Icon
                size={14}
                className="shrink-0"
                style={{ color: isActive ? "var(--g-accent)" : "var(--g-text-muted)" }}
              />
              <span style={{ color: isActive ? "var(--g-text)" : "var(--g-text-muted)" }}>
                {label}
              </span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
