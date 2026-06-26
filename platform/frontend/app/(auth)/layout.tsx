"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useThemeStore } from "@/stores/theme.store";
import { useLocaleStore } from "@/stores/locale.store";
import { getPublicSettings } from "@/lib/api/settings";
import { STALE_TIME } from "@/lib/config";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
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

  return <>{children}</>;
}
