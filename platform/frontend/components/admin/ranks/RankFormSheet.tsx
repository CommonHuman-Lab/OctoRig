"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useState } from "react";
import { Save } from "lucide-react";
import type { Rank } from "@/lib/api/ranks";
import { RankChip } from "@/components/ui/RankChip";
import { EmojiPicker } from "@/components/ui/EmojiPicker";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";
import { Button } from "@/components/ui/Button";

const BLANK_FORM = { name: "", min_points: 0, icon: "", color: "#6b7280" };
export type RankFormState = typeof BLANK_FORM;

function rankToForm(r: Rank): RankFormState {
  return { name: r.name, min_points: r.min_points, icon: r.icon ?? "", color: r.color ?? "#6b7280" };
}

interface RankFormSheetProps {
  open: boolean;
  initialValues?: Rank | null;
  saveMutation: {
    mutate: (data: { name: string; min_points: number; icon?: string; color?: string }) => void;
    isPending: boolean;
  };
  onToggleActive: (rank: Rank) => void;
  onClose: () => void;
}

export function RankFormSheet({ open, initialValues, saveMutation, onToggleActive, onClose }: RankFormSheetProps) {
  const [form, setForm] = useState<RankFormState>(BLANK_FORM);
  const isEdit = !!initialValues;

  useEffect(() => {
    if (open) setForm(initialValues ? rankToForm(initialValues) : BLANK_FORM);
  }, [open, initialValues]);

  useEscapeKey(onClose, open);

  if (!open) return null;

  const previewRank = form.name
    ? { id: 0, name: form.name, color: form.color || null, icon: form.icon || null, min_points: 0, is_active: true }
    : null;

  function handleSubmit() {
    if (!form.name) return;
    saveMutation.mutate({
      name: form.name,
      min_points: form.min_points,
      icon: form.icon || undefined,
      color: form.color || undefined,
    });
  }

  return (
    <SheetShell
      title={isEdit ? `Edit — ${initialValues!.name}` : "New Rank"}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose}>Cancel</Button>
          <Button
            variant="primary"
            disabled={!form.name || saveMutation.isPending}
            onClick={handleSubmit}
            leftIcon={<Save size={13} />}
          >
            {saveMutation.isPending ? "Saving…" : isEdit ? "Save Changes" : "Create Rank"}
          </Button>
        </>
      }
    >
          <RankChip rank={previewRank} />

          <label className="ev-field">
            <span className="ev-label">Name</span>
            <input
              className="g-input"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              placeholder="e.g. Hacker"
              autoComplete="off"
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">Min Points</span>
            <input
              className="g-input"
              type="number"
              min={0}
              value={form.min_points}
              onChange={(e) => setForm((f) => ({ ...f, min_points: Number(e.target.value) }))}
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">Icon</span>
            <EmojiPicker
              value={form.icon}
              onChange={(v) => setForm((f) => ({ ...f, icon: v }))}
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">Color</span>
            <div className="color-row">
              <input
                type="color"
                value={form.color}
                onChange={(e) => setForm((f) => ({ ...f, color: e.target.value }))}
              />
              <input
                className="g-input"
                value={form.color}
                onChange={(e) => setForm((f) => ({ ...f, color: e.target.value }))}
                placeholder="#6b7280"
                style={{ flex: 1 }}
                autoComplete="off"
              />
            </div>
          </label>

          {isEdit && (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span className="text-sm">Active</span>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={initialValues!.is_active}
                  onChange={() => onToggleActive(initialValues!)}
                />
                <span className="toggle-track" />
              </label>
            </div>
          )}
    </SheetShell>
  );
}
