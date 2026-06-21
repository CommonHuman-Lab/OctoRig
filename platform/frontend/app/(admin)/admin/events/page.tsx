"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../admin.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Plus } from "lucide-react";
import {
  getEvents, createEvent, updateEvent, transitionEvent,
  addEventChallenge, removeEventChallenge,
  type CtfEvent, type EventStatus,
  type CreateEventPayload, type UpdateEventPayload,
} from "@/lib/api/events";
import { getChallenges } from "@/lib/api/challenges";
import { useConfirmStore } from "@/stores/confirm.store";
import { useUserStore } from "@/stores/user.store";
import { useAdminGuard } from "@/hooks/useAdminGuard";
import {
  EventFormSheet, BLANK_FORM, toLocalInput, toISOOrNull,
  type SheetState, type EventForm,
} from "@/components/admin/events/EventFormSheet";
import { EventsTable } from "@/components/admin/events/EventsTable";
import { ChallengeMappingPanel } from "@/components/admin/events/ChallengeMappingPanel";

export default function AdminEventsPage() {
  const { confirm } = useConfirmStore();
  const { user } = useUserStore();

  useAdminGuard();

  const { data: events = [], isLoading } = useQuery({
    queryKey: ["admin-events"],
    queryFn: () => getEvents(),
    enabled: !!user?.permissions?.includes("admin.panel"),
  });

  const [sheet, setSheet] = useState<SheetState>({ open: false, editing: null });
  const [form, setForm] = useState<EventForm>(BLANK_FORM);
  const [mapSlug, setMapSlug] = useState<string | null>(null);
  const [challSearch, setChallSearch] = useState("");

  const mapEvent = mapSlug ? events.find((e) => e.slug === mapSlug) ?? null : null;

  const { data: eventChallenges = [] } = useQuery({
    queryKey: ["event-challenges", mapSlug],
    queryFn: () => import("@/lib/api/events").then((m) => m.getEventChallenges(mapSlug!)),
    enabled: !!mapSlug,
  });

  const { data: allChallenges = [] } = useQuery({
    queryKey: ["challenges-all"],
    queryFn: () => getChallenges(),
    staleTime: 60_000,
  });

  function openCreate() {
    setForm(BLANK_FORM);
    setSheet({ open: true, editing: null });
  }

  function openEdit(ev: CtfEvent) {
    setForm({
      slug: ev.slug,
      title: ev.title,
      description: ev.description ?? "",
      start_at: toLocalInput(ev.start_at),
      end_at: toLocalInput(ev.end_at),
      freeze_scoreboard_at: toLocalInput(ev.freeze_scoreboard_at),
      visibility: ev.visibility,
      scoring_mode: ev.scoring_mode,
      max_team_size: ev.max_team_size?.toString() ?? "",
    });
    setSheet({ open: true, editing: ev });
  }

  const saveMutation = useApiMutation<CtfEvent, void>({
    mutationFn: async () => {
      const payload = {
        title: form.title,
        description: form.description || null,
        start_at: toISOOrNull(form.start_at),
        end_at: toISOOrNull(form.end_at),
        freeze_scoreboard_at: toISOOrNull(form.freeze_scoreboard_at),
        visibility: form.visibility,
        scoring_mode: form.scoring_mode,
        max_team_size: form.max_team_size ? parseInt(form.max_team_size) : null,
      };
      if (sheet.editing) {
        return updateEvent(sheet.editing.slug, payload as UpdateEventPayload);
      } else {
        return createEvent({ slug: form.slug, ...payload } as CreateEventPayload);
      }
    },
    invalidateKeys: [["admin-events"]],
    successMessage: () => (sheet.editing ? "Event updated" : "Event created"),
    errorMessage: "Failed to save event",
    onSuccess: () => setSheet({ open: false, editing: null }),
  });

  const transitionMutation = useApiMutation({
    mutationFn: ({ slug, status }: { slug: string; status: EventStatus }) =>
      transitionEvent(slug, status),
    invalidateKeys: [["admin-events"]],
    successMessage: "Status updated",
    errorMessage: "Failed to update status",
  });

  const addChallMutation = useApiMutation({
    mutationFn: (challengeId: number) => addEventChallenge(mapSlug!, challengeId),
    invalidateKeys: [["event-challenges", mapSlug]],
    errorMessage: "Failed to add challenge",
  });

  const removeChallMutation = useApiMutation({
    mutationFn: (challengeId: number) => removeEventChallenge(mapSlug!, challengeId),
    invalidateKeys: [["event-challenges", mapSlug]],
    errorMessage: "Failed to remove challenge",
  });

  const mappedIds = new Set(eventChallenges.map((c) => c.id));
  const filteredAll = allChallenges.filter((c) =>
    !mappedIds.has(c.id) &&
    (challSearch === "" || c.title.toLowerCase().includes(challSearch.toLowerCase()))
  );

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Events</h1>
        <button className="g-btn g-btn-primary g-btn-sm" onClick={openCreate}>
          <Plus size={13} />
          New Event
        </button>
      </div>

      <EventsTable
        events={events}
        isLoading={isLoading}
        mapSlug={mapSlug}
        onToggleMap={(slug) => setMapSlug(mapSlug === slug ? null : slug)}
        onEdit={openEdit}
        transitionMutation={transitionMutation}
        confirm={confirm}
      />

      {mapSlug && mapEvent && (
        <ChallengeMappingPanel
          mapEvent={mapEvent}
          eventChallenges={eventChallenges}
          filteredAll={filteredAll}
          challSearch={challSearch}
          onChallSearch={setChallSearch}
          onClose={() => setMapSlug(null)}
          addChallMutation={addChallMutation}
          removeChallMutation={removeChallMutation}
        />
      )}

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
