// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { apiClient } from "./client";
import { PAGINATION } from "@/lib/config";
import type { ScoreboardEntry, ChallengeDifficulty } from "./challenges";

export type EventStatus = "draft" | "published" | "running" | "ended" | "archived";
export type EventVisibility = "public" | "private" | "unlisted";
export type EventScoringMode = "static" | "dynamic";

export interface CtfEvent {
  id: number;
  slug: string;
  title: string;
  description: string | null;
  status: EventStatus;
  visibility: EventVisibility;
  scoring_mode: EventScoringMode;
  start_at: string | null;
  end_at: string | null;
  max_team_size: number | null;
  freeze_scoreboard_at: string | null;
  created_at: string;
  scoreboard_frozen: boolean;
}

export interface EventChallenge {
  id: number;
  slug: string;
  title: string;
  category: string;
  difficulty: ChallengeDifficulty;
  points: number;
  tags: string[];
  solve_count: number;
  solved_by_me: boolean;
  released_at: string | null;
}

export async function getEvents(status?: string): Promise<CtfEvent[]> {
  const { data } = await apiClient.get<CtfEvent[]>("/events/", {
    params: status ? { status } : {},
  });
  return data;
}

export async function getEvent(slug: string): Promise<CtfEvent> {
  const { data } = await apiClient.get<CtfEvent>(`/events/${slug}`);
  return data;
}

export async function getEventChallenges(slug: string): Promise<EventChallenge[]> {
  const { data } = await apiClient.get<EventChallenge[]>(`/events/${slug}/challenges`);
  return data;
}

export async function getEventScoreboard(
  slug: string,
  limit: number = PAGINATION.LARGE_LIMIT
): Promise<ScoreboardEntry[]> {
  const { data } = await apiClient.get<ScoreboardEntry[]>(
    `/events/${slug}/scoreboard`,
    { params: { limit } }
  );
  return data;
}

export async function registerTeam(slug: string, teamId: number): Promise<void> {
  await apiClient.post(`/events/${slug}/register`, { team_id: teamId });
}

export interface CreateEventPayload {
  slug: string;
  title: string;
  description?: string;
  start_at?: string;
  end_at?: string;
  visibility: EventVisibility;
  scoring_mode: EventScoringMode;
  max_team_size?: number;
}

export async function createEvent(payload: CreateEventPayload): Promise<CtfEvent> {
  const { data } = await apiClient.post<CtfEvent>("/events/", payload);
  return data;
}

export async function transitionEvent(slug: string, status: EventStatus): Promise<CtfEvent> {
  const { data } = await apiClient.post<CtfEvent>(`/events/${slug}/status`, { status });
  return data;
}

export interface UpdateEventPayload {
  title?: string;
  description?: string | null;
  start_at?: string | null;
  end_at?: string | null;
  visibility?: EventVisibility;
  scoring_mode?: EventScoringMode;
  max_team_size?: number | null;
  freeze_scoreboard_at?: string | null;
}

export async function updateEvent(slug: string, payload: UpdateEventPayload): Promise<CtfEvent> {
  const { data } = await apiClient.patch<CtfEvent>(`/events/${slug}`, payload);
  return data;
}

export async function addEventChallenge(
  slug: string,
  challengeId: number,
  pointsOverride?: number | null
): Promise<void> {
  await apiClient.post(`/events/${slug}/challenges`, {
    challenge_id: challengeId,
    points_override: pointsOverride ?? null,
  });
}

export async function removeEventChallenge(slug: string, challengeId: number): Promise<void> {
  await apiClient.delete(`/events/${slug}/challenges/${challengeId}`);
}
