// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useTranslations } from "next-intl";
import { Pencil, Trash2 } from "lucide-react";
import type { Rank } from "@/lib/api/ranks";
import { RankChip } from "@/components/ui/RankChip";
import { Button } from "@/components/ui/Button";

export function RankTable({
  ranks,
  selected,
  isLoading,
  onEdit,
  onDelete,
}: {
  ranks: Rank[];
  selected: Rank | null;
  isLoading: boolean;
  onEdit: (rank: Rank) => void;
  onDelete: (rank: Rank) => void;
}) {
  const t = useTranslations("admin.ranks");
  const tCommon = useTranslations("common");
  const tUsers = useTranslations("admin.users");

  if (isLoading) {
    return <div className="text-muted text-sm" style={{ padding: "1rem" }}>{tCommon("loading")}</div>;
  }

  return (
    <table className="rank-table">
      <thead>
        <tr>
          <th>{t("colRank")}</th>
          <th>{t("colMinPoints")}</th>
          <th>{tUsers("colStatus")}</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {ranks.map((rank) => (
          <tr
            key={rank.id}
            className={selected?.id === rank.id ? "selected" : ""}
            style={{ cursor: "pointer" }}
            onClick={() => onEdit(rank)}
          >
            <td>
              <RankChip rank={rank} />
            </td>
            <td className="rank-pts">{rank.min_points.toLocaleString()}</td>
            <td>
              <span
                className="inactive-pill"
                style={rank.is_active ? { background: "var(--g-accent-dim)", color: "var(--g-accent)" } : undefined}
              >
                {rank.is_active ? tUsers("active") : tUsers("inactive")}
              </span>
            </td>
            <td>
              <div style={{ display: "flex", gap: "0.4rem" }} onClick={(e) => e.stopPropagation()}>
                <Button
                  style={{ padding: "0.2rem 0.4rem" }}
                  onClick={() => onEdit(rank)}
                  tooltip={tCommon("edit")}
                  leftIcon={<Pencil size={12} />}
                />
                <Button
                  style={{ padding: "0.2rem 0.4rem", color: "var(--g-danger)" }}
                  onClick={() => onDelete(rank)}
                  tooltip={tCommon("delete")}
                  leftIcon={<Trash2 size={12} />}
                />
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
