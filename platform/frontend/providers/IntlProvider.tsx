"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useEffect, useState } from "react";
import { NextIntlClientProvider } from "next-intl";
import { useLocaleStore } from "@/stores/locale.store";
import { DEFAULT_LOCALE, type LocaleId } from "@/lib/i18n";
import enMessages from "@/messages/en.json";

const loaders: Record<LocaleId, () => Promise<{ default: Record<string, unknown> }>> = {
  en: () => Promise.resolve({ default: enMessages }),
  fr: () => import("@/messages/fr.json"),
};

export function IntlProvider({ children }: { children: React.ReactNode }) {
  const { locale } = useLocaleStore();
  // Render English immediately so there's no blank flash; swap in the dynamic catalog once loaded.
  const [messages, setMessages] = useState<Record<string, unknown>>(enMessages);

  useEffect(() => {
    let cancelled = false;
    (loaders[locale] ?? loaders[DEFAULT_LOCALE])()
      .then((mod) => { if (!cancelled) setMessages(mod.default); })
      .catch(() => loaders[DEFAULT_LOCALE]().then((mod) => { if (!cancelled) setMessages(mod.default); }));
    return () => { cancelled = true; };
  }, [locale]);

  return (
    <NextIntlClientProvider locale={locale} messages={messages} onError={() => {}}>
      {children}
    </NextIntlClientProvider>
  );
}
