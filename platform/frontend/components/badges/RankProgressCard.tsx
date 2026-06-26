// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useTranslations } from "next-intl";
import type { UserRank } from "@/lib/api/ranks";

export function RankProgressCard({ myRank }: { myRank: UserRank }) {
  const t = useTranslations("badges");
  if (!myRank.rank) return null;

  return (
    <div className="g-card rank-progress-card" style={{ marginBottom: "1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
        <span
          className="font-mono"
          style={{ fontSize: "0.8rem", fontWeight: 600, color: myRank.rank.color ?? "var(--g-text)" }}
        >
          {myRank.rank.name}
        </span>
        {myRank.next_rank ? (
          <span className="font-mono" style={{ fontSize: "0.7rem", color: "var(--g-text-muted)" }}>
            {t("rankProgress", {
              points: myRank.points.toLocaleString(),
              nextPoints: myRank.next_rank.min_points.toLocaleString(),
              nextName: myRank.next_rank.name,
            })}
          </span>
        ) : (
          <span className="font-mono" style={{ fontSize: "0.7rem", color: "var(--g-text-muted)" }}>
            {t("maxRank", { points: myRank.points.toLocaleString() })}
          </span>
        )}
      </div>
      <div style={{ height: 6, borderRadius: 99, background: "var(--g-border)", overflow: "hidden" }}>
        <div
          style={{
            height: "100%",
            borderRadius: 99,
            background: myRank.rank.color ?? "var(--g-accent)",
            width: `${Math.min(myRank.progress_pct, 100)}%`,
            transition: "width 0.4s ease",
          }}
        />
      </div>
    </div>
  );
}
