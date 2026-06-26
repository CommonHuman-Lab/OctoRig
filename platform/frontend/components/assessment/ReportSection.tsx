"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { Shield, Send } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { submitReport } from "@/lib/api/assessments";
import { formatTime } from "@/lib/utils/date";
import { useNotificationsStore } from "@/stores/notifications.store";
import { MarkdownEditor } from "@/components/ui/MarkdownEditor";
import { Button } from "@/components/ui/Button";
import { TIMING } from "@/lib/config";

function timeAgo(date: Date, now: number, t: ReturnType<typeof useTranslations>, tn: ReturnType<typeof useTranslations>): string {
  const s = Math.max(0, Math.floor((now - date.getTime()) / 1000));
  if (s < 5) return tn("justNow");
  if (s < 60) return t("secondsAgo", { count: s });
  const m = Math.floor(s / 60);
  if (m < 60) return tn("minutesAgo", { count: m });
  const h = Math.floor(m / 60);
  return tn("hoursAgo", { count: h });
}

export function ReportSection({
  content,
  onChange,
  expired,
}: {
  content: string;
  onChange: (value: string) => void;
  expired: boolean;
}) {
  const t = useTranslations("assessment");
  const tc = useTranslations("common");
  const tn = useTranslations("notifications");
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [autosaving, setAutosaving] = useState(false);
  const [now, setNow] = useState(() => Date.now());
  const { push } = useNotificationsStore();
  const savedContentRef = useRef(content);

  // Tick once a second so "Saved Xs/Xm ago" stays live without re-saving.
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), TIMING.CLOCK_TICK_MS);
    return () => clearInterval(id);
  }, []);

  const saveMutation = useMutation({
    mutationFn: (value: string) => submitReport(value),
    onSuccess: (_data, value) => {
      savedContentRef.current = value;
      setLastSaved(new Date());
    },
  });

  // Autosave a few seconds after the user stops typing — nothing is lost
  useEffect(() => {
    if (expired || content === savedContentRef.current) return;
    setAutosaving(true);
    const id = setTimeout(() => {
      saveMutation.mutate(content, { onSettled: () => setAutosaving(false) });
    }, TIMING.AUTOSAVE_DELAY_MS);
    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [content, expired]);

  function saveNow() {
    saveMutation.mutate(content, {
      onSuccess: () => push("success", t("saveReportSuccess")),
      onError: () => push("error", t("saveReportError")),
    });
  }

  return (
    <div
      style={{
        background: "var(--g-card)",
        border: "1px solid var(--g-border)",
        borderRadius: 10,
        padding: "20px 24px",
        marginTop: 32,
        display: "flex",
        flexDirection: "column",
        flex: 1,
        minHeight: 0,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Shield size={16} style={{ color: "var(--g-accent)" }} />
          <span style={{ fontWeight: 600, color: "var(--g-text)" }}>{t("reportTitle")}</span>
          {expired && (
            <span className="role-pill role-pill--on" style={{ fontSize: "0.7rem" }}>{t("lockedBadge")}</span>
          )}
        </div>
        {!expired && (
          <span
            style={{
              display: "flex", alignItems: "center", gap: 6,
              fontSize: "0.75rem",
              color: autosaving ? "var(--g-accent)" : "var(--g-text-muted)",
            }}
          >
            {autosaving && (
              <span
                aria-hidden
                style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: "var(--g-accent)",
                  animation: "pulse 1s ease-in-out infinite",
                }}
              />
            )}
            {autosaving
              ? tc("saving")
              : lastSaved
                ? t("savedAt", { time: timeAgo(lastSaved, now, t, tn), clock: formatTime(lastSaved) })
                : t("notSavedYet")}
          </span>
        )}
      </div>

      {expired ? (
        <div
          className="md-preview"
          style={{ flex: 1, minHeight: 0, overflowY: "auto" }}
        >
          {content ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          ) : (
            <p className="md-preview-empty">{t("noReportSubmitted")}</p>
          )}
        </div>
      ) : (
        <MarkdownEditor
          value={content}
          onChange={onChange}
          minHeight={520}
          fill
          placeholder={t("reportPlaceholder")}
        />
      )}

      {!expired && (
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 10 }}>
          <Button
            variant="primary"
            size="sm"
            disabled={saveMutation.isPending || !content.trim() || content === savedContentRef.current}
            onClick={saveNow}
            leftIcon={<Send size={13} />}
          >
            {saveMutation.isPending ? tc("saving") : t("saveReport")}
          </Button>
          <span style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>
            {t("autosaveHint")}
          </span>
        </div>
      )}
    </div>
  );
}
