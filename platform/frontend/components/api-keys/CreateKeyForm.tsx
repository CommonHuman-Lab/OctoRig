"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useState } from "react";
import { Button } from "@/components/ui/Button";

export function CreateKeyForm({
  onSubmit,
  isPending,
  onCancel,
}: {
  onSubmit: (name: string, expiry: string) => void;
  isPending: boolean;
  onCancel: () => void;
}) {
  const [name, setName] = useState("");
  const [expiry, setExpiry] = useState("");

  function handleSubmit() {
    onSubmit(name, expiry);
    setName("");
    setExpiry("");
  }

  return (
    <div className="create-form g-panel">
      <div className="g-panel-header">
        <span className="font-mono text-sm">New API Key</span>
      </div>
      <div className="create-body">
        <div className="field">
          <label className="text-11 text-muted">Key Name</label>
          <input
            className="g-input"
            placeholder="e.g. CI/CD Pipeline"
            value={name}
            onChange={(e) => setName(e.target.value)}
            autoFocus
          />
        </div>
        <div className="field">
          <label className="text-11 text-muted">Expiry Date (optional)</label>
          <input
            className="g-input"
            type="datetime-local"
            value={expiry}
            onChange={(e) => setExpiry(e.target.value)}
          />
        </div>
        <div className="form-actions">
          <Button onClick={onCancel}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={!name.trim() || isPending}
          >
            {isPending ? "Creating…" : "Create Key"}
          </Button>
        </div>
      </div>
    </div>
  );
}
