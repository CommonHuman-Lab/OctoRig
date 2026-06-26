"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./ranks-admin.css";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import {
  getAdminRanks,
  createAdminRank,
  updateAdminRank,
  deleteAdminRank,
  type Rank,
} from "@/lib/api/ranks";
import { useConfirmStore } from "@/stores/confirm.store";
import { RankTable } from "@/components/admin/ranks/RankTable";
import { RankFormSheet } from "@/components/admin/ranks/RankFormSheet";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Button } from "@/components/ui/Button";

export default function AdminRanksPage() {
  const t = useTranslations("admin.ranks");
  const tCommon = useTranslations("common");
  const { confirm } = useConfirmStore();

  const [sheetOpen, setSheetOpen] = useState(false);
  const [selected, setSelected] = useState<Rank | null>(null);

  const { data: ranks = [], isLoading } = useQuery({
    queryKey: ["admin-ranks"],
    queryFn: getAdminRanks,
  });

  function openCreate() {
    setSelected(null);
    setSheetOpen(true);
  }

  function openEdit(rank: Rank) {
    setSelected(rank);
    setSheetOpen(true);
  }

  function closeSheet() {
    setSheetOpen(false);
    setSelected(null);
  }

  const saveMutation = useApiMutation({
    mutationFn: (payload: { name: string; min_points: number; icon?: string; color?: string }) =>
      selected ? updateAdminRank(selected.id, payload) : createAdminRank(payload),
    invalidateKeys: [["admin-ranks"], ["ranks"]],
    successMessage: () => (selected ? t("toastRankUpdated") : t("toastRankCreated")),
    errorMessage: t("toastSaveRankFailed"),
    onSuccess: closeSheet,
  });

  const toggleMutation = useApiMutation({
    mutationFn: (rank: Rank) => updateAdminRank(rank.id, { is_active: !rank.is_active }),
    invalidateKeys: [["admin-ranks"], ["ranks"]],
    errorMessage: t("toastUpdateRankFailed"),
  });

  const deleteMutation = useApiMutation({
    mutationFn: (id: number) => deleteAdminRank(id),
    invalidateKeys: [["admin-ranks"], ["ranks"]],
    successMessage: t("toastRankDeleted"),
    errorMessage: t("toastDeleteRankFailed"),
    onSuccess: closeSheet,
  });

  function handleDelete(rank: Rank) {
    confirm({
      title: t("deleteRankTitle"),
      body: t("deleteRankBody", { name: rank.name }),
      confirmLabel: tCommon("delete"),
      dangerous: true,
      onConfirm: () => deleteMutation.mutate(rank.id),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title font-mono">{t("title")}</h1>
          <p className="page-sub">{t("ranksConfigured", { count: ranks.length })}</p>
        </div>
        <Button variant="primary" leftIcon={<Plus size={13} />} onClick={openCreate}>
          {t("newRank")}
        </Button>
      </div>

      <div className="g-card" style={{ padding: 0, overflow: "hidden" }}>
        <RankTable
          ranks={ranks}
          selected={selected}
          isLoading={isLoading}
          onEdit={openEdit}
          onDelete={handleDelete}
        />
      </div>

      <RankFormSheet
        open={sheetOpen}
        initialValues={selected}
        saveMutation={saveMutation}
        onToggleActive={(rank) => toggleMutation.mutate(rank)}
        onClose={closeSheet}
      />
    </div>
  );
}
