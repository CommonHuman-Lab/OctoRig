// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import Link from "next/link";
import { useTranslations } from "next-intl";
import type { ScoreboardEntry } from "@/lib/api/challenges";
import type { Rank } from "@/lib/api/ranks";
import { RankChip } from "@/components/ui/RankChip";
import { RankNum } from "./RankNum";

function rankForPoints(ranks: Rank[], points: number): Rank | null {
  const eligible = ranks.filter((r) => r.is_active && r.min_points <= points);
  if (eligible.length === 0) return null;
  return eligible.reduce((a, b) => (b.min_points > a.min_points ? b : a));
}

export function ScoreRow({
  entry,
  ranks,
  isMe,
  rowRef,
}: {
  entry: ScoreboardEntry;
  ranks: Rank[];
  isMe: boolean;
  rowRef?: React.Ref<HTMLTableRowElement>;
}) {
  const t = useTranslations("scoreboard");
  const rank = rankForPoints(ranks, entry.total);
  return (
    <tr className={isMe ? "sb-row--me" : ""} ref={rowRef}>
      <td><RankNum n={entry.rank} /></td>
      <td>
        {entry.username ? (
          <Link href={`/profile/${entry.username}`} className="sb-username">
            {entry.username}
          </Link>
        ) : (
          <span className="sb-username" style={{ color: "var(--g-text-muted)" }}>{t("unknownUser")}</span>
        )}
      </td>
      <td><RankChip rank={rank} /></td>
      <td className="sb-pts">{entry.total.toLocaleString()}</td>
      <td className="sb-meta">{entry.solve_count}</td>
      <td className="sb-meta">{entry.badge_count}</td>
    </tr>
  );
}
