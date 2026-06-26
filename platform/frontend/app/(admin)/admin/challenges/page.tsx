"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../admin.css";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { ToggleLeft, ToggleRight, ExternalLink } from "lucide-react";
import Link from "next/link";
import {
  getAdminChallenges,
  setChallengeActive,
  type ChallengeListItem,
  type ChallengeDifficulty,
} from "@/lib/api/challenges";
import { useApiMutation } from "@/hooks/useApiMutation";
import { DIFF_COLOR } from "@/lib/utils/difficulty";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { FilterPills } from "@/components/ui/FilterPills";
import { Button } from "@/components/ui/Button";

function ChallengeRow({ ch }: { ch: ChallengeListItem }) {
  const t = useTranslations("admin.challenges");
  const { mutate, isPending } = useApiMutation<{ slug: string; is_active: boolean }, void>({
    mutationFn: () => setChallengeActive(ch.slug, !ch.is_active),
    invalidateKeys: [["admin", "challenges"]],
    successMessage: (res) =>
      res.is_active ? t("toastChallengeEnabled", { title: ch.title }) : t("toastChallengeDisabled", { title: ch.title }),
    errorMessage: t("toastUpdateChallengeFailed"),
  });

  return (
    <tr style={{ opacity: ch.is_active ? 1 : 0.5 }}>
      <td>
        <Link
          href={`/challenges/${ch.slug}`}
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: "var(--g-text)", display: "inline-flex", alignItems: "center", gap: "0.3rem" }}
        >
          {ch.title}
          <ExternalLink size={10} style={{ color: "var(--g-text-muted)" }} />
        </Link>
      </td>
      <td>
        <span style={{
          fontFamily: "var(--font-mono, monospace)",
          fontSize: "0.75rem",
          color: "var(--g-text-muted)",
        }}>
          {ch.category}
        </span>
      </td>
      <td>
        <span style={{ fontSize: "0.75rem", color: DIFF_COLOR[ch.difficulty] }}>
          {ch.difficulty}
        </span>
      </td>
      <td>
        <span style={{
          fontSize: "0.7rem",
          color: "var(--g-text-muted)",
          background: "var(--g-surface-2)",
          padding: "0.1rem 0.35rem",
          borderRadius: "3px",
          fontFamily: "var(--font-mono, monospace)",
        }}>
          {ch.challenge_type.replace("_", " ")}
        </span>
      </td>
      <td style={{ color: "var(--g-text-muted)", fontSize: "0.75rem", textAlign: "right" }}>
        {ch.points}
      </td>
      <td style={{ color: "var(--g-text-muted)", fontSize: "0.75rem", textAlign: "right" }}>
        {ch.solve_count}
      </td>
      <td>
        <Button
          variant="ghost"
          size="sm"
          disabled={isPending}
          onClick={() => mutate()}
          tooltip={ch.is_active ? t("disableChallengeTooltip") : t("enableChallengeTooltip")}
          leftIcon={ch.is_active ? (
            <ToggleRight size={14} style={{ color: "var(--g-success)" }} />
          ) : (
            <ToggleLeft size={14} style={{ color: "var(--g-text-muted)" }} />
          )}
        >
          {isPending ? "…" : ch.is_active ? t("enabledLabel") : t("disabledLabel")}
        </Button>
      </td>
    </tr>
  );
}

export default function AdminChallengesPage() {
  const t = useTranslations("admin.challenges");
  const tCommon = useTranslations("common");
  const tUsers = useTranslations("admin.users");

  function filterLabel(v: string | undefined) {
    if (v === "active") return tUsers("active");
    if (v === "inactive") return tUsers("inactive");
    return tCommon("all");
  }

  const [filter, setFilter] = useState<"all" | "active" | "inactive">("all");
  const [search, setSearch] = useState("");

  const { data: challenges = [], isLoading } = useQuery({
    queryKey: ["admin", "challenges"],
    queryFn: getAdminChallenges,
  });

  const filtered = challenges.filter((ch) => {
    if (filter === "active" && !ch.is_active) return false;
    if (filter === "inactive" && ch.is_active) return false;
    if (search && !ch.title.toLowerCase().includes(search.toLowerCase()) &&
        !ch.category.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const activeCount = challenges.filter((c) => c.is_active).length;
  const inactiveCount = challenges.length - activeCount;

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">{t("title")}</h1>
        <div style={{ fontSize: "0.8125rem", color: "var(--g-text-muted)" }}>
          {t("summaryLine", { active: activeCount, inactive: inactiveCount, total: challenges.length })}
        </div>
      </div>

      <div className="filter-bar">
        <FilterPills
          size="sm"
          groups={[
            {
              options: ["all", "active", "inactive"],
              value: filter,
              onChange: (v) => setFilter(v as "all" | "active" | "inactive"),
              label: filterLabel,
            },
          ]}
        />
        <input
          className="g-input"
          placeholder={t("searchPlaceholder")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ marginLeft: "auto", maxWidth: "240px" }}
        />
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={filtered}
        empty={<div className="text-muted text-sm mt-4">{t("noChallengesFound")}</div>}
      >
        {(filtered) => (
          <table className="g-table">
            <thead>
              <tr>
                <th>{tCommon("colTitle")}</th>
                <th>{tCommon("colCategory")}</th>
                <th>{t("colDifficulty")}</th>
                <th>{tCommon("colType")}</th>
                <th style={{ textAlign: "right" }}>{tCommon("colPoints")}</th>
                <th style={{ textAlign: "right" }}>{tCommon("colSolves")}</th>
                <th>{tCommon("colStatus")}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((ch) => (
                <ChallengeRow key={ch.slug} ch={ch} />
              ))}
            </tbody>
          </table>
        )}
      </AsyncContent>
    </div>
  );
}
