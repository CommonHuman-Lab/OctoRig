"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useState, useRef, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import type { TeamRole } from "@/lib/api/teams";
import { ASSIGNABLE_ROLES, searchUsers } from "@/lib/api/teams";
import { Button } from "@/components/ui/Button";
import { STALE_TIME } from "@/lib/config";

export function InviteForm({
  onSubmit,
  isPending,
  onCancel,
}: {
  onSubmit: (username: string, role: TeamRole) => void;
  isPending: boolean;
  onCancel: () => void;
}) {
  const t = useTranslations("teams");
  const tc = useTranslations("common");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const [role, setRole] = useState<TeamRole>("member");
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const { data: results = [] } = useQuery({
    queryKey: ["user-search", query],
    queryFn: () => searchUsers(query),
    enabled: query.length >= 2,
    staleTime: STALE_TIME.INVITE,
  });

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  function handleSelect(username: string) {
    setSelected(username);
    setQuery(username);
    setOpen(false);
  }

  function handleSubmit() {
    if (!selected) return;
    onSubmit(selected, role);
    setQuery("");
    setSelected(null);
  }

  return (
    <div className="invite-form">
      <div ref={containerRef} style={{ position: "relative" }}>
        <input
          className="g-input g-input-sm"
          placeholder={t("searchUsernamePlaceholder")}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setSelected(null);
            setOpen(true);
          }}
          onFocus={() => query.length >= 2 && setOpen(true)}
          autoFocus
          autoComplete="off"
        />
        {open && results.length > 0 && (
          <div style={{
            position: "absolute", top: "100%", left: 0, right: 0, zIndex: "var(--z-popover)",
            background: "var(--g-surface)", border: "1px solid var(--g-border)",
            borderRadius: "6px", marginTop: "2px", overflow: "hidden",
            boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
          }}>
            {results.map((u) => (
              <div
                key={u.id}
                style={{
                  padding: "0.4rem 0.6rem", cursor: "pointer",
                  fontFamily: "var(--font-mono, monospace)", fontSize: "0.8rem",
                  color: "var(--g-text)",
                }}
                onMouseDown={() => handleSelect(u.username)}
                onMouseEnter={(e) => (e.currentTarget.style.background = "var(--g-surface-2)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "")}
              >
                {u.username}
              </div>
            ))}
          </div>
        )}
      </div>
      <select
        className="g-select g-select-sm"
        value={role}
        onChange={(e) => setRole(e.target.value as TeamRole)}
      >
        {ASSIGNABLE_ROLES.map((r) => (
          <option key={r} value={r}>
            {r.charAt(0).toUpperCase() + r.slice(1)}
          </option>
        ))}
      </select>
      <Button
        variant="primary"
        size="sm"
        onClick={handleSubmit}
        disabled={!selected || isPending}
      >
        {isPending ? t("sending") : t("invite")}
      </Button>
      <Button size="sm" onClick={onCancel}>
        {tc("cancel")}
      </Button>
    </div>
  );
}
