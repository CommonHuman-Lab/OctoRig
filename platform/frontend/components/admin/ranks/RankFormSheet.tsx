"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
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
  const t = useTranslations("admin.ranks");
  const tCommon = useTranslations("common");
  const tTeams = useTranslations("admin.teams");
  const tRoles = useTranslations("admin.roles");
  const tUsers = useTranslations("admin.users");
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
      title={isEdit ? t("editTitle", { name: initialValues!.name }) : t("newRank")}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose}>{tCommon("cancel")}</Button>
          <Button
            variant="primary"
            disabled={!form.name || saveMutation.isPending}
            onClick={handleSubmit}
            leftIcon={<Save size={13} />}
          >
            {saveMutation.isPending ? tCommon("saving") : isEdit ? tRoles("saveChanges") : t("createRankBtn")}
          </Button>
        </>
      }
    >
          <RankChip rank={previewRank} />

          <label className="ev-field">
            <span className="ev-label">{tTeams("nameLabel")}</span>
            <input
              className="g-input"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              placeholder={t("namePlaceholder")}
              autoComplete="off"
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">{t("colMinPoints")}</span>
            <input
              className="g-input"
              type="number"
              min={0}
              value={form.min_points}
              onChange={(e) => setForm((f) => ({ ...f, min_points: Number(e.target.value) }))}
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">{t("iconLabel")}</span>
            <EmojiPicker
              value={form.icon}
              onChange={(v) => setForm((f) => ({ ...f, icon: v }))}
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">{t("colorLabel")}</span>
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
              <span className="text-sm">{tUsers("active")}</span>
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
