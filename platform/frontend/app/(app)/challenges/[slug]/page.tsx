"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../challenges.css";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { AlertTriangle, CheckCircle2, Container } from "lucide-react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import {
  getChallenge, submitFlag,
  type HintSummary,
} from "@/lib/api/challenges";
import { getMyProfile } from "@/lib/api/profiles";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getPublicSettings } from "@/lib/api/settings";
import { PyodideEditor } from "@/components/challenges/PyodideEditor";
import { deployInstance, getMyInstance, stopDeployment, type Deployment } from "@/lib/api/deployments";
import { getLabs } from "@/lib/api/labs";
import { useNotificationsStore } from "@/stores/notifications.store";
import { PageSpinner } from "@/components/ui/Spinner";
import { InstanceCard } from "@/components/challenges/InstanceCard";
import { HintCard } from "@/components/challenges/HintCard";
import { ChallengeHeader } from "@/components/challenges/ChallengeHeader";
import { SubmitForm } from "@/components/challenges/SubmitForm";
import { NoteList } from "@/components/notes/NoteList";
import { Button } from "@/components/ui/Button";
import { TIMING, STALE_TIME } from "@/lib/config";

export default function ChallengeDetailPage() {
  const t = useTranslations("challenges.detail");
  const tNav = useTranslations("nav");
  const { slug } = useParams<{ slug: string }>();
  const qc = useQueryClient();
  const { push } = useNotificationsStore();

  const [flag, setFlag] = useState("");
  const [submitResult, setSubmitResult] = useState<{
    correct: boolean;
    message: string;
    firstBlood: boolean;
    points: number;
  } | null>(null);
  const [localHints, setLocalHints] = useState<Record<number, string>>({});
  const [cooldownUntil, setCooldownUntil] = useState<number | null>(null);
  const [cooldownRemaining, setCooldownRemaining] = useState(0);

  useEffect(() => {
    if (!cooldownUntil) return;
    const tick = () => {
      const remaining = Math.ceil((cooldownUntil - Date.now()) / 1000);
      if (remaining <= 0) { setCooldownRemaining(0); setCooldownUntil(null); return; }
      setCooldownRemaining(remaining);
    };
    tick();
    const id = setInterval(tick, TIMING.CHALLENGE_TICK_MS);
    return () => clearInterval(id);
  }, [cooldownUntil]);

  const { data: profile } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: getMyProfile,
    staleTime: STALE_TIME.SHORT,
  });
  const userPoints = profile?.total_points ?? 0;

  const { data: ch, isLoading } = useQuery({
    queryKey: ["challenge", slug],
    queryFn: () => getChallenge(slug),
  });

  const { data: labs = [] } = useQuery({
    queryKey: ["labs"],
    queryFn: () => getLabs(),
    staleTime: STALE_TIME.SHORT,
    enabled: !!ch?.lab_slug || (ch?.required_labs?.length ?? 0) > 0,
  });

  const { data: publicSettings } = useQuery({
    queryKey: ["public-settings"],
    queryFn: getPublicSettings,
    staleTime: STALE_TIME.LONG,
  });

  const labTemplate = ch?.lab_slug
    ? labs.find((l) => l.slug === ch.lab_slug) ?? null
    : null;

  const labIsLive =
    labTemplate?.current_deployment?.status === "running" ||
    labTemplate?.current_deployment?.status === "starting";

  const offlineRequiredLabs = (ch?.required_labs ?? []).filter((req) => {
    const tpl = labs.find((l) => l.slug === req.slug);
    const s = tpl?.current_deployment?.status;
    return s !== "running" && s !== "starting";
  });

  const { data: instance = null } = useQuery({
    queryKey: ["challenge-instance", ch?.id],
    queryFn: () => getMyInstance(ch!.id),
    enabled: ch?.challenge_type === "container",
    refetchInterval: (q) => {
      const s = q.state.data?.status;
      return s === "starting" || s === "stopping" ? 3_000 : 15_000;
    },
  });

  // Prefer the caller's own dynamically-allocated instance over the lab template's static defaults
  const labUrl =
    instance?.access_info.find((a) => a.key === "URL")?.value ??
    labTemplate?.access_info.find((a) => a.key === "URL")?.value ??
    null;

  const deployMutation = useApiMutation<Deployment, void>({
    mutationFn: () => deployInstance(ch!.id, 2),
    invalidateKeys: [["challenge-instance", ch?.id]],
    successMessage: t("toastInstanceStarting"),
    errorMessage: (err: unknown) =>
      (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
      t("toastDeployFailed"),
  });

  const stopMutation = useMutation({
    mutationFn: () => stopDeployment(instance!.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["challenge-instance", ch?.id] });
      push("info", t("toastInstanceDestroyed"));
    },
    onError: () => push("error", t("toastStopInstanceFailed")),
  });

  const submitMutation = useMutation({
    mutationFn: (f: string) => submitFlag(slug, f),
    onSuccess: (res) => {
      setSubmitResult({
        correct: res.correct || res.already_solved,
        message: res.message,
        firstBlood: res.first_blood,
        points: res.points_awarded,
      });
      if (res.correct || res.already_solved) {
        qc.invalidateQueries({ queryKey: ["challenge", slug] });
        qc.invalidateQueries({ queryKey: ["challenges"] });
        if (res.first_blood) push("success", t("toastFirstBlood", { points: res.points_awarded }));
        else if (!res.already_solved) push("success", t("toastCorrect", { points: res.points_awarded }));
        setFlag("");
      } else {
        push("error", t("toastIncorrectFlag"));
      }
    },
    onError: (err: unknown) => {
      const res = (err as { response?: { status?: number; data?: { detail?: string } } })?.response;
      const detail = res?.data?.detail;
      if (res?.status === 429 && detail) {
        const match = detail.match(/(\d+)\s*second/i);
        if (match) setCooldownUntil(Date.now() + parseInt(match[1]) * 1000);
      }
      push("error", detail ?? t("toastSubmissionFailed"));
    },
  });

  function handleHintUnlocked(hintId: number, content: string) {
    setLocalHints((prev) => ({ ...prev, [hintId]: content }));
    qc.invalidateQueries({ queryKey: ["challenge", slug] });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!flag.trim()) return;
    setSubmitResult(null);
    submitMutation.mutate(flag.trim());
  }

  if (isLoading) return <div className="page"><PageSpinner /></div>;
  if (!ch) return <div className="page text-muted text-xs">{t("challengeNotFound")}</div>;

  const codeSnippet = ch.challenge_type === "short_answer" ? (ch.content?.code_snippet as string | undefined) : undefined;
  const language = (ch.content?.language as string | undefined) ?? "text";
  const isPythonChallenge = ch.challenge_type === "short_answer" && language === "python";
  const showEditor = isPythonChallenge && (publicSettings?.python_editor_enabled ?? true);
  const starterCode = (ch.content?.starter_code as string | undefined) ?? (showEditor ? codeSnippet : undefined);

  const hints: HintSummary[] = ch.hints.map((h) => ({
    ...h,
    content: localHints[h.id] ?? h.content,
    unlocked: h.unlocked || localHints[h.id] !== undefined,
  }));

  return (
    <div className="page">
      <Link href="/challenges" className="back-link">
        <ArrowLeft size={14} />
        <span>{tNav("challenges")}</span>
      </Link>

      <ChallengeHeader
        challenge={ch}
        solvedByMe={ch.solved_by_me}
        labIsLive={labTemplate ? labIsLive : undefined}
        labUrl={labUrl}
      />

      {offlineRequiredLabs.map((req) => (
        <div
          key={req.slug}
          style={{
            display: "flex", alignItems: "center", gap: "0.5rem",
            padding: "0.625rem 0.875rem",
            background: "color-mix(in srgb, var(--g-warning) 12%, transparent)",
            border: "1px solid color-mix(in srgb, var(--g-warning) 35%, transparent)",
            borderRadius: "6px", marginBottom: "0.75rem",
            fontSize: "0.8125rem", color: "var(--g-text)",
          }}
        >
          <AlertTriangle size={14} style={{ color: "var(--g-warning)", flexShrink: 0 }} />
          <span>{t("alsoRequiresLab", { name: req.name })}</span>
          <Link href="/labs" style={{ marginLeft: "auto", color: "var(--g-accent)", fontSize: "0.75rem" }}>
            {t("startLabLink")}
          </Link>
        </div>
      ))}

      <div className={showEditor ? "ch-split" : "ch-body"}>
        <div className={showEditor ? "ch-content" : "ch-body"}>
          <section className="g-card ch-desc-card">
            <div className="ch-desc">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{ch.description}</ReactMarkdown>
            </div>
            {ch.tags.length > 0 && (
              <div className="ch-tags" style={{ marginTop: "1rem" }}>
                {ch.tags.map((t) => (
                  <span key={t} className="g-badge g-badge--accent">{t}</span>
                ))}
              </div>
            )}
          </section>

          {codeSnippet && !showEditor && (
            <section className="g-card">
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
                <h2 className="section-title" style={{ margin: 0 }}>{t("codeHeading")}</h2>
                <span style={{
                  fontSize: "0.625rem", fontFamily: "var(--font-mono, monospace)",
                  textTransform: "uppercase", letterSpacing: "0.08em",
                  color: "var(--g-text-muted)", background: "var(--g-surface-2)",
                  padding: "0.15rem 0.4rem", borderRadius: "3px",
                }}>
                  {language}
                </span>
              </div>
              <pre style={{
                margin: 0, padding: "1rem",
                background: "var(--g-surface-2)", border: "1px solid var(--g-border)",
                borderRadius: "6px", fontSize: "0.8125rem", lineHeight: 1.6,
                color: "var(--g-text)", whiteSpace: "pre", overflowX: "auto",
                fontFamily: "var(--font-mono, monospace)",
              }}>
                <code>{codeSnippet}</code>
              </pre>
            </section>
          )}

          {hints.length > 0 && (
            <section>
              <h2 className="section-title">{t("hintsHeading")}</h2>
              <div className="hints-list">
                {hints.map((h) => (
                  <HintCard
                    key={h.id}
                    hint={h}
                    slug={slug}
                    userPoints={userPoints}
                    onUnlocked={handleHintUnlocked}
                  />
                ))}
              </div>
            </section>
          )}

          {ch.challenge_type === "container" && (
            <section>
              <h2 className="section-title">{t("labInstanceHeading")}</h2>
              {instance && (instance.status === "running" || instance.status === "starting" || instance.status === "stopping") ? (
                <InstanceCard
                  instance={instance}
                  onStop={() => stopMutation.mutate()}
                  isStopping={stopMutation.isPending}
                />
              ) : (
                <div className="g-card" style={{ borderStyle: "dashed" }}>
                  <p className="text-11 text-muted mb-3">
                    {t("requiresInstanceBody")}
                  </p>
                  <Button
                    variant="primary"
                    leftIcon={<Container size={13} />}
                    onClick={() => deployMutation.mutate()}
                    disabled={deployMutation.isPending}
                  >
                    {deployMutation.isPending ? t("deployingBtn") : t("deployInstanceBtn")}
                  </Button>
                </div>
              )}
            </section>
          )}

          <section className="g-card">
            <h2 className="section-title">{tNav("notes")}</h2>
            <NoteList filter={{ challenge_id: ch.id }} emptyMessage={t("noNotesForChallenge")} />
          </section>

          <section className="g-card submit-card">
            <h2 className="section-title">{codeSnippet ? t("submitAnswerHeading") : t("submitFlagHeading")}</h2>
            {ch.solved_by_me ? (
              <div className="submit-solved">
                <CheckCircle2 size={16} />
                {t("alreadySolvedBody")}
              </div>
            ) : (
              <SubmitForm
                codeSnippet={codeSnippet}
                flag={flag}
                onFlagChange={setFlag}
                onSubmit={handleSubmit}
                isLoading={submitMutation.isPending}
                submitResult={submitResult}
                cooldownRemaining={cooldownRemaining}
              />
            )}
          </section>
        </div>

        {showEditor && (
          <div className="ch-editor-panel">
            <PyodideEditor starterCode={starterCode} />
          </div>
        )}
      </div>
    </div>
  );
}
