"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useState } from "react";
import { useApiMutation } from "@/hooks/useApiMutation";
import { CheckCircle, XCircle, Clock } from "lucide-react";
import {
  claimSubmission,
  reviewSubmission,
  type ContentSubmission,
  type ReviewVerdict,
} from "@/lib/api/content";
import { BodyPreview } from "./BodyPreview";
import { StatusPill } from "@/components/ui/StatusPill";
import { Button } from "@/components/ui/Button";

function ReviewForm({ subId, onDone }: { subId: number; onDone: () => void }) {
  const [verdict, setVerdict] = useState<ReviewVerdict>("approved");
  const [comment, setComment] = useState("");

  const { mutate, isPending } = useApiMutation<
    { review_id: number; verdict: ReviewVerdict; submission_status: ContentSubmission["status"] },
    void
  >({
    mutationFn: () => reviewSubmission(subId, verdict, comment || undefined),
    invalidateKeys: [["content", "queue", "pending"]],
    successMessage: (data) => `Verdict submitted: ${data.verdict}`,
    errorMessage: "Failed to submit review.",
    onSuccess: onDone,
  });

  return (
    <div style={{
      marginTop: "0.5rem", padding: "0.75rem",
      background: "var(--g-surface)", border: "1px solid var(--g-border)",
      borderRadius: "4px", display: "flex", flexDirection: "column", gap: "0.5rem",
    }}>
      <div style={{ display: "flex", gap: "0.5rem" }}>
        {(["approved", "rejected", "needs_changes"] as ReviewVerdict[]).map((v) => (
          <Button
            key={v}
            size="sm"
            variant={verdict === v ? "primary" : "ghost"}
            onClick={() => setVerdict(v)}
            leftIcon={
              v === "approved" ? <CheckCircle size={12} /> :
              v === "rejected" ? <XCircle size={12} /> :
              <Clock size={12} />
            }
          >
            {v.replace("_", " ")}
          </Button>
        ))}
      </div>
      <textarea
        className="g-input"
        rows={2}
        placeholder="Optional comment…"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        style={{ resize: "vertical", fontSize: "0.8125rem" }}
      />
      <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
        <Button variant="ghost" size="sm" onClick={onDone}>Cancel</Button>
        <Button variant="primary" size="sm" disabled={isPending} onClick={() => mutate()}>
          {isPending ? "Submitting…" : "Submit Review"}
        </Button>
      </div>
    </div>
  );
}

export function PendingRow({ sub }: { sub: ContentSubmission }) {
  const [showReview, setShowReview] = useState(false);
  const [showBody, setShowBody] = useState(false);

  const { mutate: claim, isPending: claiming } = useApiMutation<ContentSubmission, void>({
    mutationFn: () => claimSubmission(sub.id),
    invalidateKeys: [["content", "queue", "pending"]],
    successMessage: "Submission claimed.",
    errorMessage: "Failed to claim submission.",
  });

  const isClaimed = sub.status === "in_review";

  return (
    <>
      <tr>
        <td>
          <Button
            variant="ghost"
            size="sm"
            style={{ padding: "0.1rem 0.4rem", fontSize: "0.7rem" }}
            onClick={() => setShowBody((v) => !v)}
            tooltip="Toggle body"
          >
            {showBody ? "▾" : "▸"}
          </Button>
          {" "}
          <span style={{ color: "var(--g-text)" }}>{sub.title}</span>
        </td>
        <td><span className="role-pill role-pill--on">{sub.content_type}</span></td>
        <td style={{ color: "var(--g-text-muted)", fontSize: "0.75rem" }}>
          {sub.author_username ?? `#${sub.author_id}`}
        </td>
        <td><StatusPill status={sub.status} /></td>
        <td>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {!isClaimed && (
              <Button variant="ghost" size="sm" disabled={claiming} onClick={() => claim()}>
                {claiming ? "Claiming…" : "Claim"}
              </Button>
            )}
            {isClaimed && (
              <Button variant="primary" size="sm" onClick={() => setShowReview((v) => !v)}>
                Review
              </Button>
            )}
          </div>
        </td>
      </tr>
      {showBody && (
        <tr>
          <td colSpan={5} style={{ padding: "0 0.75rem 0.5rem" }}>
            <BodyPreview body={sub.body} contentType={sub.content_type} />
          </td>
        </tr>
      )}
      {showReview && isClaimed && (
        <tr>
          <td colSpan={5} style={{ padding: "0 0.75rem 0.75rem" }}>
            <ReviewForm subId={sub.id} onDone={() => setShowReview(false)} />
          </td>
        </tr>
      )}
    </>
  );
}
