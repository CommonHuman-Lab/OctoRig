// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import axios from "axios";
import { useUserStore } from "@/stores/user.store";
import { installDemoInterceptor } from "@/lib/demo/interceptor";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export const apiClient = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
  withCredentials: true, // send the HttpOnly refresh-token cookie on every request
});

apiClient.interceptors.request.use((config) => {
  const token = useUserStore.getState().accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 401 handling: attempt one silent refresh, retry the original request, then give up
let _refreshPromise: Promise<string> | null = null;

apiClient.interceptors.response.use(
  (r) => r,
  async (err) => {
    const original = err.config;

    if (
      err.response?.status !== 401 ||
      original._retried ||
      original.url?.includes("/auth/refresh")
    ) {
      return Promise.reject(err);
    }

    original._retried = true;

    try {
      // Deduplicate: if a refresh is already in flight, wait for it
      if (!_refreshPromise) {
        _refreshPromise = axios
          .post<{ access_token: string }>(
            `${API_BASE}/api/v1/auth/refresh`,
            {},
            { withCredentials: true }
          )
          .then((res) => res.data.access_token)
          .finally(() => { _refreshPromise = null; });
      }

      const newToken = await _refreshPromise;
      useUserStore.getState().setAccessToken(newToken);
      original.headers.Authorization = `Bearer ${newToken}`;
      return apiClient(original);
    } catch {
      // Refresh failed — session is gone
      useUserStore.getState().clearSession();
      if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
      return Promise.reject(err);
    }
  }
);

installDemoInterceptor(apiClient);
