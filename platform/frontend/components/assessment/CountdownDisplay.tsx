"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Clock } from "lucide-react";
import { TIMING } from "@/lib/config";

function useCountdown(expiresAt: string | null) {
  const [remaining, setRemaining] = useState<number | null>(null);

  useEffect(() => {
    if (!expiresAt) { setRemaining(null); return; }
    const update = () => {
      const diff = Math.max(0, Math.floor((new Date(expiresAt).getTime() - Date.now()) / 1000));
      setRemaining(diff);
    };
    update();
    const id = setInterval(update, TIMING.CLOCK_TICK_MS);
    return () => clearInterval(id);
  }, [expiresAt]);

  return remaining;
}

export function CountdownDisplay({ expiresAt }: { expiresAt: string | null }) {
  const t = useTranslations("assessment");
  const remaining = useCountdown(expiresAt);

  if (remaining === null) return null;

  const expired = remaining === 0;
  const h = Math.floor(remaining / 3600);
  const m = Math.floor((remaining % 3600) / 60);
  const s = remaining % 60;
  const formatted = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        fontFamily: "var(--font-mono, monospace)",
        fontSize: "1.2rem",
        fontWeight: 700,
        color: expired ? "var(--g-danger)" : remaining < 3600 ? "var(--g-warning, #f59e0b)" : "var(--g-text)",
      }}
    >
      <Clock size={18} />
      {expired ? t("expiredBadge") : formatted}
    </div>
  );
}
