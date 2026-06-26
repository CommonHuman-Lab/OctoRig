// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useThemeStore } from "@/stores/theme.store";
import { useLocaleStore } from "@/stores/locale.store";
import { getPublicSettings } from "@/lib/api/settings";
import { Notifications } from "@/components/ui/Notifications";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { STALE_TIME } from "@/lib/config";

export default function AssessmentLayout({ children }: { children: React.ReactNode }) {
  const t = useTranslations("login");
  const { theme, applyPlatformDefault } = useThemeStore();
  const { applyPlatformDefault: applyLocalePlatformDefault } = useLocaleStore();

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const { data: publicSettings } = useQuery({
    queryKey: ["public-settings"],
    queryFn: getPublicSettings,
    staleTime: STALE_TIME.LONG,
  });

  useEffect(() => {
    applyPlatformDefault(publicSettings?.default_theme);
    applyLocalePlatformDefault(publicSettings?.default_locale);
  }, [publicSettings, applyPlatformDefault, applyLocalePlatformDefault]);

  return (
    <>
      <main style={{ minHeight: "calc(100vh - 36px)", overflowY: "auto" }}>
        {children}
      </main>
      <footer
        style={{
          height: 36,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderTop: "1px solid var(--g-border)",
          background: "var(--g-chrome)",
        }}
      >
        <a
          href="https://github.com/CommonHuman-Lab"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            fontSize: "0.625rem",
            fontFamily: "var(--font-mono, monospace)",
            letterSpacing: "0.06em",
            color: "var(--g-text-muted)",
            textDecoration: "none",
            opacity: 0.6,
          }}
        >
          {t("by")} CommonHuman
        </a>
      </footer>
      <Notifications />
      <ConfirmModal />
    </>
  );
}
