"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../../admin.css";
import "../../settings/settings.css";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { ArrowLeft, Copy, Check, Plus, ChevronDown, ChevronRight, Shield, Pencil } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  getAssessment,
  listInvites,
  createInvite,
  revokeInvite,
  updateAssessment,
  listCandidateProgress,
  type CreateAssessmentPayload,
  type AssessmentInvite,
  type AssessmentInviteWithProgress,
  type InviteStatus,
} from "@/lib/api/assessments";
import { getLabs, type LabTemplate } from "@/lib/api/labs";
import { AssessmentFormSheet } from "@/components/admin/assessments/AssessmentFormSheet";
import { useConfirmStore } from "@/stores/confirm.store";
import { formatDateTime } from "@/lib/utils/date";
import { Button } from "@/components/ui/Button";
import { TIMING, STALE_TIME } from "@/lib/config";

function StatusBadge({ status }: { status: InviteStatus }) {
  const t = useTranslations("admin.assessments");
  const tUsers = useTranslations("admin.users");
  const colors: Record<InviteStatus, string> = {
    pending: "var(--g-text-muted)",
    accepted: "var(--g-warning, #f59e0b)",
    active: "var(--g-accent)",
    completed: "var(--g-success, #22c55e)",
    expired: "var(--g-danger)",
    revoked: "var(--g-danger)",
  };
  const labels: Record<InviteStatus, string> = {
    pending: t("statusPending"),
    accepted: t("statusAccepted"),
    active: tUsers("active"),
    completed: t("statusCompleted"),
    expired: t("statusExpired"),
    revoked: t("statusRevoked"),
  };
  return (
    <span
      style={{
        fontSize: "0.7rem",
        fontFamily: "var(--font-mono, monospace)",
        color: colors[status],
        textTransform: "uppercase",
        letterSpacing: "0.04em",
      }}
    >
      {labels[status]}
    </span>
  );
}

function CopyButton({ text }: { text: string }) {
  const t = useTranslations("admin.assessments");
  const [copied, setCopied] = useState(false);
  return (
    <Button
      size="sm"
      icon
      tooltip={t("copyInviteLinkTooltip")}
      leftIcon={copied ? <Check size={12} /> : <Copy size={12} />}
      onClick={() => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), TIMING.COPY_FEEDBACK_MS);
      }}
    />
  );
}

