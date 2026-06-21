"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../events.css";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft, Trophy, Clock, Users, Snowflake, CheckCircle2, Target,
} from "lucide-react";
import {
  getEvent, getEventChallenges, getEventScoreboard, type EventChallenge,
} from "@/lib/api/events";
import { formatDateTime } from "@/lib/utils/date";
import { DIFF_COLOR } from "@/lib/utils/difficulty";
import { Button } from "@/components/ui/Button";

function ChallengeGrid({ challenges }: { challenges: EventChallenge[] }) {
  const byCategory = challenges.reduce<Record<string, EventChallenge[]>>((acc, ch) => {
    (acc[ch.category] ??= []).push(ch);
    return acc;
  }, {});

  return (
    <div className="ch-sections">
      {Object.entries(byCategory).map(([cat, chs]) => (
        <div key={cat}>
          <h3 className="cat-title">{cat.replace(/-/g, " ")}</h3>
          <div className="ch-grid">
            {chs.map((ch) => (
              <Link
                key={ch.id}
                href={`/challenges/${ch.slug}`}
                className={`ev-ch-card ${ch.solved_by_me ? "ev-ch-card--solved" : ""}`}
              >
                <div className="ev-ch-top">
                  <span className="ev-ch-title">{ch.title}</span>
                  {ch.solved_by_me && <CheckCircle2 size={12} style={{ color: "var(--g-success)" }} />}
                </div>
                <div className="ev-ch-footer">
                  <span className="ev-ch-pts">{ch.points} pts</span>
                  <span className="ev-ch-diff" style={{ color: DIFF_COLOR[ch.difficulty] }}>
                    {ch.difficulty}
                  </span>
                  <span className="ev-ch-solves">
                    <Target size={10} />
                    {ch.solve_count}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function Scoreboard({ slug }: { slug: string }) {
  const { data: rows = [], isLoading } = useQuery({
    queryKey: ["event-scoreboard", slug],
    queryFn: () => getEventScoreboard(slug, 50),
  });

  if (isLoading) return <div className="text-muted text-sm">Loading scoreboard…</div>;
  if (rows.length === 0) return <div className="text-muted text-sm">No scores yet.</div>;

  return (
    <div className="sb-table">
      <div className="sb-head">
        <span>#</span>
        <span>Team</span>
        <span className="sb-right">Score</span>
      </div>
      {rows.map((r) => (
        <div key={r.rank} className={`sb-row ${r.rank <= 3 ? `sb-top${r.rank}` : ""}`}>
          <span className="sb-rank">{r.rank}</span>
          <span className="sb-name">Team {r.team_id ?? r.user_id}</span>
          <span className="sb-score">{r.total}</span>
        </div>
      ))}
    </div>
  );
}

export default function EventDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [tab, setTab] = useState<"challenges" | "scoreboard">("challenges");

  const { data: ev, isLoading: evLoading } = useQuery({
    queryKey: ["event", slug],
    queryFn: () => getEvent(slug),
  });

  const { data: challenges = [], isLoading: chLoading } = useQuery({
    queryKey: ["event-challenges", slug],
    queryFn: () => getEventChallenges(slug),
    enabled: tab === "challenges",
  });

  if (evLoading) return <div className="page text-muted text-sm">Loading event…</div>;
  if (!ev) return <div className="page text-muted text-sm">Event not found.</div>;

  const isLive = ev.status === "running";
  const solved = challenges.filter((c) => c.solved_by_me).length;

  return (
    <div className="page">
      <Link href="/events" className="back-link">
        <ArrowLeft size={14} />
        <span>Events</span>
      </Link>

      {/* Header */}
      <div className="ev-header">
        <div className="ev-header-top">
          <span className={`ev-status-badge ${isLive ? "ev-status-live" : ""}`}>
            {isLive ? "● LIVE" : ev.status.toUpperCase()}
          </span>
          {ev.scoreboard_frozen && (
            <span className="ev-frozen">
              <Snowflake size={11} />
              Scoreboard frozen
            </span>
          )}
        </div>
        <h1 className="ev-title">{ev.title}</h1>
        {ev.description && <p className="ev-desc">{ev.description}</p>}

        <div className="ev-stats">
          {ev.start_at && (
            <span className="ev-stat">
              <Clock size={12} />
              {formatDateTime(ev.start_at)} → {formatDateTime(ev.end_at)}
            </span>
          )}
          {ev.max_team_size && (
            <span className="ev-stat">
              <Users size={12} />
              Max {ev.max_team_size} per team
            </span>
          )}
          <span className="ev-stat">
            <Trophy size={12} />
            {ev.scoring_mode} scoring
          </span>
          {tab === "challenges" && challenges.length > 0 && (
            <span className="ev-stat">
              <CheckCircle2 size={12} />
              {solved}/{challenges.length} solved
            </span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <Button variant="tab" active={tab === "challenges"} onClick={() => setTab("challenges")}>
          Challenges {challenges.length > 0 && `(${challenges.length})`}
        </Button>
        <Button variant="tab" active={tab === "scoreboard"} onClick={() => setTab("scoreboard")}>
          Scoreboard
        </Button>
      </div>

      <div className="tab-content">
        {tab === "challenges" && (
          chLoading
            ? <div className="text-muted text-sm">Loading challenges…</div>
            : challenges.length === 0
              ? <div className="text-muted text-sm">No challenges released yet.</div>
              : <ChallengeGrid challenges={challenges} />
        )}
        {tab === "scoreboard" && <Scoreboard slug={slug} />}
      </div>
    </div>
  );
}
