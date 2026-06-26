"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Shield, Clock, AlertTriangle, Play, Lock, CheckCircle2 } from "lucide-react";
import {
  getAssessmentStatus,
  startAssessment,
  completeAssessment,
  type CandidateAssessmentStatus,
} from "@/lib/api/assessments";
import { useUserStore } from "@/stores/user.store";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { CountdownDisplay } from "@/components/assessment/CountdownDisplay";
import { LabCard } from "@/components/assessment/LabCard";
import { ReportSection } from "@/components/assessment/ReportSection";
import { WorkspaceSidebar, type SectionId } from "@/components/assessment/WorkspaceSidebar";
import { Button } from "@/components/ui/Button";

export default function AssessmentWorkspacePage() {
  const t = useTranslations("assessment");
  const { accessToken, user, _hasHydrated, isRestoringToken } = useUserStore();
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();
  const router = useRouter();
  const qc = useQueryClient();
  const [section, setSection] = useState<SectionId>("overview");
  const [reportContent, setReportContent] = useState<string | null>(null);

  useEffect(() => {
    if (_hasHydrated && !isRestoringToken && !accessToken) {
      router.replace("/login");
    }
  }, [_hasHydrated, isRestoringToken, accessToken, router]);

  const { data: status, isLoading } = useQuery<CandidateAssessmentStatus>({
    queryKey: ["assessment-status"],
    queryFn: getAssessmentStatus,
    enabled: !!accessToken && !!user?.is_candidate,
    refetchInterval: 30_000,
    retry: false,
  });

  useEffect(() => {
    if (status && reportContent === null) {
      setReportContent(status.report_content ?? "");
    }
  }, [status, reportContent]);

  const startMutation = useApiMutation<CandidateAssessmentStatus, void>({
    mutationFn: startAssessment,
    invalidateKeys: [["assessment-status"]],
    successMessage: t("startedToast"),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("startError"),
  });

  const completeMutation = useMutation({
    mutationFn: completeAssessment,
    onSuccess: (data) => {
      qc.setQueryData(["assessment-status"], data);
      push("success", t("completedToast"));
    },
    onError: (err: any) =>
      push("error", err?.response?.data?.detail ?? t("completeError")),
  });

  function confirmComplete() {
    confirm({
      title: t("completeConfirmTitle"),
      body: t("completeConfirmBody"),
      confirmLabel: t("completeAssessment"),
      dangerous: true,
      onConfirm: () => completeMutation.mutate(),
    });
  }

  if (!_hasHydrated || isRestoringToken || !accessToken) return null;

  if (isLoading) {
    return (
      <div style={outerStyle}>
        <p style={{ color: "var(--g-text-muted)" }}>{t("loadingAssessment")}</p>
      </div>
    );
  }

  if (!status) {
    return (
      <div style={outerStyle}>
        <div style={{ textAlign: "center" }}>
          <AlertTriangle size={40} style={{ color: "var(--g-warning)", marginBottom: 12 }} />
          <h2 style={{ color: "var(--g-text)", marginBottom: 8 }}>{t("noActiveAssessment")}</h2>
          <p style={{ color: "var(--g-text-muted)" }}>{t("inviteNotFoundBody")}</p>
        </div>
      </div>
    );
  }

  const completedByChoice = status.completed_at !== null;
  const expired = (status.time_remaining_seconds ?? 1) === 0;
  const notStarted = status.started_at === null;
  const companyName = status.company_name || "OctoRig";

  return (
    <div style={{ minHeight: "100vh", background: "var(--g-chrome)", padding: "0 0 60px" }}>
      {/* Header bar */}
      <div
        style={{
          background: "var(--g-card)",
          borderBottom: "1px solid var(--g-border)",
          padding: "12px 32px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          position: "sticky",
          top: 0,
          zIndex: "var(--z-dropdown)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {status.company_logo_url ? (
            <img src={status.company_logo_url} alt={companyName} style={{ height: 28, objectFit: "contain" }} />
          ) : (
            <Shield size={22} style={{ color: "var(--g-accent)" }} />
          )}
          <span style={{ fontWeight: 600, color: "var(--g-text)", fontSize: "0.95rem" }}>
            {companyName}
          </span>
          <span style={{ color: "var(--g-border)" }}>·</span>
          <span style={{ color: "var(--g-text-muted)", fontSize: "0.85rem" }}>
            {status.assessment_name}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          {completedByChoice ? (
            <span style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.75rem", color: "var(--g-success, #22c55e)", fontFamily: "var(--font-mono, monospace)" }}>
              <CheckCircle2 size={14} />
              {t("completedBadge")}
            </span>
          ) : expired && (
            <span style={{ fontSize: "0.75rem", color: "var(--g-danger)", fontFamily: "var(--font-mono, monospace)" }}>
              {t("endedBadge")}
            </span>
          )}
          {!notStarted && !expired && <CountdownDisplay expiresAt={status.expires_at} />}
          <span style={{ fontSize: "0.8rem", color: "var(--g-text-muted)" }}>
            {user?.username}
          </span>
        </div>
      </div>

      {/* Body */}
      <div style={{ display: "flex", minHeight: "calc(100vh - 57px)" }}>
        <WorkspaceSidebar active={section} onSelect={setSection} />

        <div
          style={{
            flex: 1,
            maxWidth: section === "report" ? 1280 : 900,
            margin: "0 auto",
            padding: "32px 24px",
            display: "flex",
            flexDirection: "column",
            width: "100%",
          }}
        >
          {section === "overview" && (
            <>
              {status.candidate_instructions && (
                <div
                  style={{
                    background: "var(--g-card)",
                    border: "1px solid var(--g-border)",
                    borderRadius: 10,
                    padding: "16px 20px",
                    marginBottom: 28,
                    fontSize: "0.85rem",
                    color: "var(--g-text)",
                    lineHeight: 1.7,
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {status.candidate_instructions}
                </div>
              )}

              {notStarted && !expired && (
                <div
                  style={{
                    textAlign: "center",
                    padding: "40px 24px",
                    background: "var(--g-card)",
                    border: "1px solid var(--g-border)",
                    borderRadius: 12,
                    marginBottom: 28,
                  }}
                >
                  <Clock size={36} style={{ color: "var(--g-accent)", marginBottom: 12 }} />
                  <h2 style={{ color: "var(--g-text)", marginBottom: 8 }}>{t("readyToBegin")}</h2>
                  <p style={{ color: "var(--g-text-muted)", marginBottom: 20, maxWidth: 400, margin: "0 auto 20px" }}>
                    {t.rich("readyToBeginBody", {
                      count: status.labs.length,
                      name: status.assessment_name,
                      hours: Math.floor((/* duration */ status.time_remaining_seconds ?? 0) / 3600 || 48),
                      b: (chunks) => <strong>{chunks}</strong>,
                    })}
                  </p>
                  <Button
                    variant="primary"
                    disabled={startMutation.isPending}
                    onClick={() => startMutation.mutate()}
                    leftIcon={<Play size={15} />}
                  >
                    {startMutation.isPending ? t("starting") : t("startAssessment")}
                  </Button>
                </div>
              )}

              {!notStarted && (
                <div
                  style={{
                    background: "var(--g-card)",
                    border: "1px solid var(--g-border)",
                    borderRadius: 10,
                    padding: "16px 20px",
                    color: "var(--g-text-muted)",
                    fontSize: "0.85rem",
                  }}
                >
                  {completedByChoice
                    ? t("completedSummary")
                    : expired
                      ? t("expiredSummary")
                      : t("deployedSummary", { count: status.labs.length })}
                </div>
              )}

              {!notStarted && !expired && !completedByChoice && (
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: 16,
                    marginTop: 20,
                    padding: "16px 20px",
                    background: "var(--g-card)",
                    border: "1px solid var(--g-border)",
                    borderRadius: 10,
                  }}
                >
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, fontWeight: 600, color: "var(--g-text)", marginBottom: 4 }}>
                      <Lock size={14} style={{ color: "var(--g-text-muted)" }} />
                      {t("doneEarly")}
                    </div>
                    <p style={{ color: "var(--g-text-muted)", fontSize: "0.8rem", margin: 0 }}>
                      {t("doneEarlyBody")}
                    </p>
                  </div>
                  <Button
                    variant="danger"
                    size="sm"
                    style={{ flexShrink: 0 }}
                    disabled={completeMutation.isPending}
                    onClick={confirmComplete}
                    leftIcon={<CheckCircle2 size={13} />}
                  >
                    {completeMutation.isPending ? t("completing") : t("completeAssessment")}
                  </Button>
                </div>
              )}
            </>
          )}

          {section === "labs" && (
            <>
              {notStarted ? (
                <p style={{ color: "var(--g-text-muted)", fontSize: "0.85rem" }}>
                  {t("startFromOverviewLabs")}
                </p>
              ) : (
                <>
                  <h2
                    style={{
                      color: "var(--g-text-muted)",
                      fontSize: "0.7rem",
                      textTransform: "uppercase",
                      letterSpacing: "0.08em",
                      marginBottom: 12,
                    }}
                  >
                    {t("targetMachines", { count: status.labs.length })}
                  </h2>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 16, marginBottom: 8 }}>
                    {status.labs.map((lab) => (
                      <LabCard key={lab.slug} lab={lab} expired={expired} />
                    ))}
                  </div>
                </>
              )}
            </>
          )}

          {section === "report" && (
            <>
              {notStarted ? (
                <p style={{ color: "var(--g-text-muted)", fontSize: "0.85rem" }}>
                  {t("startFromOverviewReport")}
                </p>
              ) : (
                <ReportSection
                  content={reportContent ?? ""}
                  onChange={setReportContent}
                  expired={expired}
                />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

const outerStyle: React.CSSProperties = {
  minHeight: "100vh",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "var(--g-chrome)",
  color: "var(--g-text)",
};
