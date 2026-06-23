// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { apiClient } from "./client";

export type NoteVisibility = "private" | "team";

export interface Note {
  id: number;
  title: string;
  content: string;
  tags: string[];
  lab_template_id: number | null;
  challenge_id: number | null;
  visibility: NoteVisibility;
  team_id: number | null;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface NoteListParams {
  lab_template_id?: number;
  challenge_id?: number;
  tag?: string;
  q?: string;
}

export interface NoteCreatePayload {
  title: string;
  content?: string;
  tags?: string[];
  lab_template_id?: number | null;
  challenge_id?: number | null;
  visibility?: NoteVisibility;
  team_id?: number | null;
}

export type NoteUpdatePayload = Partial<NoteCreatePayload>;

export async function listNotes(params?: NoteListParams): Promise<Note[]> {
  const { data } = await apiClient.get<Note[]>("/notes", { params });
  return data;
}

export async function getNote(id: number): Promise<Note> {
  const { data } = await apiClient.get<Note>(`/notes/${id}`);
  return data;
}

export async function createNote(payload: NoteCreatePayload): Promise<Note> {
  const { data } = await apiClient.post<Note>("/notes", payload);
  return data;
}

export async function updateNote(id: number, payload: NoteUpdatePayload): Promise<Note> {
  const { data } = await apiClient.patch<Note>(`/notes/${id}`, payload);
  return data;
}

export async function deleteNote(id: number): Promise<void> {
  await apiClient.delete(`/notes/${id}`);
}

export async function exportNote(id: number): Promise<void> {
  const { data, headers } = await apiClient.get<Blob>(`/notes/${id}/export`, {
    responseType: "blob",
  });
  const disposition = headers["content-disposition"] as string | undefined;
  const filename = disposition?.match(/filename="([^"]+)"/)?.[1] ?? `note-${id}.md`;

  const url = URL.createObjectURL(data);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
