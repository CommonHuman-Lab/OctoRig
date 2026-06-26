// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { apiClient } from "./client";

export interface ProfileBadge {
  slug: string;
  name: string;
  icon: string;
  awarded_at: string;
}

export interface RecentSolve {
  challenge_id: number;
  challenge_title: string;
  challenge_slug: string;
  points_awarded: number;
  submitted_at: string;
  is_first_blood: boolean;
}

export interface UserProfile {
  user_id: number;
  username: string;
  bio: string | null;
  avatar_url: string | null;
  website_url: string | null;
  location: string | null;
  github_handle: string | null;
  privacy_level: "public" | "team_only" | "private";
  show_activity: boolean;
  theme: string | null;
  locale: string | null;
  total_points: number;
  solve_count: number;
  first_bloods: number;
  team_count: number;
  badges: ProfileBadge[];
  recent_solves: RecentSolve[];
}

export interface ProfileUpdatePayload {
  bio?: string;
  avatar_url?: string;
  website_url?: string;
  location?: string;
  github_handle?: string;
  privacy_level?: "public" | "team_only" | "private";
  show_activity?: boolean;
  theme?: string | null;
  locale?: string | null;
}

export async function getMyProfile(): Promise<UserProfile> {
  const { data } = await apiClient.get<UserProfile>("/profiles/me");
  return data;
}

export async function updateMyProfile(payload: ProfileUpdatePayload): Promise<UserProfile> {
  const { data } = await apiClient.patch<UserProfile>("/profiles/me", payload);
  return data;
}

export async function getUserProfile(username: string): Promise<UserProfile> {
  const { data } = await apiClient.get<UserProfile>(`/profiles/${username}`);
  return data;
}
