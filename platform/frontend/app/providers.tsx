"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { WSProvider } from "@/providers/WSProvider";
import { IntlProvider } from "@/providers/IntlProvider";
import { useUserStore } from "@/stores/user.store";
import { refreshToken } from "@/lib/api/auth";
import { STALE_TIME } from "@/lib/config";

export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { staleTime: STALE_TIME.MEDIUM, retry: 1 } },
      })
  );

  // Access token lives only in memory; restore it via /auth/refresh's HttpOnly cookie on load
  useEffect(() => {
    const { user, accessToken, setAccessToken, clearSession, setIsRestoringToken } =
      useUserStore.getState();
    if (user && !accessToken) {
      refreshToken()
        .then(({ access_token }) => setAccessToken(access_token))
        .catch(() => clearSession())
        .finally(() => setIsRestoringToken(false));
    }
  }, []);

  return (
    <QueryClientProvider client={client}>
      <IntlProvider>
        <WSProvider>{children}</WSProvider>
      </IntlProvider>
    </QueryClientProvider>
  );
}
