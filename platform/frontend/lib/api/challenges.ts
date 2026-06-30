// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { apiClient } from "./client";
import { PAGINATION } from "@/lib/config";

export type ChallengeDifficulty = "easy" | "medium" | "hard" | "insane";
export type ChallengeType =
  | "flag" | "mcq" | "short_answer" | "file_upload"
  | "dynamic_flag" | "api" | "web" | "container";

export interface HintSummary {
  id: number;
  order_num: number;
  cost: number;
  content: string | null;
  unlocked: boolean;
}

export interface RequiredLabSummary {
  slug: string;
  name: string;
}

export interface ChallengeListItem {
  id: number;
  slug: string;
  title: string;
  difficulty: ChallengeDifficulty;
  category: string;
  tags: string[];
  points: number;
  challenge_type: ChallengeType;
  estimated_minutes: number | null;
  solve_count: number;
  solved_by_me: boolean;
  is_active: boolean;
  lab_slug: string | null;
  lab_name: string | null;
  lab_category: string | null;
  required_labs: RequiredLabSummary[];
}

export interface ChallengeDetail extends ChallengeListItem {
  description: string;
  skills: string[];
  content: Record<string, unknown>;
  hints: HintSummary[];
  files: Array<{ id: number; filename: string; size_bytes: number }>;
  first_blood_user: string | null;
  version: number;
  lab_slug: string | null;
  lab_name: string | null;
  lab_category: string | null;
  required_labs: RequiredLabSummary[];
}

export interface FlagSubmitResult {
  correct: boolean;
  already_solved: boolean;
  first_blood: boolean;
  points_awarded: number;
  message: string;
}

export interface HintUnlockResult {
  hint_id: number;
  content: string;
  cost: number;
}

export interface ScoreboardEntry {
  rank: number;
  user_id: number | null;
  username: string | null;
  team_id: number | null;
  total: number;
  solve_count: number;
  badge_count: number;
  last_tx: string | null;
  frozen?: boolean;
}

export async function getChallenges(params?: {
  category?: string;
  difficulty?: string;
  search?: string;
  tag?: string;
  lab_category?: string;
  lab_slug?: string;
}): Promise<ChallengeListItem[]> {
  const { data } = await apiClient.get<ChallengeListItem[]>("/challenges/", {
    params,
  });
  return data;
}

export async function getChallenge(slug: string): Promise<ChallengeDetail> {
  const { data } = await apiClient.get<ChallengeDetail>(`/challenges/${slug}`);
  return data;
}

export async function submitFlag(
  slug: string,
  flag: string,
  event_id?: number
): Promise<FlagSubmitResult> {
  const { data } = await apiClient.post<FlagSubmitResult>(
    `/challenges/${slug}/submit`,
    { flag, event_id: event_id ?? null }
  );
  return data;
}

export async function unlockHint(
  slug: string,
  hintId: number
): Promise<HintUnlockResult> {
  const { data } = await apiClient.post<HintUnlockResult>(
    `/challenges/${slug}/hints/${hintId}/unlock`
  );
  return data;
}

export async function getGlobalScoreboard(
  limit: number = PAGINATION.LARGE_LIMIT
): Promise<ScoreboardEntry[]> {
  const { data } = await apiClient.get<ScoreboardEntry[]>(
    "/scoreboards/global",
    { params: { limit } }
  );
  return data;
}

export async function getAdminChallenges(): Promise<ChallengeListItem[]> {
  const { data } = await apiClient.get<ChallengeListItem[]>("/challenges/admin/all");
  return data;
}

export async function setChallengeActive(
  slug: string,
  is_active: boolean
): Promise<{ slug: string; is_active: boolean }> {
  const { data } = await apiClient.patch(`/challenges/${slug}/active`, { is_active });
  return data;
}
