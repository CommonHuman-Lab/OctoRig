"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Calendar, Save } from "lucide-react";
import {
  type CtfEvent, type EventVisibility, type EventScoringMode,
} from "@/lib/api/events";
import { MarkdownEditor } from "@/components/ui/MarkdownEditor";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";

export interface SheetState {
  open: boolean;
  editing: CtfEvent | null;
}

export const BLANK_FORM = {
  slug: "", title: "", description: "",
  start_at: "", end_at: "", freeze_scoreboard_at: "",
  visibility: "private" as EventVisibility,
  scoring_mode: "static" as EventScoringMode,
  max_team_size: "",
};

export type EventForm = typeof BLANK_FORM;

export function toLocalInput(val: string | null | undefined): string {
  if (!val) return "";
  try { return new Date(val).toISOString().slice(0, 16); } catch { return ""; }
}

export function toISOOrNull(val: string): string | null {
  if (!val) return null;
  try { return new Date(val).toISOString(); } catch { return null; }
}

function slugify(s: string) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

interface EventFormSheetProps {
  sheet: SheetState;
  form: EventForm;
  onChange: (update: Partial<EventForm>) => void;
  onClose: () => void;
  saveMutation: { mutate: () => void; isPending: boolean };
}

export function EventFormSheet({ sheet, form, onChange, onClose, saveMutation }: EventFormSheetProps) {
  useEscapeKey(onClose, sheet.open);

  if (!sheet.open) return null;

  return (
    <SheetShell
      title={sheet.editing ? "Edit Event" : "New Event"}
      onClose={onClose}
      footer={
        <>
          <button className="g-btn g-btn-ghost" onClick={onClose}>Cancel</button>
          <button
            className="g-btn g-btn-primary"
            disabled={!form.title || (!sheet.editing && !form.slug) || saveMutation.isPending}
            onClick={() => saveMutation.mutate()}
          >
            <Save size={13} />
            {saveMutation.isPending ? "Saving…" : sheet.editing ? "Save Changes" : "Create Event"}
          </button>
        </>
      }
    >
          <label className="ev-field">
            <span className="ev-label">Title</span>
            <input
              className="g-input"
              value={form.title}
              onChange={(e) => onChange({
                title: e.target.value,
                slug: sheet.editing ? form.slug : slugify(e.target.value),
              })}
            />
          </label>

          {!sheet.editing && (
            <label className="ev-field">
              <span className="ev-label">Slug</span>
              <input
                className="g-input"
                value={form.slug}
                onChange={(e) => onChange({ slug: slugify(e.target.value) })}
              />
            </label>
          )}

          <div className="ev-field">
            <span className="ev-label">Description</span>
            <MarkdownEditor
              value={form.description}
              onChange={(v) => onChange({ description: v })}
              placeholder="Event description (markdown supported)…"
              minHeight={120}
            />
          </div>

          <div className="ev-field-row">
            <label className="ev-field">
              <span className="ev-label">
                <Calendar size={11} style={{ display: "inline", marginRight: 4 }} />Start
              </span>
              <input
                type="datetime-local"
                className="g-input"
                value={form.start_at}
                onChange={(e) => onChange({ start_at: e.target.value })}
              />
            </label>
            <label className="ev-field">
              <span className="ev-label">
                <Calendar size={11} style={{ display: "inline", marginRight: 4 }} />End
              </span>
              <input
                type="datetime-local"
                className="g-input"
                value={form.end_at}
                onChange={(e) => onChange({ end_at: e.target.value })}
              />
            </label>
          </div>

          <label className="ev-field">
            <span className="ev-label">Freeze Scoreboard At</span>
            <input
              type="datetime-local"
              className="g-input"
              value={form.freeze_scoreboard_at}
              onChange={(e) => onChange({ freeze_scoreboard_at: e.target.value })}
            />
          </label>

          <div className="ev-field-row">
            <label className="ev-field">
              <span className="ev-label">Visibility</span>
              <select
                className="g-input"
                value={form.visibility}
                onChange={(e) => onChange({ visibility: e.target.value as EventVisibility })}
              >
                <option value="private">Private</option>
                <option value="unlisted">Unlisted</option>
                <option value="public">Public</option>
              </select>
            </label>
            <label className="ev-field">
              <span className="ev-label">Scoring Mode</span>
              <select
                className="g-input"
                value={form.scoring_mode}
                onChange={(e) => onChange({ scoring_mode: e.target.value as EventScoringMode })}
              >
                <option value="static">Static</option>
                <option value="dynamic">Dynamic</option>
              </select>
            </label>
          </div>

          <label className="ev-field">
            <span className="ev-label">Max Team Size</span>
            <input
              type="number"
              className="g-input"
              min={1}
              placeholder="Unlimited"
              value={form.max_team_size}
              onChange={(e) => onChange({ max_team_size: e.target.value })}
            />
          </label>
    </SheetShell>
  );
}
