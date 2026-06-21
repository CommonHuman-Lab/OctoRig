"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Server, Flag, CheckCircle, XCircle } from "lucide-react";
import { type CandidateLabInfo } from "@/lib/api/assessments";
import { getChallenges, submitFlag, type ChallengeListItem } from "@/lib/api/challenges";
import { CopyButton } from "@/components/ui/CopyButton";
import { Button } from "@/components/ui/Button";

const STATUS_COLORS: Record<string, string> = {
  running: "var(--g-success, #22c55e)",
  starting: "var(--g-warning, #f59e0b)",
  stopping: "var(--g-warning, #f59e0b)",
  stopped: "var(--g-danger)",
  error: "var(--g-danger)",
};

function ChallengeFlagItem({ challenge }: { challenge: ChallengeListItem }) {
  const [flag, setFlag] = useState("");
  const [result, setResult] = useState<{ correct: boolean; message: string } | null>(null);
  const qc = useQueryClient();

  const submitMutation = useMutation({
    mutationFn: () => submitFlag(challenge.slug, flag),
    onSuccess: (data) => {
      setResult({ correct: data.correct, message: data.message });
      if (data.correct) {
        setFlag("");
        qc.invalidateQueries({ queryKey: ["candidate-challenges"] });
      }
    },
    onError: () => setResult({ correct: false, message: "Failed to submit flag." }),
  });

  const solved = challenge.solved_by_me;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 6,
        padding: "8px 0",
        borderBottom: "1px solid var(--g-border)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.8rem" }}>
        {solved ? (
          <CheckCircle size={13} style={{ color: "var(--g-success, #22c55e)", flexShrink: 0 }} />
        ) : (
          <Flag size={13} style={{ color: "var(--g-text-muted)", flexShrink: 0 }} />
        )}
        <span style={{ color: "var(--g-text)", flex: 1 }}>{challenge.title}</span>
        <span style={{ color: "var(--g-text-muted)", fontSize: "0.7rem", fontFamily: "var(--font-mono, monospace)" }}>
          {challenge.points} pts
        </span>
      </div>

      {!solved && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (flag.trim()) submitMutation.mutate();
          }}
          style={{ display: "flex", gap: 6 }}
        >
          <input
            className="g-input font-mono"
            style={{ fontSize: "0.75rem", padding: "5px 8px" }}
            placeholder="FLAG{...}"
            value={flag}
            onChange={(e) => setFlag(e.target.value)}
            disabled={submitMutation.isPending}
            spellCheck={false}
            autoComplete="off"
          />
          <Button
            type="submit"
            variant="primary"
            size="sm"
            disabled={submitMutation.isPending || !flag.trim()}
          >
            {submitMutation.isPending ? "…" : "Submit"}
          </Button>
        </form>
      )}

      {result && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            fontSize: "0.72rem",
            color: result.correct ? "var(--g-success, #22c55e)" : "var(--g-danger)",
          }}
        >
          {result.correct ? <CheckCircle size={11} /> : <XCircle size={11} />}
          {result.message}
        </div>
      )}
    </div>
  );
}

function LabChallenges({ labSlug }: { labSlug: string }) {
  const { data: challenges = [], isLoading } = useQuery<ChallengeListItem[]>({
    queryKey: ["candidate-challenges", labSlug],
    queryFn: () => getChallenges({ lab_slug: labSlug }),
  });

  if (isLoading) {
    return <p style={{ color: "var(--g-text-muted)", fontSize: "0.78rem", margin: "10px 0 0" }}>Loading flags…</p>;
  }
  if (challenges.length === 0) return null;

  return (
    <div style={{ marginTop: 12 }}>
      <div style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--g-text-muted)", marginBottom: 4 }}>
        Flags ({challenges.filter((c) => c.solved_by_me).length}/{challenges.length})
      </div>
      {challenges.map((ch) => (
        <ChallengeFlagItem key={ch.slug} challenge={ch} />
      ))}
    </div>
  );
}

export function LabCard({ lab, expired }: { lab: CandidateLabInfo; expired: boolean }) {
  return (
    <div
      style={{
        background: "var(--g-card)",
        border: "1px solid var(--g-border)",
        borderRadius: 10,
        padding: "16px 20px",
        flex: "1 1 280px",
        minWidth: 260,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Server size={16} style={{ color: "var(--g-accent)" }} />
          <span style={{ fontWeight: 600, fontSize: "0.95rem", color: "var(--g-text)" }}>
            {lab.display_name}
          </span>
        </div>
        {lab.status && (
          <span
            style={{
              fontSize: "0.7rem",
              fontFamily: "var(--font-mono, monospace)",
              textTransform: "uppercase",
              color: STATUS_COLORS[lab.status] ?? "var(--g-text-muted)",
              letterSpacing: "0.04em",
            }}
          >
            {lab.status}
          </span>
        )}
      </div>

      {lab.status === "running" && lab.access_info.length > 0 && (
        <div
          style={{
            background: "var(--g-surface)",
            borderRadius: 6,
            padding: "10px 12px",
            marginBottom: 0,
            display: "flex",
            flexDirection: "column",
            gap: 4,
          }}
        >
          {lab.access_info.map((info) => (
            <div key={info.key} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.78rem" }}>
              <span style={{ color: "var(--g-text-muted)", minWidth: 40 }}>{info.key}</span>
              <code
                style={{
                  color: "var(--g-text)",
                  fontFamily: "var(--font-mono, monospace)",
                  fontSize: "0.75rem",
                  wordBreak: "break-all",
                  flex: 1,
                }}
              >
                {info.value}
              </code>
              <CopyButton value={info.value} />
            </div>
          ))}
        </div>
      )}

      {lab.status === "running" && <LabChallenges labSlug={lab.slug} />}

      {lab.status === "starting" && (
        <p style={{ color: "var(--g-text-muted)", fontSize: "0.8rem", margin: 0 }}>
          Container is starting up — this may take a minute…
        </p>
      )}

      {!lab.status && !expired && (
        <p style={{ color: "var(--g-text-muted)", fontSize: "0.8rem", margin: 0 }}>
          Not started yet.
        </p>
      )}

      {expired && (
        <p style={{ color: "var(--g-danger)", fontSize: "0.8rem", margin: 0 }}>
          Assessment expired — lab has been shut down.
        </p>
      )}
    </div>
  );
}
