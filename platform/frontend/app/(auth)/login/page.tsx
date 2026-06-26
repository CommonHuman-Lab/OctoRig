"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./login.css";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { login, getMe } from "@/lib/api/auth";
import { useUserStore } from "@/stores/user.store";
import { Button } from "@/components/ui/Button";

export default function LoginPage() {
  const t = useTranslations("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { setSession, accessToken } = useUserStore();
  const router = useRouter();

  useEffect(() => {
    if (accessToken) router.replace("/");
  }, [accessToken, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const token = await login(username, password);
      useUserStore.getState().setAccessToken(token.access_token);
      const user = await getMe();
      setSession(user, token.access_token);
      router.replace("/");
    } catch (err: any) {
      const status = err?.response?.status;
      if (status === 429) {
        setError(err?.response?.data?.detail ?? t("tooManyAttempts"));
      } else {
        setError(t("invalidCredentials"));
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="g-card login-card">
        <div className="login-brand">
          <span style={{ color: "var(--g-accent)" }}>OCTO</span>
          <span style={{ color: "var(--g-text)" }}>RIG</span>
        </div>

        <form onSubmit={handleSubmit} className="login-form mt-4">
          <input
            className="g-input"
            type="text"
            placeholder={t("usernamePlaceholder")}
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            className="g-input"
            type="password"
            placeholder={t("passwordPlaceholder")}
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <p className="text-danger text-11">{error}</p>}
          <Button variant="primary" className="w-full" type="submit" disabled={loading}>
            {loading ? t("signingIn") : t("signIn")}
          </Button>
        </form>
      </div>

      <a
        href="https://github.com/CommonHuman-Lab"
        target="_blank"
        rel="noopener noreferrer"
        style={{
          position: "fixed",
          bottom: 16,
          left: "50%",
          transform: "translateX(-50%)",
          fontSize: "0.5625rem",
          fontFamily: "var(--font-mono, monospace)",
          letterSpacing: "0.06em",
          color: "var(--g-text-muted)",
          textDecoration: "none",
          opacity: 0.55,
        }}
      >
        {t("by")} CommonHuman
      </a>
    </div>
  );
}
