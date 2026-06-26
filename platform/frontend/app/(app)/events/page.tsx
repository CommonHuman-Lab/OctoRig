"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./events.css";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
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
import { Button } from "@/components/ui/Button";

const STATUS_TAB_IDS: (EventStatus | undefined)[] = [undefined, "published", "running", "ended"];
const STATUS_TAB_KEY: Record<string, string> = {
  published: "statusUpcoming", running: "statusLive", ended: "statusPast",
};
const EVENT_STATUS_KEY: Record<string, string> = {
  draft: "statusDraft", published: "statusUpcoming", ended: "statusPast",
};
const SCORING_MODE_KEY: Record<string, string> = {
  static: "scoringStatic", dynamic: "scoringDynamic",
};

const VIS_ICON: Record<string, React.ReactNode> = {
  public:   <Globe size={10} />,
  private:  <Lock size={10} />,
  unlisted: <Eye size={10} />,
};

function CountdownBadge({ end_at, t }: { end_at: string | null; t: ReturnType<typeof useTranslations> }) {
  if (!end_at) return null;
  const ms = new Date(end_at).getTime() - Date.now();
  if (ms <= 0) return <span className="ev-ended-label">{t("ended")}</span>;
  const h = Math.floor(ms / 3_600_000);
  const m = Math.floor((ms % 3_600_000) / 60_000);
  return (
    <span className="ev-countdown">
      <Clock size={10} />
      {h > 0 ? t("remainingHM", { hours: h, minutes: m }) : t("remainingM", { minutes: m })}
    </span>
  );
}

function EventCard({ ev }: { ev: CtfEvent }) {
  const t = useTranslations("events");
  const isLive = ev.status === "running";
  return (
    <Link href={`/events/${ev.slug}`} className={`ev-card g-card ${isLive ? "ev-card--live" : ""}`}>
      <div className="ev-card-header">
        <span className="ev-vis">{VIS_ICON[ev.visibility]}</span>
        <span className="ev-status" style={{ color: EVENT_STATUS_COLORS[ev.status] }}>
          {isLive ? t("liveLabel") : t(EVENT_STATUS_KEY[ev.status] as any)}
        </span>
        {isLive && <CountdownBadge end_at={ev.end_at} t={t} />}
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
            {t("maxPerTeam", { count: ev.max_team_size })}
          </span>
        )}
        <span className="ev-meta-item">
          <Trophy size={11} />
          {t(SCORING_MODE_KEY[ev.scoring_mode] as any)}
        </span>
      </div>
    </Link>
  );
}

export default function EventsPage() {
  const t = useTranslations("events");
  const tc = useTranslations("common");
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
    successMessage: (data) => t("createdToast", { title: data.title }),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("createFailed"),
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
          {t("title")}
        </h1>
        {isAdmin && (
          <Button
            variant="primary"
            style={{ marginLeft: "auto" }}
            onClick={openCreate}
            leftIcon={<Plus size={13} />}
          >
            {t("newEvent")}
          </Button>
        )}
      </div>

      <div className="filter-bar">
        <FilterPills
          groups={[
            {
              options: STATUS_TAB_IDS,
              value: statusFilter,
              onChange: (v) => setStatusFilter(v as EventStatus | undefined),
              label: (v) => v ? t(STATUS_TAB_KEY[v] as any) : tc("all"),
            },
          ]}
        />
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={events}
        empty={
          <div className="text-muted text-sm" style={{ marginTop: "1.5rem" }}>
            {t("noEvents")}{isAdmin && t("noEventsAdminHint")}
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
