"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useTranslations } from "next-intl";
import type { ContentStatus } from "@/lib/api/content";

const STATUS_STYLE: Record<ContentStatus, { bg: string; color: string }> = {
  draft:          { bg: "color-mix(in srgb, var(--g-text-muted) 15%, transparent)", color: "var(--g-text-muted)" },
  pending_review: { bg: "color-mix(in srgb, var(--g-warning) 15%, transparent)",    color: "var(--g-warning)" },
  in_review:      { bg: "color-mix(in srgb, var(--g-accent) 15%, transparent)",     color: "var(--g-accent)" },
  approved:       { bg: "color-mix(in srgb, var(--g-success) 15%, transparent)",    color: "var(--g-success)" },
  published:      { bg: "color-mix(in srgb, var(--g-success) 15%, transparent)",    color: "var(--g-success)" },
  rejected:       { bg: "color-mix(in srgb, var(--g-danger) 15%, transparent)",     color: "var(--g-danger)" },
};

const STATUS_KEY: Record<ContentStatus, string> = {
  draft: "statusDraft",
  pending_review: "statusPendingReview",
  in_review: "statusInReview",
  approved: "statusApproved",
  published: "statusPublished",
  rejected: "statusRejected",
};

export function StatusPill({ status }: { status: ContentStatus }) {
  const t = useTranslations("content");
  const s = STATUS_STYLE[status];
  return (
    <span className="g-status-pill" style={{ background: s.bg, color: s.color }}>
      {t(STATUS_KEY[status] as any)}
    </span>
  );
}
