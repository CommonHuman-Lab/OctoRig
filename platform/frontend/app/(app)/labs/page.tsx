"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./labs.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Search, FlaskConical } from "lucide-react";
import { getLabs } from "@/lib/api/labs";
import { stopDeployment, resetDeployment } from "@/lib/api/deployments";
import { LabCard } from "@/components/labs/LabCard";
import { PageSpinner } from "@/components/ui/Spinner";

const CATEGORIES = [
  { id: undefined, label: "All" },
  { id: "world", label: "World" },
  { id: "firerange", label: "Fire Range" },
  { id: "thirdparty", label: "Third Party" },
] as const;

export default function LabsPage() {
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
    successMessage: "Lab stop requested",
    errorMessage: "Failed to stop lab",
  });

  const resetMutation = useApiMutation({
    mutationFn: resetDeployment,
    invalidateKeys: [["labs"]],
    successMessage: "Lab reset requested",
    errorMessage: "Failed to reset lab",
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
        Lab Catalog
      </h1>

      {/* Filter bar */}
      <div className="filter-bar">
        <div className="g-input-icon">
          <Search size={14} className="icon-left" />
          <input
            className="g-input"
            placeholder="Search labs…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-1">
          {CATEGORIES.map((c) => (
            <button
              key={String(c.id)}
              className={`g-btn ${category === c.id ? "g-btn-primary" : "g-btn-ghost"}`}
              onClick={() => setCategory(c.id)}
            >
              {c.label}
            </button>
          ))}
        </div>
        <button
          className={`g-btn ${onlyRunning ? "g-btn-primary" : "g-btn-ghost"}`}
          onClick={() => setOnlyRunning((v) => !v)}
          style={{ marginLeft: "auto" }}
        >
          <span style={{
            display: "inline-block", width: 7, height: 7, borderRadius: "50%",
            background: onlyRunning ? "var(--g-success)" : "var(--g-text-muted)",
            marginRight: "0.4rem", verticalAlign: "middle",
          }} />
          Running
        </button>
      </div>

      {isLoading ? (
        <PageSpinner />
      ) : (
        <div className="labs-grid mt-4">
          {filtered.map((lab) => (
            <LabCard
              key={lab.id}
              lab={lab}
              onStop={stopMutation.mutate}
              onReset={resetMutation.mutate}
            />
          ))}
          {filtered.length === 0 && (
            <div className="text-muted text-sm">No labs match your filter.</div>
          )}
        </div>
      )}
    </div>
  );
}
