"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { ChevronRight, Globe, Link2, Lock } from "lucide-react";
import {
  type CtfEvent, type EventStatus, type EventVisibility,
} from "@/lib/api/events";
import { EVENT_STATUS_COLORS } from "@/lib/utils/status";
import { formatDateTime } from "@/lib/utils/date";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { Button } from "@/components/ui/Button";

const STATUS_ORDER: EventStatus[] = ["draft", "published", "running", "ended", "archived"];

function nextStatus(s: EventStatus): EventStatus | null {
  const i = STATUS_ORDER.indexOf(s);
  return i < STATUS_ORDER.length - 1 ? STATUS_ORDER[i + 1] : null;
}

function visIcon(v: EventVisibility) {
  return v === "public" ? <Globe size={11} /> : v === "private" ? <Lock size={11} /> : <Link2 size={11} />;
}

interface EventsTableProps {
  events: CtfEvent[];
  isLoading: boolean;
  mapSlug: string | null;
  onToggleMap: (slug: string) => void;
  onEdit: (ev: CtfEvent) => void;
  transitionMutation: {
    mutate: (args: { slug: string; status: EventStatus }) => void;
    isPending: boolean;
  };
  confirm: (opts: {
    title: string;
    body?: string;
    confirmLabel?: string;
    dangerous?: boolean;
    onConfirm: () => void;
  }) => void;
}

export function EventsTable({
  events, isLoading, mapSlug, onToggleMap, onEdit, transitionMutation, confirm,
}: EventsTableProps) {
  return (
    <AsyncContent
      isLoading={isLoading}
      data={events}
      empty={
        <div className="g-card" style={{ textAlign: "center", padding: "2rem", color: "var(--g-text-muted)" }}>
          No events yet. Create one to get started.
        </div>
      }
    >
      {(events) => (
        <div className="g-card" style={{ padding: 0, overflow: "hidden" }}>
          <table className="g-table">
            <thead>
              <tr>
                <th>Event</th>
                <th>Status</th>
                <th>Visibility</th>
                <th>Scoring</th>
                <th>Start / End</th>
                <th>Challenges</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {events.map((ev) => {
                const next = nextStatus(ev.status);
                return (
                  <tr key={ev.id}>
                    <td>
                      <div style={{ fontWeight: 600, fontSize: "0.8125rem" }}>{ev.title}</div>
                      <div style={{ fontSize: "0.6875rem", color: "var(--g-text-muted)", fontFamily: "monospace" }}>{ev.slug}</div>
                    </td>
                    <td>
                      <span style={{
                        fontSize: "0.6875rem", fontWeight: 700, fontFamily: "monospace",
                        textTransform: "uppercase", color: EVENT_STATUS_COLORS[ev.status],
                      }}>
                        {ev.status}
                      </span>
                    </td>
                    <td>
                      <span style={{ display: "flex", alignItems: "center", gap: 4, fontSize: "0.75rem", color: "var(--g-text-muted)" }}>
                        {visIcon(ev.visibility)}
                        {ev.visibility}
                      </span>
                    </td>
                    <td style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>{ev.scoring_mode}</td>
                    <td style={{ fontSize: "0.6875rem", color: "var(--g-text-muted)" }}>
                      {formatDateTime(ev.start_at)}
                      {" / "}
                      {formatDateTime(ev.end_at)}
                    </td>
                    <td>
                      <Button
                        size="sm"
                        onClick={() => onToggleMap(ev.slug)}
                        rightIcon={
                          <ChevronRight
                            size={12}
                            style={{
                              transform: mapSlug === ev.slug ? "rotate(90deg)" : "none",
                              transition: "transform 0.15s",
                            }}
                          />
                        }
                      >
                        Challenges
                      </Button>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: 6 }}>
                        {next && (
                          <Button
                            size="sm"
                            disabled={transitionMutation.isPending}
                            onClick={() => confirm({
                              title: `Set status to "${next}"?`,
                              body: `This will move "${ev.title}" from ${ev.status} to ${next}.`,
                              confirmLabel: "Confirm",
                              onConfirm: () => transitionMutation.mutate({ slug: ev.slug, status: next }),
                            })}
                          >
                            → {next}
                          </Button>
                        )}
                        <Button size="sm" onClick={() => onEdit(ev)}>
                          Edit
                        </Button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </AsyncContent>
  );
}
