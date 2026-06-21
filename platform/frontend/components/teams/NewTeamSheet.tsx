"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { Plus } from "lucide-react";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";
import { Button } from "@/components/ui/Button";

interface NewTeamSheetProps {
  open: boolean;
  createMutation: {
    mutate: (data: { name: string; description?: string }) => void;
    isPending: boolean;
  };
  onClose: () => void;
}

export function NewTeamSheet({ open, createMutation, onClose }: NewTeamSheetProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  function handleClose() {
    setName("");
    setDescription("");
    onClose();
  }

  useEscapeKey(handleClose, open);

  if (!open) return null;

  return (
    <SheetShell
      title="New Team"
      onClose={handleClose}
      footer={
        <>
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            variant="primary"
            leftIcon={<Plus size={13} />}
            disabled={!name.trim() || createMutation.isPending}
            onClick={() => createMutation.mutate({ name, description: description || undefined })}
          >
            {createMutation.isPending ? "Creating…" : "Create Team"}
          </Button>
        </>
      }
    >
      <label className="ev-field">
        <span className="ev-label">Team Name</span>
        <input
          className="g-input"
          placeholder="e.g. Red Team Alpha"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoFocus
        />
      </label>
      <label className="ev-field">
        <span className="ev-label">Description (optional)</span>
        <textarea
          className="g-input"
          placeholder="What does this team do?"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
        />
      </label>
    </SheetShell>
  );
}
