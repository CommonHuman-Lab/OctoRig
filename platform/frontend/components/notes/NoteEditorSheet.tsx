"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";
import { Button } from "@/components/ui/Button";
import { MarkdownEditor } from "@/components/ui/MarkdownEditor";
import { SearchableSelect } from "@/components/ui/SearchableSelect";
import { useApiMutation } from "@/hooks/useApiMutation";
import { getLabs } from "@/lib/api/labs";
import { getChallenges } from "@/lib/api/challenges";
import { getTeams } from "@/lib/api/teams";
import {
  createNote, updateNote,
  type Note, type NoteVisibility,
} from "@/lib/api/notes";

interface NoteEditorSheetProps {
  open: boolean;
  note?: Note;
  defaultLabTemplateId?: number | null;
  defaultChallengeId?: number | null;
  onClose: () => void;
}

export function NoteEditorSheet({
  open, note, defaultLabTemplateId, defaultChallengeId, onClose,
}: NoteEditorSheetProps) {
  const t = useTranslations("notes");
  const tc = useTranslations("common");
  const tl = useTranslations("labs");
  const tch = useTranslations("challenges");
  const [title, setTitle] = useState(note?.title ?? "");
  const [content, setContent] = useState(note?.content ?? "");
  const [tagsInput, setTagsInput] = useState(note?.tags.join(", ") ?? "");
  const [labTemplateId, setLabTemplateId] = useState<number | null>(
    note?.lab_template_id ?? defaultLabTemplateId ?? null
  );
  const [challengeId, setChallengeId] = useState<number | null>(
    note?.challenge_id ?? defaultChallengeId ?? null
  );
  const [visibility, setVisibility] = useState<NoteVisibility>(note?.visibility ?? "private");
  const [teamId, setTeamId] = useState<number | null>(note?.team_id ?? null);

  const { data: labs = [] } = useQuery({ queryKey: ["labs"], queryFn: () => getLabs(), enabled: open });
  const { data: challenges = [] } = useQuery({ queryKey: ["challenges"], queryFn: () => getChallenges(), enabled: open });
  const { data: teams = [] } = useQuery({ queryKey: ["teams"], queryFn: getTeams, enabled: open });

  const tags = tagsInput.split(",").map((t) => t.trim()).filter(Boolean);

  const payload = {
    title,
    content,
    tags,
    lab_template_id: labTemplateId,
    challenge_id: challengeId,
    visibility,
    team_id: visibility === "team" ? teamId : null,
  };

  const { mutate, isPending } = useApiMutation<Note, void>({
    mutationFn: () => (note ? updateNote(note.id, payload) : createNote(payload)),
    invalidateKeys: [["notes"]],
    successMessage: note ? t("updatedToast") : t("createdToast"),
    errorMessage: note ? t("updateFailed") : t("createFailed"),
    onSuccess: onClose,
  });

  useEscapeKey(onClose, open);

  if (!open) return null;

  return (
    <SheetShell
      title={note ? t("editNote") : t("newNote")}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose}>{tc("cancel")}</Button>
          <Button
            variant="primary"
            disabled={!title.trim() || (visibility === "team" && !teamId) || isPending}
            onClick={() => mutate()}
          >
            {isPending ? tc("saving") : note ? tc("saveChanges") : t("createNote")}
          </Button>
        </>
      }
    >
      <label className="ev-field">
        <span className="ev-label">{tc("colTitle")}</span>
        <input
          className="g-input"
          placeholder={t("titlePlaceholder")}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          autoFocus
        />
      </label>

      <label className="ev-field">
        <span className="ev-label">{t("contentLabel")}</span>
        <MarkdownEditor value={content} onChange={setContent} placeholder={t("contentPlaceholder")} />
      </label>

      <label className="ev-field">
        <span className="ev-label">{t("tagsLabel")}</span>
        <input
          className="g-input"
          placeholder={t("tagsPlaceholder")}
          value={tagsInput}
          onChange={(e) => setTagsInput(e.target.value)}
        />
      </label>

      <div className="ev-field-row">
        <label className="ev-field">
          <span className="ev-label">{t("linkedLabLabel")}</span>
          <SearchableSelect
            options={labs.map((l) => ({ id: l.id, label: l.name }))}
            value={labTemplateId}
            onChange={setLabTemplateId}
            placeholder={tl("searchPlaceholder")}
          />
        </label>
        <label className="ev-field">
          <span className="ev-label">{t("linkedChallengeLabel")}</span>
          <SearchableSelect
            options={challenges.map((c) => ({ id: c.id, label: c.title }))}
            value={challengeId}
            onChange={setChallengeId}
            placeholder={tch("searchPlaceholder")}
          />
        </label>
      </div>

      <div className="ev-field-row">
        <label className="ev-field">
          <span className="ev-label">{tc("colVisibility")}</span>
          <select
            className="g-input"
            value={visibility}
            onChange={(e) => {
              const next = e.target.value as NoteVisibility;
              setVisibility(next);
              if (next === "team" && !teamId && teams.length === 1) setTeamId(teams[0].id);
            }}
          >
            <option value="private">{t("private")}</option>
            <option value="team">{t("sharedWithTeam")}</option>
          </select>
        </label>
        {visibility === "team" && (
          <label className="ev-field">
            <span className="ev-label">{tc("colTeam")}</span>
            <select
              className="g-input"
              value={teamId ?? ""}
              onChange={(e) => setTeamId(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">{t("selectTeamPlaceholder")}</option>
              {teams.map((team) => (
                <option key={team.id} value={team.id}>{team.name}</option>
              ))}
            </select>
          </label>
        )}
      </div>
    </SheetShell>
  );
}
