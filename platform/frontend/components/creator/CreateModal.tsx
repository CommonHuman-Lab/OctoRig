"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { useApiMutation } from "@/hooks/useApiMutation";
import {
  createSubmission,
  type ContentSubmission,
  type ContentType,
} from "@/lib/api/content";

export function CreateModal({ onClose }: { onClose: () => void }) {
  const [title, setTitle] = useState("");
  const [contentType, setContentType] = useState<ContentType>("challenge");

  const { mutate, isPending } = useApiMutation<ContentSubmission, void>({
    mutationFn: () =>
      createSubmission({ content_type: contentType, title, body: {} }),
    invalidateKeys: [["content", "mine"]],
    successMessage: "Draft created.",
    errorMessage: "Failed to create draft.",
    onSuccess: onClose,
  });

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-box">
        <h2 className="modal-title">New Draft</h2>

        <div className="modal-field">
          <label className="modal-label">Title</label>
          <input
            className="g-input"
            placeholder="Submission title…"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            autoFocus
          />
        </div>

        <div className="modal-field">
          <label className="modal-label">Type</label>
          <select
            className="g-input"
            value={contentType}
            onChange={(e) => setContentType(e.target.value as ContentType)}
          >
            <option value="challenge">Challenge</option>
            <option value="lab">Lab</option>
          </select>
        </div>

        <div className="modal-footer">
          <button className="g-btn g-btn-ghost" onClick={onClose}>Cancel</button>
          <button
            className="g-btn g-btn-primary"
            disabled={!title.trim() || isPending}
            onClick={() => mutate()}
          >
            {isPending ? "Creating…" : "Create Draft"}
          </button>
        </div>
      </div>
    </div>
  );
}
