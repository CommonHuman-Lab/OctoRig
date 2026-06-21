"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../admin.css";

import { useState } from "react";
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

function ChallengeRow({ ch }: { ch: ChallengeListItem }) {
  const { mutate, isPending } = useApiMutation<{ slug: string; is_active: boolean }, void>({
    mutationFn: () => setChallengeActive(ch.slug, !ch.is_active),
    invalidateKeys: [["admin", "challenges"]],
    successMessage: (res) => `${ch.title} ${res.is_active ? "enabled" : "disabled"}.`,
    errorMessage: "Failed to update challenge.",
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
        <button
          className="g-btn g-btn-ghost g-btn-sm"
          disabled={isPending}
          onClick={() => mutate()}
          style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}
          title={ch.is_active ? "Disable challenge" : "Enable challenge"}
        >
          {ch.is_active ? (
            <ToggleRight size={16} style={{ color: "var(--g-success)" }} />
          ) : (
            <ToggleLeft size={16} style={{ color: "var(--g-text-muted)" }} />
          )}
          {isPending ? "…" : ch.is_active ? "Enabled" : "Disabled"}
        </button>
      </td>
    </tr>
  );
}

export default function AdminChallengesPage() {
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
        <h1 className="page-title font-mono">Challenge Management</h1>
        <div style={{ fontSize: "0.8125rem", color: "var(--g-text-muted)" }}>
          {activeCount} active · {inactiveCount} disabled · {challenges.length} total
        </div>
      </div>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", alignItems: "center" }}>
        {(["all", "active", "inactive"] as const).map((f) => (
          <button
            key={f}
            className={`g-btn g-btn-sm ${filter === f ? "g-btn-primary" : "g-btn-ghost"}`}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
        <input
          className="g-input"
          placeholder="Search title or category…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ marginLeft: "auto", maxWidth: "240px" }}
        />
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={filtered}
        empty={<div className="text-muted text-sm mt-4">No challenges found.</div>}
      >
        {(filtered) => (
          <table className="g-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Category</th>
                <th>Difficulty</th>
                <th>Type</th>
                <th style={{ textAlign: "right" }}>Points</th>
                <th style={{ textAlign: "right" }}>Solves</th>
                <th>Status</th>
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
