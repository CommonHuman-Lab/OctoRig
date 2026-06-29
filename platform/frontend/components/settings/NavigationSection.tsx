"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { useTranslations } from "next-intl";
import { GripVertical, Eye, EyeOff, RotateCcw } from "lucide-react";
import { useSidebarStore } from "@/stores/sidebar.store";
import { NAV_ITEMS } from "@/lib/nav/items";
import { Button } from "@/components/ui/Button";

export function NavigationSection() {
  const t = useTranslations("settings");
  const tNav = useTranslations("nav");
  const { order, hidden, reorderNav, toggleNavHidden, resetNav } = useSidebarStore();
  const [dragKey, setDragKey] = useState<string | null>(null);
  const [dragOverKey, setDragOverKey] = useState<string | null>(null);

  const items = order
    .map((key) => NAV_ITEMS.find((i) => i.key === key))
    .filter((i): i is (typeof NAV_ITEMS)[number] => Boolean(i));

  return (
    <div className="settings-section">
      <h2 className="settings-section-title font-mono">{t("navigationHeading")}</h2>
      <p className="text-muted text-sm mb-3">{t("navigationDescription")}</p>

      <div className="nav-customize-list">
        {items.map(({ key, icon: Icon }) => {
          const isHidden = hidden.includes(key);
          return (
            <div
              key={key}
              className={[
                "nav-customize-item",
                dragKey === key ? "dash-dragging" : "",
                dragOverKey === key && dragKey !== key ? "dash-drag-over" : "",
                isHidden ? "nav-customize-item-hidden" : "",
              ].filter(Boolean).join(" ")}
              draggable
              onDragStart={() => setDragKey(key)}
              onDragEnd={() => { setDragKey(null); setDragOverKey(null); }}
              onDragOver={(e) => { e.preventDefault(); setDragOverKey(key); }}
              onDrop={(e) => {
                e.preventDefault();
                if (dragKey && dragKey !== key) reorderNav(dragKey, key);
                setDragKey(null);
                setDragOverKey(null);
              }}
            >
              <GripVertical size={13} className="dash-widget-grip" />
              <Icon size={14} style={{ color: "var(--g-text-muted)" }} />
              <span className="text-sm" style={{ flex: 1 }}>{tNav(key)}</span>
              {isHidden && <span className="text-muted text-9px">{t("navigationHidden")}</span>}
              <Button
                size="sm"
                icon
                leftIcon={isHidden ? <Eye size={12} /> : <EyeOff size={12} />}
                variant="ghost"
                onClick={() => toggleNavHidden(key)}
                tooltip={isHidden ? t("navigationShow") : t("navigationHide")}
              />
            </div>
          );
        })}
      </div>

      <Button
        size="sm"
        variant="ghost"
        leftIcon={<RotateCcw size={12} />}
        onClick={resetNav}
        style={{ marginTop: "0.75rem" }}
      >
        {t("navigationReset")}
      </Button>
    </div>
  );
}
