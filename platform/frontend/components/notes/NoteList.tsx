"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Download, Pencil, Trash2, Users, Lock } from "lucide-react";
import { useApiMutation } from "@/hooks/useApiMutation";
import { useConfirmStore } from "@/stores/confirm.store";
import { listNotes, deleteNote, exportNote, type Note, type NoteListParams } from "@/lib/api/notes";
import { getTeams } from "@/lib/api/teams";
import { Button } from "@/components/ui/Button";
import { NoteEditorSheet } from "./NoteEditorSheet";

export function NoteList({ filter, emptyMessage = "No notes yet." }: { filter?: NoteListParams; emptyMessage?: string }) {
  const [editing, setEditing] = useState<Note | "new" | null>(null);
  const { confirm } = useConfirmStore();

  const { data: notes = [], isLoading } = useQuery({
    queryKey: ["notes", filter ?? {}],
    queryFn: () => listNotes(filter),
  });

  const { data: teams = [] } = useQuery({ queryKey: ["teams"], queryFn: getTeams });
  const teamName = (id: number | null) => teams.find((t) => t.id === id)?.name ?? "team";

  const deleteMutation = useApiMutation<void, number>({
    mutationFn: (id) => deleteNote(id),
    invalidateKeys: [["notes"]],
    successMessage: "Note deleted.",
    errorMessage: "Failed to delete note.",
  });

  function handleDelete(note: Note) {
    confirm({
      title: "Delete note?",
      body: `"${note.title}" will be permanently deleted.`,
      dangerous: true,
      onConfirm: () => deleteMutation.mutate(note.id),
    });
  }

  return (
    <div className="notes-list-wrap">
      <div className="notes-list-header">
        <Button variant="primary" onClick={() => setEditing("new")}>
          New Note
        </Button>
      </div>

      {isLoading ? (
        <div className="text-muted text-xs">Loading notes…</div>
      ) : notes.length === 0 ? (
        <div className="text-muted text-xs">{emptyMessage}</div>
      ) : (
        <div className="notes-list">
          {notes.map((note) => (
            <div key={note.id} className="g-card note-card">
              <div className="note-card-header">
                <h3 className="note-card-title">{note.title}</h3>
                <div className="note-card-actions">
                  <Button size="sm" icon title="Export as Markdown" onClick={() => exportNote(note.id)}>
                    <Download size={13} />
                  </Button>
                  <Button size="sm" icon title="Edit" onClick={() => setEditing(note)}>
                    <Pencil size={13} />
                  </Button>
                  <Button size="sm" icon variant="danger-ghost" title="Delete" onClick={() => handleDelete(note)}>
                    <Trash2 size={13} />
                  </Button>
                </div>
              </div>

              {note.content && (
                <div className="note-card-preview md-preview">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{note.content}</ReactMarkdown>
                </div>
              )}

              <div className="note-card-footer">
                <span className="note-card-visibility" title={note.visibility === "team" ? `Shared with ${teamName(note.team_id)}` : "Private"}>
                  {note.visibility === "team" ? <Users size={11} /> : <Lock size={11} />}
                  {note.visibility === "team" && teamName(note.team_id)}
                </span>
                {note.tags.map((t) => (
                  <span key={t} className="g-tag text-10">{t}</span>
                ))}
                <span className="note-card-updated text-muted">
                  Updated {new Date(note.updated_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {editing !== null && (
        <NoteEditorSheet
          key={editing === "new" ? "new" : editing.id}
          open
          note={editing === "new" ? undefined : editing}
          defaultLabTemplateId={filter?.lab_template_id}
          defaultChallengeId={filter?.challenge_id}
          onClose={() => setEditing(null)}
        />
      )}
    </div>
  );
}
