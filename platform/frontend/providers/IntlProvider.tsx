"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useEffect, useState } from "react";
import { NextIntlClientProvider } from "next-intl";
import { useLocaleStore } from "@/stores/locale.store";
import { DEFAULT_LOCALE, type LocaleId } from "@/lib/i18n";

import enAdmin from "@/messages/en/admin.json";
import enApiKeys from "@/messages/en/apiKeys.json";
import enAssessment from "@/messages/en/assessment.json";
import enBadges from "@/messages/en/badges.json";
import enChallenges from "@/messages/en/challenges.json";
import enCommon from "@/messages/en/common.json";
import enContent from "@/messages/en/content.json";
import enCreator from "@/messages/en/creator.json";
import enDashboard from "@/messages/en/dashboard.json";
import enDeployments from "@/messages/en/deployments.json";
import enEvents from "@/messages/en/events.json";
import enLabs from "@/messages/en/labs.json";
import enLogin from "@/messages/en/login.json";
import enNav from "@/messages/en/nav.json";
import enNotes from "@/messages/en/notes.json";
import enNotifications from "@/messages/en/notifications.json";
import enProfile from "@/messages/en/profile.json";
import enScoreboard from "@/messages/en/scoreboard.json";
import enSettings from "@/messages/en/settings.json";
import enTeams from "@/messages/en/teams.json";

const enMessages: Record<string, unknown> = {
  admin: enAdmin,
  apiKeys: enApiKeys,
  assessment: enAssessment,
  badges: enBadges,
  challenges: enChallenges,
  common: enCommon,
  content: enContent,
  creator: enCreator,
  dashboard: enDashboard,
  deployments: enDeployments,
  events: enEvents,
  labs: enLabs,
  login: enLogin,
  nav: enNav,
  notes: enNotes,
  notifications: enNotifications,
  profile: enProfile,
  scoreboard: enScoreboard,
  settings: enSettings,
  teams: enTeams,
};

async function loadFr(): Promise<Record<string, unknown>> {
  const [
    admin, apiKeys, assessment, badges, challenges, common, content,
    creator, dashboard, deployments, events, labs, login, nav,
    notes, notifications, profile, scoreboard, settings, teams,
  ] = await Promise.all([
    import("@/messages/fr/admin.json"),
    import("@/messages/fr/apiKeys.json"),
    import("@/messages/fr/assessment.json"),
    import("@/messages/fr/badges.json"),
    import("@/messages/fr/challenges.json"),
    import("@/messages/fr/common.json"),
    import("@/messages/fr/content.json"),
    import("@/messages/fr/creator.json"),
    import("@/messages/fr/dashboard.json"),
    import("@/messages/fr/deployments.json"),
    import("@/messages/fr/events.json"),
    import("@/messages/fr/labs.json"),
    import("@/messages/fr/login.json"),
    import("@/messages/fr/nav.json"),
    import("@/messages/fr/notes.json"),
    import("@/messages/fr/notifications.json"),
    import("@/messages/fr/profile.json"),
    import("@/messages/fr/scoreboard.json"),
    import("@/messages/fr/settings.json"),
    import("@/messages/fr/teams.json"),
  ]);
  return {
    admin: admin.default,
    apiKeys: apiKeys.default,
    assessment: assessment.default,
    badges: badges.default,
    challenges: challenges.default,
    common: common.default,
    content: content.default,
    creator: creator.default,
    dashboard: dashboard.default,
    deployments: deployments.default,
    events: events.default,
    labs: labs.default,
    login: login.default,
    nav: nav.default,
    notes: notes.default,
    notifications: notifications.default,
    profile: profile.default,
    scoreboard: scoreboard.default,
    settings: settings.default,
    teams: teams.default,
  };
}

const loaders: Record<LocaleId, () => Promise<Record<string, unknown>>> = {
  en: () => Promise.resolve(enMessages),
  fr: loadFr,
};

export function IntlProvider({ children }: { children: React.ReactNode }) {
  const { locale } = useLocaleStore();
  // Render English immediately so there's no blank flash; swap in the dynamic catalog once loaded.
  const [messages, setMessages] = useState<Record<string, unknown>>(enMessages);

  useEffect(() => {
    let cancelled = false;
    (loaders[locale] ?? loaders[DEFAULT_LOCALE])()
      .then((msgs) => { if (!cancelled) setMessages(msgs); })
      .catch(() => loaders[DEFAULT_LOCALE]().then((msgs) => { if (!cancelled) setMessages(msgs); }));
    return () => { cancelled = true; };
  }, [locale]);

  return (
    <NextIntlClientProvider
      locale={locale}
      messages={messages}
      onError={(e) => { if (process.env.NODE_ENV !== "production") console.error(e); }}
    >
      {children}
    </NextIntlClientProvider>
  );
}
