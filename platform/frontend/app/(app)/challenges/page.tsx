"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./challenges.css";

import { useState } from "react";
import Link from "next/link";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { Search, CheckCircle2, Clock, Target, Swords } from "lucide-react";
import { getChallenges, type ChallengeListItem, type ChallengeDifficulty } from "@/lib/api/challenges";
import { getLabs, type LabTemplate } from "@/lib/api/labs";
import { PageSpinner } from "@/components/ui/Spinner";
import { FilterPills } from "@/components/ui/FilterPills";
import { Button } from "@/components/ui/Button";
import { DIFF_CLASS } from "@/lib/utils/difficulty";
import { STALE_TIME } from "@/lib/config";

const CATEGORIES = [
  { id: undefined, label: "All" },
  { id: "sqli", label: "SQLi" },
  { id: "xss", label: "XSS" },
  { id: "idor", label: "IDOR" },
  { id: "web", label: "Web" },
  { id: "recon", label: "Recon" },
  { id: "python", label: "Python" },
] as const;

const DIFFICULTIES: { id: ChallengeDifficulty | undefined; label: string }[] = [
  { id: undefined, label: "Any" },
  { id: "easy", label: "Easy" },
  { id: "medium", label: "Medium" },
  { id: "hard", label: "Hard" },
  { id: "insane", label: "Insane" },
];

const DIFF_ORDER: Record<ChallengeDifficulty, number> = {
  easy: 0, medium: 1, hard: 2, insane: 3,
};

function DiffBadge({ difficulty }: { difficulty: ChallengeDifficulty }) {
  return (
    <span className={`g-diff-badge ${DIFF_CLASS[difficulty]}`}>
      {difficulty}
    </span>
  );
}

function ChallengeCard({ ch }: { ch: ChallengeListItem }) {
  return (
    <Link href={`/challenges/${ch.slug}`} className="ch-card g-card">
      <div className="ch-card-header">
        <span className="ch-category">{ch.category.replace("-", " ")}</span>
        <DiffBadge difficulty={ch.difficulty} />
      </div>

      <h3 className="ch-title">{ch.title}</h3>

      {ch.lab_name && (
        <span className="ch-lab-tag">{ch.lab_name}</span>
      )}

      <div className="ch-tags">
        {ch.tags.slice(0, 3).map((t) => (
          <span key={t} className="g-badge g-badge--accent">{t}</span>
        ))}
      </div>

      <div className="ch-footer">
        <span className="ch-points">{ch.points} pts</span>
        <div className="ch-meta">
          {ch.estimated_minutes && (
            <span className="ch-meta-item">
              <Clock size={11} />
              {ch.estimated_minutes}m
            </span>
          )}
          <span className="ch-meta-item">
            <Target size={11} />
            {ch.solve_count} solves
          </span>
          {ch.solved_by_me && (
            <span className="ch-solved-badge">
              <CheckCircle2 size={11} />
              Solved
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}

export default function ChallengesPage() {
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [difficulty, setDifficulty] = useState<ChallengeDifficulty | undefined>(undefined);
  const [labSlug, setLabSlug] = useState<string | undefined>(undefined);
  const [solvedFilter, setSolvedFilter] = useState<"all" | "solved" | "unsolved">("all");
  const [search, setSearch] = useState("");

  const { data: challenges = [], isLoading, isFetching } = useQuery({
    queryKey: ["challenges", category, difficulty, search, labSlug],
    queryFn: () => getChallenges({
      category,
      difficulty,
      search: search || undefined,
      lab_slug: labSlug || undefined,
    }),
    placeholderData: keepPreviousData,
  });

  const { data: labs = [] } = useQuery<LabTemplate[]>({
    queryKey: ["labs"],
    queryFn: () => getLabs(),
    staleTime: STALE_TIME.MEDIUM,
  });

  const labsWithChallenges = labs.filter((l) => l.category === "world");

  const displayed = challenges
    .filter((c) => {
      if (!labSlug && c.lab_category === "firerange") return false;
      if (solvedFilter === "solved") return c.solved_by_me;
      if (solvedFilter === "unsolved") return !c.solved_by_me;
      return true;
    })
    .sort((a, b) =>
      DIFF_ORDER[a.difficulty] - DIFF_ORDER[b.difficulty] ||
      a.title.localeCompare(b.title)
    );

  const solved = challenges.filter((c) => c.solved_by_me).length;
  const total = challenges.length;

  return (
    <div className="page">
      <div className="page-header page-header--top">
        <div>
          <h1 className="page-title font-mono">
            <Swords size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
            Challenges
          </h1>
          {!isLoading && (
            <p className="page-sub">{solved}/{total} solved</p>
          )}
        </div>
      </div>

      <div className="filter-bar">
        <div className="g-input-icon">
          <Search size={14} className="icon-left" />
          <input
            className="g-input"
            placeholder="Search challenges…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <FilterPills
          groups={[
            {
              options: CATEGORIES.map((c) => c.id),
              value: category,
              onChange: (v) => setCategory(v),
              label: (v) => CATEGORIES.find((c) => c.id === v)?.label ?? "All",
            },
            {
              options: DIFFICULTIES.map((d) => d.id),
              value: difficulty,
              onChange: (v) => setDifficulty(v as ChallengeDifficulty | undefined),
              label: (v) => DIFFICULTIES.find((d) => d.id === v)?.label ?? "Any",
            },
            {
              options: ["all", "unsolved", "solved"],
              value: solvedFilter,
              onChange: (v) => setSolvedFilter(v as "all" | "unsolved" | "solved"),
            },
          ]}
        />
      </div>

      {/* Lab filters + result count + clear */}
      <div className="ch-filter-meta">
        {labsWithChallenges.length > 0 && (
          <div className="ch-lab-filters">
            <FilterPills
              size="sm"
              groups={[
                {
                  options: [undefined, ...labsWithChallenges.map((l) => l.slug)],
                  value: labSlug,
                  onChange: (v) => setLabSlug(v === labSlug ? undefined : v),
                  label: (v) => v === undefined ? "All" : labsWithChallenges.find((l) => l.slug === v)?.name ?? v,
                },
              ]}
            />
          </div>
        )}
        <div className="ch-filter-status">
          {!isLoading && (
            <span className="ch-result-count">
              {displayed.length} challenge{displayed.length !== 1 ? "s" : ""}
            </span>
          )}
          {(category || difficulty || labSlug || solvedFilter !== "all" || search) && (
            <Button
              size="sm"
              onClick={() => {
                setCategory(undefined);
                setDifficulty(undefined);
                setLabSlug(undefined);
                setSolvedFilter("all");
                setSearch("");
              }}
            >
              Clear filters
            </Button>
          )}
        </div>
      </div>

      {isLoading ? (
        <PageSpinner />
      ) : (
        <>
          <div className="g-grid-auto ch-grid" style={{ opacity: isFetching ? 0.6 : 1, transition: "opacity 0.15s" }}>
            {displayed.map((ch) => (
              <ChallengeCard key={ch.id} ch={ch} />
            ))}
          </div>
          {displayed.length === 0 && (
            <div className="text-muted text-xs mt-4">No challenges match your filter.</div>
          )}
        </>
      )}
    </div>
  );
}
