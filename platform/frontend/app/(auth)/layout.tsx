"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useThemeStore } from "@/stores/theme.store";
import { getPublicSettings } from "@/lib/api/settings";
import { STALE_TIME } from "@/lib/config";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const { theme, applyPlatformDefault } = useThemeStore();

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
  }, [publicSettings, applyPlatformDefault]);

  return <>{children}</>;
}
