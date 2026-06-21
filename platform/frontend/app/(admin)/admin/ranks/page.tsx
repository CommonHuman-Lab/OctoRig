"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./ranks-admin.css";

import { useState } from "react";
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
    successMessage: () => (selected ? "Rank updated." : "Rank created."),
    errorMessage: "Failed to save rank.",
    onSuccess: closeSheet,
  });

  const toggleMutation = useApiMutation({
    mutationFn: (rank: Rank) => updateAdminRank(rank.id, { is_active: !rank.is_active }),
    invalidateKeys: [["admin-ranks"], ["ranks"]],
    errorMessage: "Failed to update rank.",
  });

  const deleteMutation = useApiMutation({
    mutationFn: (id: number) => deleteAdminRank(id),
    invalidateKeys: [["admin-ranks"], ["ranks"]],
    successMessage: "Rank deleted.",
    errorMessage: "Failed to delete rank.",
    onSuccess: closeSheet,
  });

  function handleDelete(rank: Rank) {
    confirm({
      title: "Delete rank",
      body: `Delete "${rank.name}"? Users currently at this rank will drop to the one below.`,
      confirmLabel: "Delete",
      dangerous: true,
      onConfirm: () => deleteMutation.mutate(rank.id),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title font-mono">Ranks</h1>
          <p className="page-sub">{ranks.length} ranks configured</p>
        </div>
        <Button variant="primary" leftIcon={<Plus size={13} />} onClick={openCreate}>
          New Rank
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
