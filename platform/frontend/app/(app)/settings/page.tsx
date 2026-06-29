"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./settings.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Palette, User, Shield, FlaskConical, Settings as SettingsIcon, LayoutList } from "lucide-react";
import { NavigationSection } from "@/components/settings/NavigationSection";
import { changePassword, getMe } from "@/lib/api/auth";
import { updateMyProfile } from "@/lib/api/profiles";
import { useThemeStore } from "@/stores/theme.store";
import { useLocaleStore } from "@/stores/locale.store";
import { useUserStore } from "@/stores/user.store";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useDemoStore } from "@/stores/demo.store";
import { THEMES } from "@/lib/themes";
import { LOCALES } from "@/lib/i18n";
import { Button } from "@/components/ui/Button";

export default function SettingsPage() {
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");
  const { theme, setTheme } = useThemeStore();
  const { locale, setLocale } = useLocaleStore();
  const { user } = useUserStore();
  const { push } = useNotificationsStore();
  const { isDemoMode, toggle: toggleDemo } = useDemoStore();
  const [section, setSection] = useState<"appearance" | "navigation" | "account" | "demo">("appearance");

  const { data: me } = useQuery({ queryKey: ["me"], queryFn: getMe });

  const themeMutation = useApiMutation({
    mutationFn: (themeId: string) => updateMyProfile({ theme: themeId }),
    invalidateKeys: [],
    errorMessage: t("saveThemeError"),
  });

  const localeMutation = useApiMutation({
    mutationFn: (localeId: string) => updateMyProfile({ locale: localeId }),
    invalidateKeys: [],
    errorMessage: t("saveLocaleError"),
  });

  return (
    <div className="page">
      <h1 className="page-title font-mono">
        <SettingsIcon size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
        {t("title")}
      </h1>

      <div className="settings-layout">
        <nav className="settings-nav g-panel">
          {([
            { id: "appearance", label: t("navAppearance"), icon: <Palette size={15} /> },
            { id: "navigation", label: t("navNavigation"), icon: <LayoutList size={15} /> },
            { id: "account",    label: t("navAccount"),    icon: <User size={15} /> },
            { id: "demo",       label: t("navDemo"),       icon: <FlaskConical size={15} /> },
          ] as const).map((item) => (
            <button
              key={item.id}
              className={`settings-nav-item ${section === item.id ? "active" : ""}`}
              onClick={() => setSection(item.id)}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </nav>

        <div className="settings-content g-panel">
          {section === "appearance" && (
            <div>
              <h2 className="settings-section-title font-mono">{t("themeHeading")}</h2>
              <p className="text-muted text-sm mb-3">{t("themeDescription")}</p>
              <div className="theme-grid">
                {THEMES.map((th) => (
                  <button
                    key={th.id}
                    className={`theme-card ${theme === th.id ? "active" : ""}`}
                    onClick={() => { setTheme(th.id); themeMutation.mutate(th.id); }}
                    aria-pressed={theme === th.id}
                  >
                    <div className="theme-swatches">
                      {[th.preview.bg, th.preview.accent, th.preview.text].map((color, i) => (
                        <div key={i} className="theme-swatch" style={{ background: color }} />
                      ))}
                    </div>
                    <span className="theme-name text-11 font-mono">{th.name}</span>
                    {theme === th.id && <span className="theme-active-dot" />}
                  </button>
                ))}
              </div>

              <hr className="settings-divider" />

              <h2 className="settings-section-title font-mono">{t("languageHeading")}</h2>
              <p className="text-muted text-sm mb-3">{t("languageDescription")}</p>
              <div className="theme-grid">
                {LOCALES.map((l) => (
                  <button
                    key={l.id}
                    className={`theme-card ${locale === l.id ? "active" : ""}`}
                    onClick={() => { setLocale(l.id); localeMutation.mutate(l.id); }}
                    aria-pressed={locale === l.id}
                  >
                    <span className="theme-name text-11 font-mono">{l.nativeName}</span>
                    {locale === l.id && <span className="theme-active-dot" />}
                  </button>
                ))}
              </div>
            </div>
          )}

          {section === "navigation" && <NavigationSection />}

          {section === "demo" && (
            <div className="settings-section">
              <h2 className="settings-section-title font-mono">{t("demoHeading")}</h2>
              <p className="text-muted text-sm mb-3">{t("demoDescription")}</p>

              {isDemoMode && (
                <div className="admin-notice mb-3" style={{ borderColor: "var(--g-accent)", color: "var(--g-accent)" }}>
                  <FlaskConical size={13} />
                  <span className="text-11">{t("demoBannerOn")}</span>
                </div>
              )}

              <div className="meta-rows">
                <div className="meta-row" style={{ alignItems: "center" }}>
                  <span className="text-muted text-11">{t("demoModeLabel")}</span>
                  <label className="demo-toggle" style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer" }}>
                    <input
                      type="checkbox"
                      checked={isDemoMode}
                      onChange={() => {
                        toggleDemo();
                        setTimeout(() => window.location.reload(), 150);
                      }}
                      style={{ display: "none" }}
                    />
                    <span
                      className="demo-toggle-track"
                      style={{
                        display: "inline-flex",
                        width: "2.2rem",
                        height: "1.2rem",
                        borderRadius: 99,
                        background: isDemoMode ? "var(--g-accent)" : "var(--g-border)",
                        position: "relative",
                        transition: "background 0.15s",
                      }}
                    >
                      <span style={{
                        position: "absolute",
                        top: "0.15rem",
                        left: isDemoMode ? "calc(100% - 1.05rem)" : "0.15rem",
                        width: "0.9rem",
                        height: "0.9rem",
                        borderRadius: 99,
                        background: "white",
                        transition: "left 0.15s",
                      }} />
                    </span>
                    <span className="text-sm">{isDemoMode ? t("on") : t("off")}</span>
                  </label>
                </div>
              </div>

              <p className="text-muted" style={{ fontSize: "0.68rem", marginTop: "1rem" }}>
                {t("demoReloadNote")}
              </p>
            </div>
          )}

          {section === "account" && (
            <div className="settings-section">
              <h2 className="settings-section-title font-mono">{t("accountHeading")}</h2>
              <div className="meta-rows">
                <MetaRow label={tCommon("colUsername")} value={me?.username ?? user?.username ?? "—"} />
                <MetaRow label={tCommon("colEmail")} value={me?.email ?? user?.email ?? "—"} />
                <MetaRow
                  label={tCommon("colRole")}
                  value={(me?.permissions ?? user?.permissions)?.includes("admin.panel") ? t("roleAdministrator") : tCommon("colUser")}
                />
              </div>
              {(me?.permissions ?? user?.permissions)?.includes("admin.panel") && (
                <div className="admin-notice mt-3">
                  <Shield size={13} />
                  <span className="text-11 text-warning">{t("adminAccountNotice")}</span>
                </div>
              )}

              <hr className="settings-divider" />

              <h2 className="settings-section-title font-mono">{t("changePasswordHeading")}</h2>
              <ChangePasswordForm push={push} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="meta-row">
      <span className="text-muted text-11">{label}</span>
      <span className="text-sm text-secondary">{value}</span>
    </div>
  );
}

function ChangePasswordForm({ push }: { push: (type: "success" | "error", msg: string) => void }) {
  const t = useTranslations("settings");
  const tc = useTranslations("common");
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");

  const mutation = useApiMutation<void, void>({
    mutationFn: () => changePassword(current, next),
    invalidateKeys: [],
    successMessage: t("passwordChanged"),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("passwordChangeError"),
    onSuccess: () => {
      setCurrent(""); setNext(""); setConfirm("");
    },
  });

  const mismatch = next !== confirm && confirm.length > 0;
  const canSubmit = current && next && next === confirm && next.length >= 8;

  return (
    <form
      className="pw-form"
      onSubmit={(e) => { e.preventDefault(); if (canSubmit) mutation.mutate(); }}
    >
      <div className="settings-field">
        <label>{t("currentPasswordLabel")}</label>
        <input
          type="password"
          className="g-input"
          value={current}
          onChange={(e) => setCurrent(e.target.value)}
          autoComplete="current-password"
        />
      </div>
      <div className="settings-field">
        <label>{t("newPasswordLabel")} <span className="text-muted">{t("newPasswordHint")}</span></label>
        <input
          type="password"
          className="g-input"
          value={next}
          onChange={(e) => setNext(e.target.value)}
          autoComplete="new-password"
        />
      </div>
      <div className="settings-field">
        <label>{t("confirmPasswordLabel")}</label>
        <input
          type="password"
          className={`g-input ${mismatch ? "input-error" : ""}`}
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          autoComplete="new-password"
        />
        {mismatch && <span className="input-hint text-danger text-11">{t("passwordMismatch")}</span>}
      </div>
      <div className="settings-field" style={{ alignItems: "flex-start" }}>
        <Button
          type="submit"
          variant="primary"
          disabled={!canSubmit || mutation.isPending}
        >
          {mutation.isPending ? tc("saving") : t("updatePassword")}
        </Button>
      </div>
    </form>
  );
}
