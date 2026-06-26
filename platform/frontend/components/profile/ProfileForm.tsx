"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useTranslations } from "next-intl";
import type { ProfileUpdatePayload } from "@/lib/api/profiles";
import { Button } from "@/components/ui/Button";

export function ProfileForm({
  form,
  onChange,
  onSubmit,
  isPending,
}: {
  form: ProfileUpdatePayload;
  onChange: (key: keyof ProfileUpdatePayload, value: unknown) => void;
  onSubmit: (e: React.FormEvent) => void;
  isPending: boolean;
}) {
  const t = useTranslations("profile");
  const td = useTranslations("deployments");
  const tc = useTranslations("common");
  return (
    <form
      className="g-card g-form"
      onSubmit={onSubmit}
    >
      <div className="form-row">
        <label className="form-label">{t("bioLabel")}</label>
        <textarea
          className="g-textarea"
          rows={3}
          value={form.bio ?? ""}
          onChange={(e) => onChange("bio", e.target.value)}
          placeholder={t("bioPlaceholder")}
        />
      </div>

      <div className="form-row">
        <label className="form-label">{t("avatarUrlLabel")}</label>
        <input
          className="g-input"
          value={form.avatar_url ?? ""}
          onChange={(e) => onChange("avatar_url", e.target.value)}
          placeholder={t("urlPlaceholder")}
        />
      </div>

      <div className="form-row">
        <label className="form-label">{t("websiteLabel")}</label>
        <input
          className="g-input"
          value={form.website_url ?? ""}
          onChange={(e) => onChange("website_url", e.target.value)}
          placeholder={t("urlPlaceholder")}
        />
      </div>

      <div className="form-row">
        <label className="form-label">{t("locationLabel")}</label>
        <input
          className="g-input"
          value={form.location ?? ""}
          onChange={(e) => onChange("location", e.target.value)}
          placeholder={t("locationPlaceholder")}
        />
      </div>

      <div className="form-row">
        <label className="form-label">{t("githubLabel")}</label>
        <input
          className="g-input"
          value={form.github_handle ?? ""}
          onChange={(e) => onChange("github_handle", e.target.value)}
          placeholder={t("githubPlaceholder")}
        />
      </div>

      <div className="form-row">
        <label className="form-label">{t("privacyLabel")}</label>
        <select
          className="g-select"
          value={form.privacy_level ?? "public"}
          onChange={(e) => onChange("privacy_level", e.target.value)}
        >
          <option value="public">{t("privacyPublic")}</option>
          <option value="team_only">{t("privacyTeamOnly")}</option>
          <option value="private">{td("visPrivate")}</option>
        </select>
      </div>

      <div className="form-row form-checkbox">
        <input
          type="checkbox"
          id="show_activity"
          checked={form.show_activity ?? true}
          onChange={(e) => onChange("show_activity", e.target.checked)}
        />
        <label htmlFor="show_activity" className="form-label-inline">
          {t("showActivityLabel")}
        </label>
      </div>

      <div className="form-actions">
        <Button
          type="submit"
          variant="primary"
          disabled={isPending}
        >
          {isPending ? tc("saving") : tc("saveChanges")}
        </Button>
      </div>
    </form>
  );
}
