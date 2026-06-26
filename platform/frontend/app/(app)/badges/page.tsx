"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./badges.css";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { Award, RefreshCw } from "lucide-react";
import { getBadges, evaluateAchievements } from "@/lib/api/badges";
import { getMyRank } from "@/lib/api/ranks";
import { useNotificationsStore } from "@/stores/notifications.store";
import { BadgeCard } from "@/components/badges/BadgeCard";
import { RankProgressCard } from "@/components/badges/RankProgressCard";
import { FilterPills } from "@/components/ui/FilterPills";
import { Button } from "@/components/ui/Button";
import { STALE_TIME } from "@/lib/config";

const CATEGORIES = ["all", "milestone", "competition", "skill"] as const;
type CategoryFilter = typeof CATEGORIES[number];
type StatusFilter = "all" | "earned" | "locked";

const CATEGORY_KEY: Record<string, string> = {
  milestone: "categoryMilestone",
  competition: "categoryCompetition",
  skill: "categorySkill",
  other: "categoryOther",
};

export default function BadgesPage() {
  const t = useTranslations("badges");
  const tn = useTranslations("nav");
  const tc = useTranslations("common");
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
        push("success", t("unlockedToast", { names: newBadges.join(", ") }));
      } else {
        push("info", t("noNewBadges"));
      }
    },
    onError: () => push("error", t("evalFailed")),
  });

  const { data: myRank } = useQuery({
    queryKey: ["rank", "me"],
    queryFn: getMyRank,
    staleTime: STALE_TIME.MEDIUM,
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
            {tn("badges")}
          </h1>
          {!isLoading && <p className="page-sub">{t("earnedCount", { earned, total })}</p>}
        </div>
        <Button
          leftIcon={<RefreshCw size={13} />}
          onClick={() => evalMutation.mutate()}
          disabled={evalMutation.isPending}
        >
          {evalMutation.isPending ? t("checking") : t("checkAchievements")}
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
              label: (v) => v === "all" ? tc("all") : t(CATEGORY_KEY[v!] as any),
            },
            {
              options: ["all", "earned", "locked"],
              value: statusFilter,
              onChange: (v) => setStatusFilter(v as StatusFilter),
              label: (v) => v === "all" ? tc("all") : v === "earned" ? t("statusEarned") : t("statusLocked"),
            },
          ]}
        />
      </div>

      {isLoading ? (
        <div className="text-muted text-xs">{t("loadingBadges")}</div>
      ) : filtered.length === 0 ? (
        <div className="text-muted text-xs">{t("noMatch")}</div>
      ) : catFilter !== "all" ? (
        <div className="g-grid-auto badge-grid">
          {filtered.map((b) => <BadgeCard key={b.id} badge={b} />)}
        </div>
      ) : (
        <div className="categories">
          {Object.entries(byCategory).map(([cat, catBadges]) => (
            <section key={cat}>
              <h2 className="cat-title">{t(CATEGORY_KEY[cat] as any)}</h2>
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
