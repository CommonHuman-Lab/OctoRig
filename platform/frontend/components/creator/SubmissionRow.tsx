"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { Edit3, FileText } from "lucide-react";
import type { ContentSubmission } from "@/lib/api/content";
import { formatDate } from "@/lib/utils/date";
import { StatusPill } from "@/components/ui/StatusPill";
import { Button } from "@/components/ui/Button";
import { ChallengeBodyEditor } from "./ChallengeBodyEditor";

export function SubmissionRow({ sub }: { sub: ContentSubmission }) {
  const [expanded, setExpanded] = useState(false);

  const isEditable = sub.status === "draft" || sub.status === "rejected";
  const showEditor = isEditable && sub.content_type === "challenge";

  return (
    <>
      <tr>
        <td style={{ color: "var(--g-text)" }}>{sub.title}</td>
        <td>
          <span className="g-status-pill" style={{ background: "color-mix(in srgb, var(--g-accent) 10%, transparent)", color: "var(--g-accent)" }}>
            {sub.content_type}
          </span>
        </td>
        <td><StatusPill status={sub.status} /></td>
        <td style={{ color: "var(--g-text-muted)", fontFamily: "var(--font-mono, monospace)", fontSize: "0.75rem" }}>
          {formatDate(sub.updated_at)}
        </td>
        <td>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <Button
              size="sm"
              variant={expanded ? "subtle" : "ghost"}
              onClick={() => setExpanded((v) => !v)}
              leftIcon={isEditable ? <Edit3 size={12} /> : <FileText size={12} />}
            >
              {expanded ? "Hide" : isEditable ? "Edit" : "View"}
            </Button>
          </div>
        </td>
      </tr>
      {expanded && (
        <tr>
          <td colSpan={5} style={{ padding: "0 0.75rem 0.75rem" }}>
            {showEditor ? (
              <ChallengeBodyEditor sub={sub} />
            ) : (
              <div style={{
                background: "var(--g-surface)",
                border: "1px solid var(--g-border)",
                borderRadius: "4px",
                padding: "0.75rem",
              }}>
                <div style={{ fontSize: "0.625rem", textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--g-text-muted)", marginBottom: "0.5rem" }}>
                  Body
                </div>
                {Object.keys(sub.body).length === 0 ? (
                  <span style={{ fontSize: "0.75rem", color: "var(--g-text-muted)", fontStyle: "italic" }}>
                    Empty — no body content yet.
                  </span>
                ) : (
                  <pre style={{ margin: 0, fontSize: "0.75rem", color: "var(--g-text-secondary)", whiteSpace: "pre-wrap", wordBreak: "break-all", fontFamily: "var(--font-mono, monospace)" }}>
                    {JSON.stringify(sub.body, null, 2)}
                  </pre>
                )}
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  );
}
