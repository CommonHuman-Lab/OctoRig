"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
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
    successMessage: note ? "Note updated." : "Note created.",
    errorMessage: note ? "Failed to update note." : "Failed to create note.",
    onSuccess: onClose,
  });

  useEscapeKey(onClose, open);

  if (!open) return null;

  return (
    <SheetShell
      title={note ? "Edit Note" : "New Note"}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose}>Cancel</Button>
          <Button
            variant="primary"
            disabled={!title.trim() || (visibility === "team" && !teamId) || isPending}
            onClick={() => mutate()}
          >
            {isPending ? "Saving…" : note ? "Save Changes" : "Create Note"}
          </Button>
        </>
      }
    >
      <label className="ev-field">
        <span className="ev-label">Title</span>
        <input
          className="g-input"
          placeholder="Note title…"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          autoFocus
        />
      </label>

      <label className="ev-field">
        <span className="ev-label">Content</span>
        <MarkdownEditor value={content} onChange={setContent} placeholder="Write anything — markdown is optional…" />
      </label>

      <label className="ev-field">
        <span className="ev-label">Tags (comma separated)</span>
        <input
          className="g-input"
          placeholder="recon, sqli, todo…"
          value={tagsInput}
          onChange={(e) => setTagsInput(e.target.value)}
        />
      </label>

      <div className="ev-field-row">
        <label className="ev-field">
          <span className="ev-label">Linked Lab</span>
          <SearchableSelect
            options={labs.map((l) => ({ id: l.id, label: l.name }))}
            value={labTemplateId}
            onChange={setLabTemplateId}
            placeholder="Search labs…"
          />
        </label>
        <label className="ev-field">
          <span className="ev-label">Linked Challenge</span>
          <SearchableSelect
            options={challenges.map((c) => ({ id: c.id, label: c.title }))}
            value={challengeId}
            onChange={setChallengeId}
            placeholder="Search challenges…"
          />
        </label>
      </div>

      <div className="ev-field-row">
        <label className="ev-field">
          <span className="ev-label">Visibility</span>
          <select
            className="g-input"
            value={visibility}
            onChange={(e) => {
              const next = e.target.value as NoteVisibility;
              setVisibility(next);
              if (next === "team" && !teamId && teams.length === 1) setTeamId(teams[0].id);
            }}
          >
            <option value="private">Private</option>
            <option value="team">Shared with a team</option>
          </select>
        </label>
        {visibility === "team" && (
          <label className="ev-field">
            <span className="ev-label">Team</span>
            <select
              className="g-input"
              value={teamId ?? ""}
              onChange={(e) => setTeamId(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">Select a team…</option>
              {teams.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </label>
        )}
      </div>
    </SheetShell>
  );
}
