// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect } from "react";
import { Save } from "lucide-react";
import { THEMES } from "@/lib/themes";
import type { SiteSettings } from "@/lib/api/settings";
import { useThemeStore } from "@/stores/theme.store";
import { SettingRow } from "./SettingRow";
import { Button } from "@/components/ui/Button";

export function AppearanceSection({
  appearance,
  onChange,
  onSave,
  isPending,
}: {
  appearance: Partial<SiteSettings>;
  onChange: (patch: Partial<SiteSettings>) => void;
  onSave: () => void;
  isPending: boolean;
}) {
  // Snap back to the admin's real theme on unmount so previewing the default doesn't stick
  useEffect(() => {
    return () => {
      document.documentElement.setAttribute("data-theme", useThemeStore.getState().theme);
    };
  }, []);

  return (
    <section className="admin-settings-section">
      <h2 className="admin-settings-section-title">Appearance</h2>
      <p className="settings-section-desc">
        Set the default theme for users who have not chosen one themselves.
        Users can override this from their personal settings.
      </p>

      <SettingRow
        label="Default Theme"
        description="Applied to new users and any user who has not explicitly chosen a theme."
        control={
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {THEMES.map((t) => {
              const isActive = (appearance.default_theme ?? "rose") === t.id;
              return (
                <button
                  key={t.id}
                  onClick={() => {
                    onChange({ default_theme: t.id });
                    document.documentElement.setAttribute("data-theme", t.id);
                  }}
                  title={t.name}
                  aria-pressed={isActive}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.375rem",
                    padding: "0.25rem 0.625rem",
                    borderRadius: "var(--g-radius, 4px)",
                    border: isActive
                      ? "1px solid var(--g-accent)"
                      : "1px solid var(--g-border)",
                    background: isActive
                      ? "color-mix(in srgb, var(--g-accent) 12%, transparent)"
                      : "transparent",
                    cursor: "pointer",
                    transition: "border-color 0.15s, background 0.15s",
                  }}
                >
                  <span style={{ display: "flex", gap: 3 }}>
                    {[t.preview.bg, t.preview.accent, t.preview.text].map((c, i) => (
                      <span
                        key={i}
                        style={{
                          width: 10,
                          height: 10,
                          borderRadius: 2,
                          background: c,
                          display: "inline-block",
                        }}
                      />
                    ))}
                  </span>
                  <span style={{
                    fontSize: "0.6875rem",
                    fontFamily: "var(--font-mono, monospace)",
                    color: isActive ? "var(--g-accent)" : "var(--g-text-muted)",
                    letterSpacing: "0.04em",
                  }}>
                    {t.name}
                  </span>
                </button>
              );
            })}
          </div>
        }
      />

      <div className="settings-row-actions">
        <Button
          variant="primary"
          size="sm"
          disabled={isPending}
          onClick={onSave}
          leftIcon={<Save size={13} />}
        >
          Save Appearance
        </Button>
      </div>
    </section>
  );
}
