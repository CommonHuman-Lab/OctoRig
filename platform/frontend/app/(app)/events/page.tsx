"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./events.css";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Calendar, Clock, Trophy, Users, Lock, Globe, Eye, Plus, Flag } from "lucide-react";
import {
  getEvents,
  createEvent,
  type CtfEvent,
  type EventStatus,
  type CreateEventPayload,
} from "@/lib/api/events";
import { useUserStore } from "@/stores/user.store";
import { formatDateTime } from "@/lib/utils/date";
import { EVENT_STATUS_COLORS } from "@/lib/utils/status";
import {
  EventFormSheet, BLANK_FORM, toISOOrNull,
  type SheetState, type EventForm,
} from "@/components/admin/events/EventFormSheet";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { FilterPills } from "@/components/ui/FilterPills";

const STATUS_TABS: { id: EventStatus | undefined; label: string }[] = [
  { id: undefined, label: "All" },
  { id: "published", label: "Upcoming" },
  { id: "running", label: "Live" },
  { id: "ended", label: "Past" },
];

const VIS_ICON: Record<string, React.ReactNode> = {
  public:   <Globe size={10} />,
  private:  <Lock size={10} />,
  unlisted: <Eye size={10} />,
};

function CountdownBadge({ end_at }: { end_at: string | null }) {
  if (!end_at) return null;
  const ms = new Date(end_at).getTime() - Date.now();
  if (ms <= 0) return <span className="ev-ended-label">Ended</span>;
  const h = Math.floor(ms / 3_600_000);
  const m = Math.floor((ms % 3_600_000) / 60_000);
  return (
    <span className="ev-countdown">
      <Clock size={10} />
      {h > 0 ? `${h}h ${m}m remaining` : `${m}m remaining`}
    </span>
  );
}

function EventCard({ ev }: { ev: CtfEvent }) {
  const isLive = ev.status === "running";
  return (
    <Link href={`/events/${ev.slug}`} className={`ev-card g-card ${isLive ? "ev-card--live" : ""}`}>
      <div className="ev-card-header">
        <span className="ev-vis">{VIS_ICON[ev.visibility]}</span>
        <span className="ev-status" style={{ color: EVENT_STATUS_COLORS[ev.status] }}>
          {isLive ? "● LIVE" : ev.status}
        </span>
        {isLive && <CountdownBadge end_at={ev.end_at} />}
      </div>
      <h3 className="ev-title">{ev.title}</h3>
      {ev.description && <p className="ev-desc">{ev.description}</p>}
      <div className="ev-meta">
        <span className="ev-meta-item">
          <Calendar size={11} />
          {formatDateTime(ev.start_at)}
        </span>
        {ev.max_team_size && (
          <span className="ev-meta-item">
            <Users size={11} />
            Max {ev.max_team_size}/team
          </span>
        )}
        <span className="ev-meta-item">
          <Trophy size={11} />
          {ev.scoring_mode}
        </span>
      </div>
    </Link>
  );
}

export default function EventsPage() {
  const [statusFilter, setStatusFilter] = useState<EventStatus | undefined>(undefined);
  const [sheet, setSheet] = useState<SheetState>({ open: false, editing: null });
  const [form, setForm] = useState<EventForm>(BLANK_FORM);
  const { user } = useUserStore();
  const isAdmin = user?.permissions?.includes("admin.panel") ?? false;

  const { data: events = [], isLoading } = useQuery({
    queryKey: ["events", statusFilter],
    queryFn: () => getEvents(statusFilter),
  });

  const saveMutation = useApiMutation<CtfEvent, void>({
    mutationFn: () => {
      const payload: CreateEventPayload = {
        slug: form.slug,
        title: form.title,
        description: form.description || undefined,
        start_at: toISOOrNull(form.start_at) ?? undefined,
        end_at: toISOOrNull(form.end_at) ?? undefined,
        visibility: form.visibility,
        scoring_mode: form.scoring_mode,
        max_team_size: form.max_team_size ? Number(form.max_team_size) : undefined,
      };
      return createEvent(payload);
    },
    invalidateKeys: [["events"]],
    successMessage: (data) => `Event "${data.title}" created as draft`,
    errorMessage: (err: any) => err?.response?.data?.detail ?? "Failed to create event",
    onSuccess: () => setSheet({ open: false, editing: null }),
  });

  function openCreate() {
    setForm(BLANK_FORM);
    setSheet({ open: true, editing: null });
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">
          <Flag size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
          CTF Events
        </h1>
        {isAdmin && (
          <button
            className="g-btn g-btn-primary"
            style={{ marginLeft: "auto" }}
            onClick={openCreate}
          >
            <Plus size={13} />
            New Event
          </button>
        )}
      </div>

      <div className="filter-bar">
        <FilterPills
          groups={[
            {
              options: STATUS_TABS.map((t) => t.id),
              value: statusFilter,
              onChange: (v) => setStatusFilter(v as EventStatus | undefined),
              label: (v) => STATUS_TABS.find((t) => t.id === v)?.label ?? "All",
            },
          ]}
        />
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={events}
        empty={
          <div className="text-muted text-sm" style={{ marginTop: "1.5rem" }}>
            No events found.{isAdmin && " Click “New Event” to create one."}
          </div>
        }
      >
        {(events) => (
          <div className="g-grid-auto ev-grid" style={{ marginTop: "1rem" }}>
            {events.map((ev) => (
              <EventCard key={ev.id} ev={ev} />
            ))}
          </div>
        )}
      </AsyncContent>

      <EventFormSheet
        sheet={sheet}
        form={form}
        onChange={(update) => setForm((f) => ({ ...f, ...update }))}
        onClose={() => setSheet({ open: false, editing: null })}
        saveMutation={saveMutation}
      />
    </div>
  );
}
