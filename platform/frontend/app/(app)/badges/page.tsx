"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./badges.css";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Award, RefreshCw } from "lucide-react";
import { getBadges, evaluateAchievements } from "@/lib/api/badges";
import { getMyRank } from "@/lib/api/ranks";
import { useNotificationsStore } from "@/stores/notifications.store";
import { BadgeCard } from "@/components/badges/BadgeCard";
import { RankProgressCard } from "@/components/badges/RankProgressCard";
import { FilterPills } from "@/components/ui/FilterPills";
import { Button } from "@/components/ui/Button";

const CATEGORIES = ["all", "milestone", "competition", "skill"] as const;
type CategoryFilter = typeof CATEGORIES[number];
type StatusFilter = "all" | "earned" | "locked";

export default function BadgesPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const [catFilter, setCatFilter] = useState<CategoryFilter>("all");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");

  const { data: badges = [], isLoading } = useQuery({
    queryKey: ["badges"],
    queryFn: getBadges,
  });

  const evalMutation = useMutation({
    mutationFn: evaluateAchievements,
    onSuccess: (newBadges) => {
      qc.invalidateQueries({ queryKey: ["badges"] });
      if (newBadges.length > 0) {
        push("success", `Unlocked: ${newBadges.join(", ")}`);
      } else {
        push("info", "No new badges earned yet.");
      }
    },
    onError: () => push("error", "Failed to evaluate achievements"),
  });

  const { data: myRank } = useQuery({
    queryKey: ["rank", "me"],
    queryFn: getMyRank,
    staleTime: 60_000,
  });

  const earned = badges.filter((b) => b.earned).length;
  const total = badges.length;

  const filtered = badges.filter((b) => {
    if (catFilter !== "all" && b.category !== catFilter) return false;
    if (statusFilter === "earned" && !b.earned) return false;
    if (statusFilter === "locked" && b.earned) return false;
    return true;
  });

  const byCategory = filtered.reduce<Record<string, typeof filtered>>((acc, b) => {
    const cat = b.category ?? "other";
    (acc[cat] ??= []).push(b);
    return acc;
  }, {});

  return (
    <div className="page">
      <div className="page-header page-header--top">
        <div>
          <h1 className="page-title font-mono">
            <Award size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
            Badges
          </h1>
          {!isLoading && <p className="page-sub">{earned}/{total} earned</p>}
        </div>
        <Button
          leftIcon={<RefreshCw size={13} />}
          onClick={() => evalMutation.mutate()}
          disabled={evalMutation.isPending}
        >
          {evalMutation.isPending ? "Checking…" : "Check Achievements"}
        </Button>
      </div>

      {myRank && <RankProgressCard myRank={myRank} />}

      <div className="filter-bar">
        <FilterPills
          groups={[
            {
              options: [...CATEGORIES],
              value: catFilter,
              onChange: (v) => setCatFilter(v as CategoryFilter),
              label: (v) => v === "all" ? "All" : v!.charAt(0).toUpperCase() + v!.slice(1),
            },
            {
              options: ["all", "earned", "locked"],
              value: statusFilter,
              onChange: (v) => setStatusFilter(v as StatusFilter),
            },
          ]}
        />
      </div>

      {isLoading ? (
        <div className="text-muted text-xs">Loading badges…</div>
      ) : filtered.length === 0 ? (
        <div className="text-muted text-xs">No badges match this filter.</div>
      ) : catFilter !== "all" ? (
        <div className="g-grid-auto badge-grid">
          {filtered.map((b) => <BadgeCard key={b.id} badge={b} />)}
        </div>
      ) : (
        <div className="categories">
          {Object.entries(byCategory).map(([cat, catBadges]) => (
            <section key={cat}>
              <h2 className="cat-title">{cat}</h2>
              <div className="g-grid-auto badge-grid">
                {catBadges.map((b) => <BadgeCard key={b.id} badge={b} />)}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
