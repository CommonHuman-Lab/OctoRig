"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { Shield, Clock, Server, AlertTriangle } from "lucide-react";
import { getInviteLanding, acceptInvite } from "@/lib/api/assessments";
import { login, getMe } from "@/lib/api/auth";
import { useUserStore } from "@/stores/user.store";
import { useNotificationsStore } from "@/stores/notifications.store";
import { Button } from "@/components/ui/Button";

export default function InviteLandingPage() {
  const t = useTranslations("assessment");
  const tl = useTranslations("login");
  const tc = useTranslations("common");
  const { token } = useParams<{ token: string }>();
  const router = useRouter();
  const { push } = useNotificationsStore();
  const { accessToken, user, setSession } = useUserStore();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  const { data: landing, isLoading, error } = useQuery({
    queryKey: ["invite-landing", token],
    queryFn: () => getInviteLanding(token),
    retry: false,
  });

  // Already accepted by this user — redirect straight to workspace
  useEffect(() => {
    if (landing?.status === "active" && accessToken) {
      router.replace("/assessment");
    }
  }, [landing, accessToken, router]);

  const acceptMutation = useMutation({
    mutationFn: () => acceptInvite(token, { username, password }),
    onSuccess: async (data) => {
      const { getMe } = await import("@/lib/api/auth");
      const me = await getMe();
      setSession(me, data.access_token);
      push("success", t("welcomeToast"));
      router.replace("/assessment");
    },
    onError: (err: any) =>
      push("error", err?.response?.data?.detail ?? t("registrationFailed")),
  });

  const loginMutation = useMutation({
    mutationFn: () => login(loginUsername, loginPassword),
    onSuccess: async (data) => {
      const me = await getMe();
      setSession(me, data.access_token);
      router.replace("/assessment");
    },
    onError: () => push("error", tl("invalidCredentials")),
  });

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (password !== confirm) {
      push("error", t("passwordsDontMatch"));
      return;
    }
    if (password.length < 8) {
      push("error", t("passwordTooShort"));
      return;
    }
    acceptMutation.mutate();
  }

  if (isLoading) {
    return (
      <div style={outerStyle}>
        <p style={{ color: "var(--g-text-muted)" }}>{t("loadingInvite")}</p>
      </div>
    );
  }

  if (error || !landing) {
    return (
      <div style={outerStyle}>
        <div style={cardStyle}>
          <AlertTriangle size={36} style={{ color: "var(--g-danger)", marginBottom: 12 }} />
          <h1 style={headingStyle}>{t("inviteNotFoundTitle")}</h1>
          <p style={{ color: "var(--g-text-muted)", textAlign: "center", maxWidth: 360 }}>
            {t("inviteNotFoundLinkBody")}
          </p>
        </div>
      </div>
    );
  }

  if (landing.status === "revoked" || landing.status === "expired") {
    return (
      <div style={outerStyle}>
        <div style={cardStyle}>
          <AlertTriangle size={36} style={{ color: "var(--g-danger)", marginBottom: 12 }} />
          <h1 style={headingStyle}>
            {landing.status === "revoked" ? t("inviteRevokedTitle") : t("inviteExpiredTitle")}
          </h1>
          <p style={{ color: "var(--g-text-muted)", textAlign: "center", maxWidth: 360 }}>
            {landing.status === "revoked" ? t("inviteRevokedBody") : t("inviteExpiredBody")}
          </p>
        </div>
      </div>
    );
  }

  const companyName = landing.company_name || "OctoRig";

  return (
    <div style={outerStyle}>
      <div style={{ ...cardStyle, maxWidth: 520 }}>
        {/* Header */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginBottom: 28 }}>
          {landing.company_logo_url ? (
            <img
              src={landing.company_logo_url}
              alt={companyName}
              style={{ height: 48, objectFit: "contain", marginBottom: 12 }}
            />
          ) : (
            <Shield size={40} style={{ color: "var(--g-accent)", marginBottom: 12 }} />
          )}
          <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--g-text-muted)", marginBottom: 4 }}>
            {companyName}
          </div>
          <h1 style={{ ...headingStyle, fontSize: "1.4rem" }}>{landing.assessment_name}</h1>
          {landing.candidate_name && (
            <p style={{ color: "var(--g-text-muted)", fontSize: "0.875rem", marginTop: 4 }}>
              {t("greeting", { name: landing.candidate_name })}
            </p>
          )}
        </div>

        {/* Meta */}
        <div style={{ display: "flex", gap: 24, justifyContent: "center", marginBottom: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--g-text-muted)", fontSize: "0.8rem" }}>
            <Server size={14} />
            {t("labCount", { count: landing.lab_count })}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--g-text-muted)", fontSize: "0.8rem" }}>
            <Clock size={14} />
            {t("durationWindow", { hours: landing.duration_hours })}
          </div>
        </div>

        {/* Instructions */}
        {landing.candidate_instructions && (
          <div
            style={{
              background: "var(--g-surface)",
              border: "1px solid var(--g-border)",
              borderRadius: 8,
              padding: "14px 16px",
              marginBottom: 24,
              fontSize: "0.85rem",
              color: "var(--g-text)",
              lineHeight: 1.6,
              whiteSpace: "pre-wrap",
            }}
          >
            {landing.candidate_instructions}
          </div>
        )}

        {/* Registration form */}
        {landing.status === "pending" && !accessToken && (
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div style={dividerStyle}>{t("createAccountDivider")}</div>

            <div className="ev-field">
              <label className="ev-label">{tc("colUsername")}</label>
              <input
                className="g-input"
                required
                minLength={3}
                maxLength={64}
                placeholder={t("chooseUsernamePlaceholder")}
                value={username}
                autoComplete="username"
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>

            <div className="ev-field">
              <label className="ev-label">{tc("colPassword")}</label>
              <input
                className="g-input"
                type="password"
                required
                minLength={8}
                placeholder={t("atLeast8CharsPlaceholder")}
                value={password}
                autoComplete="new-password"
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <div className="ev-field">
              <label className="ev-label">{t("confirmPasswordLabel")}</label>
              <input
                className="g-input"
                type="password"
                required
                minLength={8}
                placeholder={t("repeatPasswordPlaceholder")}
                value={confirm}
                autoComplete="new-password"
                onChange={(e) => setConfirm(e.target.value)}
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              disabled={acceptMutation.isPending || !username || !password}
              style={{ marginTop: 4 }}
            >
              {acceptMutation.isPending ? t("settingUp") : t("acceptAndBegin")}
            </Button>

            <p style={{ fontSize: "0.75rem", color: "var(--g-text-muted)", textAlign: "center", margin: 0 }}>
              {t.rich("timerStartsNote", { b: (chunks) => <strong>{chunks}</strong> })}
            </p>
          </form>
        )}

        {/* Already logged in — show accept link */}
        {landing.status === "pending" && accessToken && (
          <div style={{ textAlign: "center" }}>
            <p style={{ color: "var(--g-text-muted)", fontSize: "0.875rem", marginBottom: 16 }}>
              {t.rich("signedInAs", { username: user?.username ?? "", b: (chunks) => <strong>{chunks}</strong> })}
            </p>
            <Button
              variant="primary"
              disabled={acceptMutation.isPending}
              onClick={() => acceptMutation.mutate()}
            >
              {acceptMutation.isPending ? t("linking") : t("acceptAndGoToAssessment")}
            </Button>
          </div>
        )}

        {/* Returning candidate: accepted or active but not currently signed in */}
        {(landing.status === "accepted" || landing.status === "active") && !accessToken && (
          <form
            onSubmit={(e) => { e.preventDefault(); loginMutation.mutate(); }}
            style={{ display: "flex", flexDirection: "column", gap: 14, width: "100%" }}
          >
            <div style={dividerStyle}>{t("signInToContinueDivider")}</div>
            <div className="ev-field">
              <label className="ev-label">{tc("colUsername")}</label>
              <input
                className="g-input"
                required
                placeholder={t("yourUsernamePlaceholder")}
                value={loginUsername}
                autoComplete="username"
                onChange={(e) => setLoginUsername(e.target.value)}
              />
            </div>
            <div className="ev-field">
              <label className="ev-label">{tc("colPassword")}</label>
              <input
                className="g-input"
                type="password"
                required
                placeholder={t("yourPasswordPlaceholder")}
                value={loginPassword}
                autoComplete="current-password"
                onChange={(e) => setLoginPassword(e.target.value)}
              />
            </div>
            <Button
              type="submit"
              variant="primary"
              disabled={loginMutation.isPending || !loginUsername || !loginPassword}
            >
              {loginMutation.isPending ? tl("signingIn") : t("signInAndGoToAssessment")}
            </Button>
          </form>
        )}

        {/* Returning candidate: accepted and already signed in */}
        {landing.status === "accepted" && accessToken && (
          <div style={{ textAlign: "center" }}>
            <p style={{ color: "var(--g-text-muted)", marginBottom: 16 }}>
              {t("alreadyAcceptedBody")}
            </p>
            <Button variant="primary" onClick={() => router.replace("/assessment")}>
              {t("goToAssessment")}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

const outerStyle: React.CSSProperties = {
  minHeight: "100vh",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "2rem",
  background: "var(--g-chrome)",
};

const cardStyle: React.CSSProperties = {
  background: "var(--g-card)",
  border: "1px solid var(--g-border)",
  borderRadius: 12,
  padding: "32px 36px",
  width: "100%",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
};

const headingStyle: React.CSSProperties = {
  margin: 0,
  fontSize: "1.25rem",
  fontWeight: 700,
  color: "var(--g-text)",
  textAlign: "center",
};

const dividerStyle: React.CSSProperties = {
  width: "100%",
  textAlign: "center",
  borderBottom: "1px solid var(--g-border)",
  lineHeight: "0.1em",
  margin: "4px 0 8px",
  color: "var(--g-text-muted)",
  fontSize: "0.75rem",
  textTransform: "uppercase",
  letterSpacing: "0.06em",
};