function ProgressRow({
  assessmentId,
  invite,
  progress,
}: {
  assessmentId: number;
  invite: AssessmentInvite;
  progress?: AssessmentInviteWithProgress;
}) {
  const t = useTranslations("admin.assessments");
  const tAssessment = useTranslations("assessment");
  const [expanded, setExpanded] = useState(false);
  const { confirm } = useConfirmStore();

  const revokeMutation = useApiMutation<void, void>({
    mutationFn: () => revokeInvite(assessmentId, invite.id),
    invalidateKeys: [["assessment-invites", assessmentId]],
    successMessage: t("toastInviteRevoked"),
    errorMessage: t("toastRevokeInviteFailed"),
  });

  const inviteUrl =
    typeof window !== "undefined"
      ? `${window.location.origin}/assessment/invite/${invite.token}`
      : `/assessment/invite/${invite.token}`;

  return (
    <>
      <tr
        style={{ cursor: "pointer" }}
        onClick={() => setExpanded((v) => !v)}
      >
        <td>
          {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        </td>
        <td style={{ color: "var(--g-text)" }}>{invite.email}</td>
        <td style={{ color: "var(--g-text-muted)", fontSize: "0.8rem" }}>
          {invite.candidate_name ?? "—"}
        </td>
        <td><StatusBadge status={invite.status} /></td>
        <td style={{ color: "var(--g-text-muted)", fontSize: "0.75rem", fontFamily: "var(--font-mono, monospace)" }}>
          {formatDateTime(invite.started_at)}
        </td>
        <td style={{ color: "var(--g-text-muted)", fontSize: "0.75rem", fontFamily: "var(--font-mono, monospace)" }}>
          {formatDateTime(invite.expires_at)}
        </td>
        <td style={{ fontSize: "0.8rem", color: "var(--g-text-muted)" }}>
          {invite.deployment_ids.length > 0 ? tAssessment("labCount", { count: invite.deployment_ids.length }) : "—"}
        </td>
        <td style={{ fontSize: "0.8rem", color: "var(--g-text)" }}>
          {progress ? (
            <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <Shield size={11} style={{ color: "var(--g-accent)" }} />
              {progress.flags_solved.length}
            </span>
          ) : "—"}
        </td>
        <td style={{ fontSize: "0.8rem", color: "var(--g-text)", fontFamily: "var(--font-mono, monospace)" }}>
          {progress ? progress.score : "—"}
        </td>
        <td>
          <div style={{ display: "flex", gap: 6 }} onClick={(e) => e.stopPropagation()}>
            <CopyButton text={inviteUrl} />
            {!invite.is_revoked && (
              <Button
                size="sm"
                style={{ color: "var(--g-danger)" }}
                onClick={() =>
                  confirm({
                    title: t("revokeInviteTitle"),
                    body: t("revokeInviteBody", { email: invite.email }),
                    confirmLabel: t("revokeBtn"),
                    dangerous: true,
                    onConfirm: () => revokeMutation.mutate(),
                  })
                }
              >
                {t("revokeBtn")}
              </Button>
            )}
          </div>
        </td>
      </tr>

      {expanded && (
        <tr>
          <td colSpan={10} style={{ background: "var(--g-surface-elevated, var(--g-surface))", padding: "12px 20px" }}>
            {progress ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                <div style={{ display: "flex", gap: 32, flexWrap: "wrap" }}>
                  <div>
                    <div style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--g-text-muted)", marginBottom: 6 }}>
                      {t("flagsSolvedHeading", { count: progress.flags_solved.length, points: progress.score })}
                    </div>
                    {progress.flags_solved.length === 0 ? (
                      <span className="text-muted" style={{ fontSize: "0.8rem" }}>{t("noneYet")}</span>
                    ) : (
                      <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 4 }}>
                        {progress.flags_solved.map((f) => (
                          <li key={f.challenge_slug} style={{ fontSize: "0.8rem", display: "flex", alignItems: "center", gap: 6 }}>
                            <Shield size={11} style={{ color: "var(--g-accent)" }} />
                            <span style={{ color: "var(--g-text)" }}>{f.challenge_title}</span>
                            <span style={{ color: "var(--g-text-muted)", fontSize: "0.7rem" }}>+{f.points} pts</span>
                            <span style={{ color: "var(--g-text-muted)", fontSize: "0.7rem" }}>
                              {formatDateTime(f.solved_at)}
                            </span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div>
                    <div style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--g-text-muted)", marginBottom: 6 }}>
                      {t("completedHeading")}
                    </div>
                    <span style={{ fontSize: "0.8rem", color: "var(--g-text)", fontFamily: "var(--font-mono, monospace)" }}>
                      {formatDateTime(invite.completed_at)}
                    </span>
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--g-text-muted)", marginBottom: 6, display: "flex", alignItems: "center", gap: 8 }}>
                    {t("reportHeading")}
                    {invite.completed_at ? (
                      <span className="g-status-pill g-status-pill--on" style={{ fontSize: "0.7rem" }}>{t("submittedBadge")}</span>
                    ) : progress.report_content ? (
                      <span className="g-status-pill" style={{ fontSize: "0.7rem", color: "var(--g-warning, #f59e0b)" }}>{t("draftInProgressBadge")}</span>
                    ) : (
                      <span className="g-status-pill g-status-pill--off" style={{ fontSize: "0.7rem" }}>{t("notStartedBadge")}</span>
                    )}
                  </div>
                  {progress.report_content ? (
                    <div
                      className="md-preview"
                      style={{
                        maxHeight: 480,
                        overflowY: "auto",
                        background: "var(--g-surface)",
                        border: "1px solid var(--g-border, rgba(255,255,255,0.08))",
                        borderRadius: 6,
                        padding: "12px 16px",
                      }}
                    >
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{progress.report_content}</ReactMarkdown>
                    </div>
                  ) : (
                    <span className="text-muted" style={{ fontSize: "0.8rem" }}>{t("noReportSavedYet")}</span>
                  )}
                </div>
              </div>
            ) : (
              <span className="text-muted text-sm">{t("noProgressYet")}</span>
            )}
          </td>
        </tr>
      )}
    </>
  );
}

