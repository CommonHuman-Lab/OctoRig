"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useState } from "react";
import { Palette, X } from "lucide-react";
import { clsx } from "clsx";
import { THEMES, type ThemeId } from "@/lib/themes";
import { useThemeStore } from "@/stores/theme.store";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { Button } from "./Button";

export function ThemeModal() {
  const [open, setOpen] = useState(false);
  const { theme, setTheme } = useThemeStore();

  function pick(id: ThemeId) {
    setTheme(id);
    setOpen(false);
  }

  useEscapeKey(() => setOpen(false), open);

  return (
    <>
      <Button icon leftIcon={<Palette size={16} />} onClick={() => setOpen(true)} tooltip="Change theme" />

      {open && (
        <div className="g-backdrop" onClick={() => setOpen(false)}>
          <div className="g-modal theme-modal" onClick={(e) => e.stopPropagation()}>
            <div className="g-modal-header">
              <span className="font-mono text-sm">THEME</span>
              <Button icon leftIcon={<X size={16} />} onClick={() => setOpen(false)} />
            </div>
            <div className="theme-grid">
              {THEMES.map((t) => (
                <button
                  key={t.id}
                  className={clsx("theme-card", theme === t.id && "theme-card--active")}
                  onClick={() => pick(t.id)}
                  style={{ background: t.preview.bg, borderColor: theme === t.id ? t.preview.accent : t.preview.border }}
                >
                  <div className="theme-swatch" style={{ background: t.preview.accent }} />
                  <div>
                    <p className="text-sm font-mono" style={{ color: t.preview.text }}>{t.name}</p>
                    <p className="text-10" style={{ color: t.preview.dim }}>{t.hint}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <style>{`
        .theme-modal { max-width: 480px; width: 100%; }
        .theme-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; padding: 1rem; }
        .theme-card {
          display: flex; align-items: center; gap: 0.75rem;
          padding: 0.75rem; border-radius: 0.5rem; border: 1px solid;
          cursor: pointer; text-align: left; transition: border-color 0.15s;
        }
        .theme-card--active { outline: 2px solid var(--g-accent); outline-offset: 1px; }
        .theme-swatch { width: 24px; height: 24px; border-radius: 50%; flex-shrink: 0; }
      `}</style>
    </>
  );
}
