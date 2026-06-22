"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState, useEffect } from "react";
import { TIMING } from "@/lib/config";

export function useCountdown(isoTarget: string | null | undefined): { label: string; remainingMs: number } {
  const [state, setState] = useState({ label: "", remainingMs: Infinity });

  useEffect(() => {
    if (!isoTarget) return;
    const tick = () => {
      const diff = new Date(isoTarget).getTime() - Date.now();
      if (diff <= 0) { setState({ label: "Expired", remainingMs: 0 }); return; }
      const h = Math.floor(diff / 3_600_000);
      const m = Math.floor((diff % 3_600_000) / 60_000);
      const s = Math.floor((diff % 60_000) / 1_000);
      setState({ label: h > 0 ? `${h}h ${m}m` : `${m}m ${s}s`, remainingMs: diff });
    };
    tick();
    const id = setInterval(tick, TIMING.CLOCK_TICK_MS);
    return () => clearInterval(id);
  }, [isoTarget]);

  return state;
}
