// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { apiClient } from "./client";

export interface SiteSettings {
  registration_open: boolean;
  maintenance_mode: boolean;
  maintenance_message: string | null;
  max_flag_attempts: number | null;
  dynamic_scoring_enabled: boolean;
  dynamic_decay_factor: number;
  dynamic_min_floor_pct: number;
  scoreboard_frozen_at: string | null;
  first_blood_enabled: boolean;
  python_editor_enabled: boolean;
  hide_lab_ports: boolean;
  company_name: string | null;
  company_logo_url: string | null;
  default_theme: string | null;
  default_locale: string | null;
  updated_at: string;
}

export interface PublicSettings {
  registration_open: boolean;
  maintenance_mode: boolean;
  maintenance_message: string | null;
  first_blood_enabled: boolean;
  python_editor_enabled: boolean;
  company_name: string | null;
  company_logo_url: string | null;
  default_theme: string | null;
  default_locale: string | null;
}

export type SiteSettingsPatch = Partial<Omit<SiteSettings, "updated_at">>;

export async function getSiteSettings(): Promise<SiteSettings> {
  const { data } = await apiClient.get<SiteSettings>("/admin/settings");
  return data;
}

export async function updateSiteSettings(
  patch: SiteSettingsPatch
): Promise<SiteSettings> {
  const { data } = await apiClient.patch<SiteSettings>("/admin/settings", patch);
  return data;
}

export async function getPublicSettings(): Promise<PublicSettings> {
  const { data } = await apiClient.get<PublicSettings>("/auth/settings/public");
  return data;
}

export async function revokeAdminApiKey(keyId: number): Promise<void> {
  await apiClient.delete(`/admin/api-keys/${keyId}`);
}