export default function AssessmentDetailPage() {
  const t = useTranslations("admin.assessments");
  const tCommon = useTranslations("common");
  const tNav = useTranslations("nav");
  const tUsers = useTranslations("admin.users");
  const { id } = useParams<{ id: string }>();
  const assessmentId = Number(id);

  const [editSheetOpen, setEditSheetOpen] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [newName, setNewName] = useState("");

  const { data: assessment, isLoading: assessmentLoading } = useQuery({
    queryKey: ["admin-assessment", assessmentId],
    queryFn: () => getAssessment(assessmentId),
  });

  const { data: invites = [], isLoading: invitesLoading } = useQuery({
    queryKey: ["assessment-invites", assessmentId],
    queryFn: () => listInvites(assessmentId),
  });

  const { data: progressList = [] } = useQuery({
    queryKey: ["assessment-progress", assessmentId],
    queryFn: () => listCandidateProgress(assessmentId),
    enabled: invites.length > 0,
    refetchInterval: 30_000,
  });
  const progressByInviteId = new Map(progressList.map((p) => [p.id, p]));

  const { data: labs = [], isLoading: labsLoading } = useQuery<LabTemplate[]>({
    queryKey: ["labs", "world"],
    queryFn: () => getLabs("world"),
    staleTime: STALE_TIME.MEDIUM,
  });

  const updateMutation = useApiMutation({
    mutationFn: (payload: CreateAssessmentPayload) => updateAssessment(assessmentId, payload),
    invalidateKeys: [["admin-assessment", assessmentId], ["admin-assessments"]],
    successMessage: t("toastAssessmentUpdated"),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("toastUpdateAssessmentFailed"),
    onSuccess: () => setEditSheetOpen(false),
  });

  const inviteMutation = useApiMutation<AssessmentInvite, void>({
    mutationFn: () =>
      createInvite(assessmentId, {
        email: newEmail,
        candidate_name: newName || undefined,
      }),
    invalidateKeys: [["assessment-invites", assessmentId], ["admin-assessments"]],
    successMessage: (data) => t("toastInviteCreated", { email: data.email }),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("toastCreateInviteFailed"),
    onSuccess: () => {
      setNewEmail("");
      setNewName("");
    },
  });

  if (assessmentLoading) {
    return (
      <div className="page">
        <p className="text-muted text-sm">{tCommon("loading")}</p>
      </div>
    );
  }

  if (!assessment) {
    return (
      <div className="page">
        <p className="text-muted text-sm">{t("assessmentNotFound")}</p>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <Button href="/admin/assessments" size="sm" leftIcon={<ArrowLeft size={14} />}>
          {t("backBtn")}
        </Button>
        <h1 className="page-title font-mono">{assessment.name}</h1>
        <span className={`g-status-pill ${assessment.is_active ? "g-status-pill--on" : "g-status-pill--off"}`}>
          {assessment.is_active ? tUsers("active") : tUsers("inactive")}
        </span>
        <Button
          size="sm"
          style={{ marginLeft: "auto" }}
          leftIcon={<Pencil size={13} />}
          onClick={() => setEditSheetOpen(true)}
        >
          {tCommon("edit")}
        </Button>
      </div>

      {/* Assessment summary */}
      <div className="g-card" style={{ padding: "16px 20px", marginBottom: 24, display: "flex", gap: 32, flexWrap: "wrap" }}>
        <div>
          <div className="text-11 text-muted" style={{ marginBottom: 2 }}>{tNav("labs")}</div>
          <div style={{ fontFamily: "var(--font-mono, monospace)", fontSize: "0.875rem", color: "var(--g-text)" }}>
            {assessment.lab_slugs.map((slug) => {
              const display = assessment.lab_display_names[slug];
              return (
                <div key={slug}>
                  {display ? (
                    <><span style={{ color: "var(--g-text)" }}>{display}</span><span style={{ color: "var(--g-text-muted)", fontSize: "0.7rem" }}> ({slug})</span></>
                  ) : slug}
                </div>
              );
            })}
          </div>
        </div>
        <div>
          <div className="text-11 text-muted" style={{ marginBottom: 2 }}>{t("durationLabel")}</div>
          <div style={{ fontSize: "0.875rem", color: "var(--g-text)" }}>{assessment.duration_hours}h</div>
        </div>
        {assessment.company_name && (
          <div>
            <div className="text-11 text-muted" style={{ marginBottom: 2 }}>{t("companyLabel")}</div>
            <div style={{ fontSize: "0.875rem", color: "var(--g-text)" }}>{assessment.company_name}</div>
          </div>
        )}
        <div>
          <div className="text-11 text-muted" style={{ marginBottom: 2 }}>{t("colCandidates")}</div>
          <div style={{ fontSize: "0.875rem", color: "var(--g-text)" }}>
            {t("candidatesCountSummary", { active: assessment.active_invite_count, total: assessment.invite_count })}
          </div>
        </div>
      </div>

      {/* Add candidate */}
      <section className="admin-settings-section" style={{ marginBottom: 24 }}>
        <h2 className="admin-settings-section-title">{t("addCandidateSectionTitle")}</h2>
        <div style={{ display: "flex", gap: 10, alignItems: "flex-end", flexWrap: "wrap", padding: "12px 16px" }}>
          <div className="ev-field" style={{ flexShrink: 0, minWidth: 220 }}>
            <label className="ev-label">{t("emailLabel")}</label>
            <input
              className="g-input"
              type="email"
              placeholder={t("emailPlaceholder")}
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
            />
          </div>
          <div className="ev-field" style={{ flexShrink: 0, minWidth: 180 }}>
            <label className="ev-label">{t("nameOptionalLabel")}</label>
            <input
              className="g-input"
              placeholder={t("namePlaceholderJane")}
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
          </div>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Plus size={13} />}
            disabled={!newEmail || inviteMutation.isPending}
            onClick={() => inviteMutation.mutate()}
          >
            {inviteMutation.isPending ? tUsers("creating") : t("generateInviteBtn")}
          </Button>
        </div>
      </section>

      {/* Candidates table */}
      <section>
        <h2 className="section-title text-11 text-muted" style={{ marginBottom: "0.75rem" }}>
          {t("candidatesSectionTitle", { count: invites.length })}
        </h2>

        {invitesLoading ? (
          <p className="text-muted text-sm">{tCommon("loading")}</p>
        ) : invites.length === 0 ? (
          <p className="text-muted text-sm">{t("noInvitesYet")}</p>
        ) : (
          <table className="g-table">
            <thead>
              <tr>
                <th style={{ width: 24 }}></th>
                <th>{t("colEmail")}</th>
                <th>{t("colName")}</th>
                <th>{tUsers("colStatus")}</th>
                <th>{t("colStarted")}</th>
                <th>{t("colExpires")}</th>
                <th>{tNav("labs")}</th>
                <th>{t("colFlags")}</th>
                <th>{t("colScore")}</th>
                <th>{tCommon("actions")}</th>
              </tr>
            </thead>
            <tbody>
              {invites.map((invite) => (
                <ProgressRow
                  key={invite.id}
                  assessmentId={assessmentId}
                  invite={invite}
                  progress={progressByInviteId.get(invite.id)}
                />
              ))}
            </tbody>
          </table>
        )}
      </section>

      <AssessmentFormSheet
        open={editSheetOpen}
        labs={labs}
        labsLoading={labsLoading}
        saveMutation={updateMutation}
        onClose={() => setEditSheetOpen(false)}
        initialValues={assessment}
      />
    </div>
  );
}
