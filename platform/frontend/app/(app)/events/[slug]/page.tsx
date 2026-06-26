"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../events.css";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import {
  ArrowLeft, Trophy, Clock, Users, Snowflake, CheckCircle2, Target,
} from "lucide-react";
import {
  getEvent, getEventChallenges, getEventScoreboard, type EventChallenge,
} from "@/lib/api/events";
import { formatDateTime } from "@/lib/utils/date";
import { DIFF_COLOR } from "@/lib/utils/difficulty";
import { Button } from "@/components/ui/Button";

const EVENT_STATUS_KEY: Record<string, string> = {
  draft: "statusDraft", published: "statusUpcoming", ended: "statusPast",
};
const SCORING_MODE_KEY: Record<string, string> = {
  static: "scoringStatic", dynamic: "scoringDynamic",
};

function ChallengeTile({ ch }: { ch: EventChallenge }) {
  const tc = useTranslations("common");
  return (
    <Link
      href={`/challenges/${ch.slug}`}
      className={`ev-ch-card ${ch.solved_by_me ? "ev-ch-card--solved" : ""}`}
    >
      <div className="ev-ch-top">
        <span className="ev-ch-title">{ch.title}</span>
        {ch.solved_by_me && <CheckCircle2 size={12} style={{ color: "var(--g-success)" }} />}
      </div>
      <div className="ev-ch-footer">
        <span className="ev-ch-pts">{tc("points", { count: ch.points })}</span>
        <span className="ev-ch-diff" style={{ color: DIFF_COLOR[ch.difficulty] }}>
          {tc(ch.difficulty)}
        </span>
        <span className="ev-ch-solves">
          <Target size={10} />
          {ch.solve_count}
        </span>
      </div>
    </Link>
  );
}

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
              <ChallengeTile key={ch.id} ch={ch} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function Scoreboard({ slug }: { slug: string }) {
  const t = useTranslations("events");
  const ts = useTranslations("scoreboard");
  const tc = useTranslations("common");
  const { data: rows = [], isLoading } = useQuery({
    queryKey: ["event-scoreboard", slug],
    queryFn: () => getEventScoreboard(slug, 50),
  });

  if (isLoading) return <div className="text-muted text-sm">{t("loadingScoreboard")}</div>;
  if (rows.length === 0) return <div className="text-muted text-sm">{ts("noScores")}</div>;

  return (
    <div className="sb-table">
      <div className="sb-head">
        <span>#</span>
        <span>{tc("colTeam")}</span>
        <span className="sb-right">{tc("colScore")}</span>
      </div>
      {rows.map((r) => (
        <div key={r.rank} className={`sb-row ${r.rank <= 3 ? `sb-top${r.rank}` : ""}`}>
          <span className="sb-rank">{r.rank}</span>
          <span className="sb-name">{t("teamLabel", { id: r.team_id ?? r.user_id ?? "" })}</span>
          <span className="sb-score">{r.total}</span>
        </div>
      ))}
    </div>
  );
}

export default function EventDetailPage() {
  const t = useTranslations("events");
  const tn = useTranslations("nav");
  const tch = useTranslations("challenges");
  const tsb = useTranslations("scoreboard");
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

  if (evLoading) return <div className="page text-muted text-sm">{t("loadingEvent")}</div>;
  if (!ev) return <div className="page text-muted text-sm">{t("notFound")}</div>;

  const isLive = ev.status === "running";
  const solved = challenges.filter((c) => c.solved_by_me).length;

  return (
    <div className="page">
      <Link href="/events" className="back-link">
        <ArrowLeft size={14} />
        <span>{tn("events")}</span>
      </Link>

      {/* Header */}
      <div className="ev-header">
        <div className="ev-header-top">
          <span className={`ev-status-badge ${isLive ? "ev-status-live" : ""}`}>
            {isLive ? t("liveLabel") : t(EVENT_STATUS_KEY[ev.status] as any).toUpperCase()}
          </span>
          {ev.scoreboard_frozen && (
            <span className="ev-frozen">
              <Snowflake size={11} />
              {tsb("frozen")}
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
              {t("maxPerTeamLong", { count: ev.max_team_size })}
            </span>
          )}
          <span className="ev-stat">
            <Trophy size={12} />
            {t("scoringSuffix", { mode: t(SCORING_MODE_KEY[ev.scoring_mode] as any) })}
          </span>
          {tab === "challenges" && challenges.length > 0 && (
            <span className="ev-stat">
              <CheckCircle2 size={12} />
              {tch("solved", { solved, total: challenges.length })}
            </span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <Button variant="tab" active={tab === "challenges"} onClick={() => setTab("challenges")}>
          {tn("challenges")} {challenges.length > 0 && `(${challenges.length})`}
        </Button>
        <Button variant="tab" active={tab === "scoreboard"} onClick={() => setTab("scoreboard")}>
          {tn("scoreboard")}
        </Button>
      </div>

      <div className="tab-content">
        {tab === "challenges" && (
          chLoading
            ? <div className="text-muted text-sm">{t("loadingChallenges")}</div>
            : challenges.length === 0
              ? <div className="text-muted text-sm">{t("noChallengesReleased")}</div>
              : <ChallengeGrid challenges={challenges} />
        )}
        {tab === "scoreboard" && <Scoreboard slug={slug} />}
      </div>
    </div>
  );
}
