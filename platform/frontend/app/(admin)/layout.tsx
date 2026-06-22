"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { AdminSidebar } from "@/components/layout/AdminSidebar";
import { Notifications } from "@/components/ui/Notifications";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { useUserStore } from "@/stores/user.store";
import { useThemeStore } from "@/stores/theme.store";
import { getPublicSettings } from "@/lib/api/settings";
import { STALE_TIME } from "@/lib/config";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { accessToken, _hasHydrated, isRestoringToken, user } = useUserStore();
  const { theme, applyPlatformDefault } = useThemeStore();
  const router = useRouter();

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    if (!_hasHydrated || isRestoringToken) return;
    if (!accessToken) { router.replace("/login"); return; }
    if (!user?.permissions?.includes("admin.panel")) router.replace("/");
  }, [_hasHydrated, isRestoringToken, accessToken, user, router]);

  const { data: publicSettings } = useQuery({
    queryKey: ["public-settings"],
    queryFn: getPublicSettings,
    staleTime: STALE_TIME.LONG,
    enabled: !!accessToken,
  });

  useEffect(() => {
    applyPlatformDefault(publicSettings?.default_theme);
  }, [publicSettings, applyPlatformDefault]);

  const isAdmin = user?.permissions?.includes("admin.panel") ?? false;

  // Wait for rehydration/redirects to settle before rendering the admin shell.
  if (!_hasHydrated || isRestoringToken || !accessToken || !isAdmin) return null;

  return (
    <>
      <div className="flex flex-1 overflow-hidden">
        <AdminSidebar />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
      <Notifications />
      <ConfirmModal />
    </>
  );
}
