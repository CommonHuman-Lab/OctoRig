"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../admin.css";
import "./settings.css";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { resetDatabase, restartPlatform } from "@/lib/api/admin";
import { getSiteSettings, updateSiteSettings, type SiteSettings } from "@/lib/api/settings";
import { useConfirmStore } from "@/stores/confirm.store";
import { useApiMutation } from "@/hooks/useApiMutation";
import { useUserStore } from "@/stores/user.store";
import { PlatformSection } from "@/components/admin/settings/PlatformSection";
import { ScoringSection } from "@/components/admin/settings/ScoringSection";
import { FeaturesSection } from "@/components/admin/settings/FeaturesSection";
import { BrandingSection } from "@/components/admin/settings/BrandingSection";
import { AppearanceSection } from "@/components/admin/settings/AppearanceSection";
import { DangerZone } from "@/components/admin/settings/DangerZone";

export default function AdminSettingsPage() {
  const { confirm } = useConfirmStore();
  const { user } = useUserStore();
  const router = useRouter();

  useEffect(() => {
    if (user && !user.permissions?.includes("admin.panel")) router.replace("/");
  }, [user, router]);

  const { data: settings, isLoading } = useQuery({
    queryKey: ["site-settings"],
    queryFn: getSiteSettings,
    enabled: !!user?.permissions?.includes("admin.panel"),
  });

  const [platform, setPlatform] = useState<Partial<SiteSettings>>({});
  const [scoring, setScoring] = useState<Partial<SiteSettings>>({});
  const [features, setFeatures] = useState<Partial<SiteSettings>>({});
  const [branding, setBranding] = useState<Partial<SiteSettings>>({});
  const [appearance, setAppearance] = useState<Partial<SiteSettings>>({});

  useEffect(() => {
    if (!settings) return;
    setPlatform({
      registration_open: settings.registration_open,
      maintenance_mode: settings.maintenance_mode,
      maintenance_message: settings.maintenance_message,
      max_flag_attempts: settings.max_flag_attempts,
    });
    setScoring({
      dynamic_scoring_enabled: settings.dynamic_scoring_enabled,
      dynamic_decay_factor: settings.dynamic_decay_factor,
      dynamic_min_floor_pct: settings.dynamic_min_floor_pct,
      scoreboard_frozen_at: settings.scoreboard_frozen_at,
      first_blood_enabled: settings.first_blood_enabled,
    });
    setFeatures({
      python_editor_enabled: settings.python_editor_enabled,
    });
    setBranding({
      company_name: settings.company_name,
      company_logo_url: settings.company_logo_url,
    });
    setAppearance({
      default_theme: settings.default_theme,
      default_locale: settings.default_locale,
    });
  }, [settings]);

  const saveMutation = useApiMutation({
    mutationFn: updateSiteSettings,
    invalidateKeys: [["site-settings"]],
    successMessage: "Settings saved",
    errorMessage: "Failed to save settings",
  });

  const resetDbMutation = useApiMutation<void, void>({
    mutationFn: resetDatabase,
    invalidateKeys: [],
    successMessage: "Database reset — all activity data cleared",
    errorMessage: "Failed to reset database",
  });

  function handleResetDb() {
    confirm({
      title: "Reset entire database?",
      body: "This will permanently delete ALL submissions, scores, hint unlocks, badges, event registrations, assessment invites & reports, deployments, notifications, sessions, and audit logs. Accounts, teams, labs, challenges, events, and assessment configs are kept. This cannot be undone.",
      confirmLabel: "Reset Database",
      dangerous: true,
      onConfirm: () => resetDbMutation.mutate(),
    });
  }

  const restartPlatformMutation = useApiMutation<void, void>({
    mutationFn: restartPlatform,
    invalidateKeys: [],
    successMessage: "Platform restarting — this may take a minute",
    errorMessage: "Failed to restart platform",
  });

  function handleRestartPlatform() {
    confirm({
      title: "Restart the platform?",
      body: "This stops every running lab, then restarts the API, worker, and frontend containers. The platform — including this page — will be briefly unreachable while it comes back up.",
      confirmLabel: "Restart Platform",
      dangerous: true,
      onConfirm: () => restartPlatformMutation.mutate(),
    });
  }

  if (isLoading || !settings) {
    return (
      <div className="page">
        <div className="page-header"><h1 className="page-title font-mono">Settings</h1></div>
        <p style={{ color: "var(--g-text-muted)", fontSize: "0.875rem" }}>Loading…</p>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Settings</h1>
      </div>

      <PlatformSection
        platform={platform}
        onChange={(patch) => setPlatform((p) => ({ ...p, ...patch }))}
        onSave={() => saveMutation.mutate(platform)}
        isPending={saveMutation.isPending}
      />

      <ScoringSection
        scoring={scoring}
        onChange={(patch) => setScoring((s) => ({ ...s, ...patch }))}
        onSave={() => saveMutation.mutate(scoring)}
        isPending={saveMutation.isPending}
      />

      <FeaturesSection
        features={features}
        onChange={(patch) => setFeatures((f) => ({ ...f, ...patch }))}
        onSave={() => saveMutation.mutate(features)}
        isPending={saveMutation.isPending}
      />

      <BrandingSection
        branding={branding}
        onChange={(patch) => setBranding((b) => ({ ...b, ...patch }))}
        onSave={() => saveMutation.mutate(branding)}
        isPending={saveMutation.isPending}
      />

      <AppearanceSection
        appearance={appearance}
        onChange={(patch) => setAppearance((a) => ({ ...a, ...patch }))}
        onSave={() => saveMutation.mutate(appearance)}
        isPending={saveMutation.isPending}
      />

      <DangerZone
        onResetDb={handleResetDb}
        isPending={resetDbMutation.isPending}
        onRestartPlatform={handleRestartPlatform}
        isRestartPending={restartPlatformMutation.isPending}
      />
    </div>
  );
}
