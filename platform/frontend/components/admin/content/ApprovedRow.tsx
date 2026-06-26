"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Printer } from "lucide-react";
import {
  publishSubmission,
  type ContentSubmission,
} from "@/lib/api/content";
import { useApiMutation } from "@/hooks/useApiMutation";
import { BodyPreview } from "./BodyPreview";
import { StatusPill } from "@/components/ui/StatusPill";
import { Button } from "@/components/ui/Button";

export function ApprovedRow({ sub }: { sub: ContentSubmission }) {
  const t = useTranslations("admin.content");
  const [showBody, setShowBody] = useState(false);

  const { mutate: publish, isPending } = useApiMutation<ContentSubmission, void>({
    mutationFn: () => publishSubmission(sub.id),
    invalidateKeys: [["content", "queue", "approved"]],
    successMessage: t("toastSubmissionPublished"),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("toastPublishFailed"),
  });

  return (
    <>
      <tr>
        <td>
          <Button
            variant="ghost"
            size="sm"
            style={{ padding: "0.1rem 0.4rem", fontSize: "0.7rem" }}
            onClick={() => setShowBody((v) => !v)}
            tooltip={t("toggleBodyTooltip")}
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
          <Button
            variant="primary"
            size="sm"
            disabled={isPending}
            onClick={() => publish()}
            leftIcon={<Printer size={12} />}
          >
            {isPending ? t("publishingBtn") : t("publishBtn")}
          </Button>
        </td>
      </tr>
      {showBody && (
        <tr>
          <td colSpan={5} style={{ padding: "0 0.75rem 0.75rem" }}>
            <BodyPreview body={sub.body} contentType={sub.content_type} />
          </td>
        </tr>
      )}
    </>
  );
}
