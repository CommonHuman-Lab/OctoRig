"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useState } from "react";
import { Save } from "lucide-react";
import { type AdminTeam } from "@/lib/api/admin";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";
import { Button } from "@/components/ui/Button";

interface TeamEditSheetProps {
  open: boolean;
  team: AdminTeam | null;
  saveMutation: { mutate: (data: { name: string }) => void; isPending: boolean };
  onClose: () => void;
}

export function TeamEditSheet({ open, team, saveMutation, onClose }: TeamEditSheetProps) {
  const [name, setName] = useState("");

  useEffect(() => {
    if (open) setName(team?.name ?? "");
  }, [open, team]);

  useEscapeKey(onClose, open);

  if (!open || !team) return null;

  return (
    <SheetShell
      title={<>Edit Team — {team.slug}</>}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose}>Cancel</Button>
          <Button
            variant="primary"
            disabled={!name || saveMutation.isPending}
            onClick={() => saveMutation.mutate({ name })}
            leftIcon={<Save size={13} />}
          >
            {saveMutation.isPending ? "Saving…" : "Save Changes"}
          </Button>
        </>
      }
    >
      <label className="ev-field">
        <span className="ev-label">Name</span>
        <input
          className="g-input"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoFocus
        />
      </label>
    </SheetShell>
  );
}
