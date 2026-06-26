"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Calendar, Save } from "lucide-react";
import { useTranslations } from "next-intl";
import {
  type CtfEvent, type EventVisibility, type EventScoringMode,
} from "@/lib/api/events";
import { MarkdownEditor } from "@/components/ui/MarkdownEditor";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";
import { Button } from "@/components/ui/Button";

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
  const t = useTranslations("events");
  const tc = useTranslations("common");
  useEscapeKey(onClose, sheet.open);

  if (!sheet.open) return null;

  return (
    <SheetShell
      title={sheet.editing ? t("editEvent") : t("newEvent")}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose}>{tc("cancel")}</Button>
          <Button
            variant="primary"
            disabled={!form.title || (!sheet.editing && !form.slug) || saveMutation.isPending}
            onClick={() => saveMutation.mutate()}
            leftIcon={<Save size={13} />}
          >
            {saveMutation.isPending ? tc("saving") : sheet.editing ? tc("saveChanges") : t("createEvent")}
          </Button>
        </>
      }
    >
          <label className="ev-field">
            <span className="ev-label">{tc("colTitle")}</span>
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
              <span className="ev-label">{tc("colSlug")}</span>
              <input
                className="g-input"
                value={form.slug}
                onChange={(e) => onChange({ slug: slugify(e.target.value) })}
              />
            </label>
          )}

          <div className="ev-field">
            <span className="ev-label">{tc("colDescription")}</span>
            <MarkdownEditor
              value={form.description}
              onChange={(v) => onChange({ description: v })}
              placeholder={t("descriptionPlaceholder")}
              minHeight={120}
            />
          </div>

          <div className="ev-field-row">
            <label className="ev-field">
              <span className="ev-label">
                <Calendar size={11} style={{ display: "inline", marginRight: 4 }} />{t("startLabel")}
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
                <Calendar size={11} style={{ display: "inline", marginRight: 4 }} />{t("endLabel")}
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
            <span className="ev-label">{t("freezeScoreboardLabel")}</span>
            <input
              type="datetime-local"
              className="g-input"
              value={form.freeze_scoreboard_at}
              onChange={(e) => onChange({ freeze_scoreboard_at: e.target.value })}
            />
          </label>

          <div className="ev-field-row">
            <label className="ev-field">
              <span className="ev-label">{tc("colVisibility")}</span>
              <select
                className="g-input"
                value={form.visibility}
                onChange={(e) => onChange({ visibility: e.target.value as EventVisibility })}
              >
                <option value="private">{t("visibilityPrivate")}</option>
                <option value="unlisted">{t("visibilityUnlisted")}</option>
                <option value="public">{t("visibilityPublic")}</option>
              </select>
            </label>
            <label className="ev-field">
              <span className="ev-label">{t("scoringModeLabel")}</span>
              <select
                className="g-input"
                value={form.scoring_mode}
                onChange={(e) => onChange({ scoring_mode: e.target.value as EventScoringMode })}
              >
                <option value="static">{t("scoringStatic")}</option>
                <option value="dynamic">{t("scoringDynamic")}</option>
              </select>
            </label>
          </div>

          <label className="ev-field">
            <span className="ev-label">{t("maxTeamSizeLabel")}</span>
            <input
              type="number"
              className="g-input"
              min={1}
              placeholder={t("unlimitedPlaceholder")}
              value={form.max_team_size}
              onChange={(e) => onChange({ max_team_size: e.target.value })}
            />
          </label>
    </SheetShell>
  );
}
