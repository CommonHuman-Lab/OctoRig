"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Shield, Send } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { submitReport } from "@/lib/api/assessments";
import { formatTime } from "@/lib/utils/date";
import { useNotificationsStore } from "@/stores/notifications.store";
import { MarkdownEditor } from "@/components/ui/MarkdownEditor";
import { Button } from "@/components/ui/Button";

const AUTOSAVE_DELAY_MS = 1500;

function timeAgo(date: Date, now: number): string {
  const s = Math.max(0, Math.floor((now - date.getTime()) / 1000));
  if (s < 5) return "just now";
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  return `${h}h ago`;
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
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [autosaving, setAutosaving] = useState(false);
  const [now, setNow] = useState(() => Date.now());
  const { push } = useNotificationsStore();
  const savedContentRef = useRef(content);

  // Tick once a second so "Saved Xs/Xm ago" stays live without re-saving.
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
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
    }, AUTOSAVE_DELAY_MS);
    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [content, expired]);

  function saveNow() {
    saveMutation.mutate(content, {
      onSuccess: () => push("success", "Report saved"),
      onError: () => push("error", "Failed to save report"),
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
          <span style={{ fontWeight: 600, color: "var(--g-text)" }}>Pentest Report</span>
          {expired && (
            <span className="role-pill role-pill--on" style={{ fontSize: "0.7rem" }}>Locked</span>
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
              ? "Saving…"
              : lastSaved
                ? `Saved ${timeAgo(lastSaved, now)} (${formatTime(lastSaved)})`
                : "Not saved yet"}
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
            <p className="md-preview-empty">No report was submitted.</p>
          )}
        </div>
      ) : (
        <MarkdownEditor
          value={content}
          onChange={onChange}
          minHeight={520}
          fill
          placeholder={`# Pentest Report\n\n## Executive Summary\n...\n\n## Findings\n### Finding 1\n- **Severity**: High\n- **Location**: ...\n- **Description**: ...\n- **Proof of Concept**: ...\n- **Remediation**: ...\n\n## Flags Captured\n- FLAG{...} — ...`}
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
            {saveMutation.isPending ? "Saving…" : "Save Report"}
          </Button>
          <span style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>
            Autosaves a couple seconds after you stop typing.
          </span>
        </div>
      )}
    </div>
  );
}
