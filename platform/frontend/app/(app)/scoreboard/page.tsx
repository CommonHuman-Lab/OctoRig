"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./scoreboard.css";

import { useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Trophy, Snowflake } from "lucide-react";
import { getGlobalScoreboard } from "@/lib/api/challenges";
import { getEventScoreboard, getEvents } from "@/lib/api/events";
import { getRanks } from "@/lib/api/ranks";
import { useUserStore } from "@/stores/user.store";
import { ScoreRow } from "@/components/scoreboard/ScoreRow";
import { ScoreboardFilters, SCOREBOARD_LIMITS } from "@/components/scoreboard/ScoreboardFilters";
import { AsyncContent } from "@/components/ui/AsyncContent";

export default function ScoreboardPage() {
  const { user } = useUserStore();
  const [limit, setLimit] = useState(50);
  const [eventSlug, setEventSlug] = useState("");
  const myRowRef = useRef<HTMLTableRowElement>(null);

  const { data: events = [] } = useQuery({
    queryKey: ["events"],
    queryFn: () => getEvents(),
  });

  const { data: ranks = [] } = useQuery({
    queryKey: ["ranks"],
    queryFn: getRanks,
    staleTime: 60_000,
  });

  const isGlobal = eventSlug === "";

  const { data: entries = [], isLoading } = useQuery({
    queryKey: ["scoreboard", isGlobal ? "global" : eventSlug, limit],
    queryFn: () =>
      isGlobal
        ? getGlobalScoreboard(limit)
        : getEventScoreboard(eventSlug, limit),
  });

  function scrollToMe() {
    myRowRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  const myEntry = user ? entries.find((e) => e.username === user.username) : null;
  const isFrozen = isGlobal && entries.length > 0 && entries[0].frozen === true;

  return (
    <div className="page">
      <div className="sb-header">
        <div>
          <h1 className="page-title font-mono">
            <Trophy size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
            Scoreboard
          </h1>
          {!isLoading && (
            <p className="page-sub" style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              {entries.length} players ranked
              {isFrozen && (
                <span style={{
                  display: "inline-flex", alignItems: "center", gap: "0.25rem",
                  fontSize: "0.6875rem", color: "var(--g-accent)",
                  background: "color-mix(in srgb, var(--g-accent) 12%, transparent)",
                  border: "1px solid color-mix(in srgb, var(--g-accent) 30%, transparent)",
                  borderRadius: "4px", padding: "0.1rem 0.4rem",
                }}>
                  <Snowflake size={10} />
                  Scoreboard frozen
                </span>
              )}
            </p>
          )}
        </div>

        <ScoreboardFilters
          events={events}
          eventSlug={eventSlug}
          limit={limit}
          myEntry={myEntry}
          onEventChange={setEventSlug}
          onLimitChange={setLimit}
          onScrollToMe={scrollToMe}
        />
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={entries}
        empty={<div className="sb-empty">No scores yet.</div>}
      >
        {(entries) => (
          <div className="sb-table-wrap g-card" style={{ padding: 0, overflow: "hidden" }}>
            <table className="sb-table">
              <thead>
                <tr>
                  <th style={{ textAlign: "right" }}>#</th>
                  <th>Player</th>
                  <th>Rank</th>
                  <th>Points</th>
                  <th>Solves</th>
                  <th>Badges</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry) => {
                  const isMe = !!user && entry.username === user.username;
                  return (
                    <ScoreRow
                      key={entry.user_id ?? entry.team_id}
                      entry={entry}
                      ranks={ranks}
                      isMe={isMe}
                      rowRef={isMe ? myRowRef : undefined}
                    />
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </AsyncContent>
    </div>
  );
}
