"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { useTranslations } from "next-intl";
import { useApiMutation } from "@/hooks/useApiMutation";
import {
  createSubmission,
  type ContentSubmission,
  type ContentType,
} from "@/lib/api/content";
import { Button } from "@/components/ui/Button";

export function CreateModal({ onClose }: { onClose: () => void }) {
  const t = useTranslations("creator");
  const tc = useTranslations("common");
  const [title, setTitle] = useState("");
  const [contentType, setContentType] = useState<ContentType>("challenge");

  const { mutate, isPending } = useApiMutation<ContentSubmission, void>({
    mutationFn: () =>
      createSubmission({ content_type: contentType, title, body: {} }),
    invalidateKeys: [["content", "mine"]],
    successMessage: t("draftCreatedToast"),
    errorMessage: t("createDraftFailed"),
    onSuccess: onClose,
  });

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-box">
        <h2 className="modal-title">{t("newDraft")}</h2>

        <div className="modal-field">
          <label className="modal-label">{tc("colTitle")}</label>
          <input
            className="g-input"
            placeholder={t("submissionTitlePlaceholder")}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            autoFocus
          />
        </div>

        <div className="modal-field">
          <label className="modal-label">{tc("colType")}</label>
          <select
            className="g-input"
            value={contentType}
            onChange={(e) => setContentType(e.target.value as ContentType)}
          >
            <option value="challenge">{t("challengeOption")}</option>
            <option value="lab">{t("labOption")}</option>
          </select>
        </div>

        <div className="modal-footer">
          <Button onClick={onClose}>{tc("cancel")}</Button>
          <Button
            variant="primary"
            disabled={!title.trim() || isPending}
            onClick={() => mutate()}
          >
            {isPending ? tc("creating") : t("createDraftBtn")}
          </Button>
        </div>
      </div>
    </div>
  );
}
