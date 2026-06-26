"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./labs.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Search, FlaskConical } from "lucide-react";
import { getLabs } from "@/lib/api/labs";
import { stopDeployment, resetDeployment } from "@/lib/api/deployments";
import { LabCard } from "@/components/labs/LabCard";
import { PageSpinner } from "@/components/ui/Spinner";
import { FilterPills } from "@/components/ui/FilterPills";

const CATEGORY_IDS = [undefined, "world", "firerange", "thirdparty"] as const;
const CATEGORY_KEYS: Record<string, string> = {
  world: "categoryWorld", firerange: "categoryFirerange", thirdparty: "categoryThirdparty",
};

export default function LabsPage() {
  const t = useTranslations("labs");
  const tc = useTranslations("common");
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [search, setSearch] = useState("");
  const [onlyRunning, setOnlyRunning] = useState(false);
  const { data: labs = [], isLoading } = useQuery({
    queryKey: ["labs", category],
    queryFn: () => getLabs(category),
  });

  const stopMutation = useApiMutation({
    mutationFn: stopDeployment,
    invalidateKeys: [["labs"]],
    successMessage: t("stopRequested"),
    errorMessage: t("stopFailed"),
  });

  const resetMutation = useApiMutation({
    mutationFn: resetDeployment,
    invalidateKeys: [["labs"]],
    successMessage: t("resetRequested"),
    errorMessage: t("resetFailed"),
  });

  const CATEGORY_ORDER: Record<string, number> = { world: 0, firerange: 1, thirdparty: 2 };

  const filtered = labs
    .filter((l) =>
      (search === "" || l.name.toLowerCase().includes(search.toLowerCase()) || l.description.toLowerCase().includes(search.toLowerCase())) &&
      (!onlyRunning || l.current_deployment?.status === "running")
    )
    .sort((a, b) => {
      const catDiff = (CATEGORY_ORDER[a.category] ?? 9) - (CATEGORY_ORDER[b.category] ?? 9);
      if (catDiff !== 0) return catDiff;
      return a.name.localeCompare(b.name);
    });

  return (
    <div className="page">
      <h1 className="page-title font-mono">
        <FlaskConical size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
        {t("title")}
      </h1>

      {/* Filter bar */}
      <div className="filter-bar">
        <div className="g-input-icon">
          <Search size={14} className="icon-left" />
          <input
            className="g-input"
            placeholder={t("searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <FilterPills
          groups={[
            {
              options: [...CATEGORY_IDS],
              value: category,
              onChange: setCategory,
              label: (v) => v === undefined ? tc("all") : t(CATEGORY_KEYS[v] as any),
            },
          ]}
        />
        <button
          className={`filter-pill ${onlyRunning ? "active" : ""}`}
          onClick={() => setOnlyRunning((v) => !v)}
          style={{ marginLeft: "auto" }}
        >
          <span style={{
            display: "inline-block", width: 7, height: 7, borderRadius: "50%",
            background: onlyRunning ? "var(--g-success)" : "var(--g-text-muted)",
            marginRight: "0.4rem", verticalAlign: "middle",
          }} />
          {tc("running")}
        </button>
      </div>

      {isLoading ? (
        <PageSpinner />
      ) : (
        <div className="g-grid-auto labs-grid mt-4">
          {filtered.map((lab) => (
            <LabCard
              key={lab.id}
              lab={lab}
              onStop={stopMutation.mutate}
              onReset={resetMutation.mutate}
            />
          ))}
          {filtered.length === 0 && (
            <div className="text-muted text-sm">{t("noMatch")}</div>
          )}
        </div>
      )}
    </div>
  );
}
