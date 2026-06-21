"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

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
  return (
    <form
      className="g-card g-form"
      onSubmit={onSubmit}
    >
      <div className="form-row">
        <label className="form-label">Bio</label>
        <textarea
          className="g-textarea"
          rows={3}
          value={form.bio ?? ""}
          onChange={(e) => onChange("bio", e.target.value)}
          placeholder="A short bio about yourself…"
        />
      </div>

      <div className="form-row">
        <label className="form-label">Avatar URL</label>
        <input
          className="g-input"
          value={form.avatar_url ?? ""}
          onChange={(e) => onChange("avatar_url", e.target.value)}
          placeholder="https://…"
        />
      </div>

      <div className="form-row">
        <label className="form-label">Website</label>
        <input
          className="g-input"
          value={form.website_url ?? ""}
          onChange={(e) => onChange("website_url", e.target.value)}
          placeholder="https://…"
        />
      </div>

      <div className="form-row">
        <label className="form-label">Location</label>
        <input
          className="g-input"
          value={form.location ?? ""}
          onChange={(e) => onChange("location", e.target.value)}
          placeholder="City, Country"
        />
      </div>

      <div className="form-row">
        <label className="form-label">GitHub handle</label>
        <input
          className="g-input"
          value={form.github_handle ?? ""}
          onChange={(e) => onChange("github_handle", e.target.value)}
          placeholder="username"
        />
      </div>

      <div className="form-row">
        <label className="form-label">Privacy</label>
        <select
          className="g-select"
          value={form.privacy_level ?? "public"}
          onChange={(e) => onChange("privacy_level", e.target.value)}
        >
          <option value="public">Public — visible to everyone</option>
          <option value="team_only">Team only</option>
          <option value="private">Private</option>
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
          Show recent activity on profile
        </label>
      </div>

      <div className="form-actions">
        <Button
          type="submit"
          variant="primary"
          disabled={isPending}
        >
          {isPending ? "Saving…" : "Save Changes"}
        </Button>
      </div>
    </form>
  );
}
