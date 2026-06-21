"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useState } from "react";
import { Save } from "lucide-react";
import { type PlatformRole, type PlatformRoleCreate, type PlatformRoleUpdate } from "@/lib/api/admin";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";

const PERMISSION_GROUPS = [
  {
    label: "Platform Pages",
    perms: [
      { key: "platform.dashboard", label: "Dashboard" },
      { key: "platform.challenges", label: "Challenges" },
      { key: "platform.events", label: "Events" },
      { key: "platform.scoreboard", label: "Scoreboard" },
      { key: "platform.badges", label: "Badges" },
      { key: "platform.labs", label: "Labs" },
      { key: "platform.deployments", label: "Deployments" },
      { key: "platform.teams", label: "Teams" },
    ],
  },
  {
    label: "Admin Section",
    perms: [
      { key: "admin.panel", label: "Admin Panel Access" },
      { key: "admin.users.view", label: "View Users" },
      { key: "admin.users.manage", label: "Manage Users" },
      { key: "admin.teams.view", label: "View Teams" },
      { key: "admin.deployments.view", label: "View Deployments" },
      { key: "admin.deployments.manage", label: "Manage Deployments" },
      { key: "admin.audit.view", label: "View Audit Log" },
      { key: "admin.challenges.manage", label: "Manage Challenges" },
      { key: "admin.events.manage", label: "Manage Events" },
      { key: "admin.api_keys.view", label: "View API Keys" },
      { key: "admin.ranks.manage", label: "Manage Ranks" },
      { key: "admin.assessments.manage", label: "Manage Assessments" },
      { key: "admin.content.manage", label: "Content Moderation" },
      { key: "admin.settings.manage", label: "Platform Settings" },
    ],
  },
  {
    label: "Creator",
    perms: [{ key: "creator.access", label: "Creator Access" }],
  },
];

const BLANK_FORM = {
  slug: "",
  display_name: "",
  description: "",
  permissions: [] as string[],
  is_default: false,
};

function roleToForm(role: PlatformRole) {
  return {
    slug: role.slug,
    display_name: role.display_name,
    description: role.description ?? "",
    permissions: role.permissions,
    is_default: role.is_default,
  };
}

interface RoleFormSheetProps {
  open: boolean;
  initialValues?: PlatformRole | null;
  saveMutation: { mutate: (data: PlatformRoleCreate | PlatformRoleUpdate) => void; isPending: boolean };
  onClose: () => void;
}

export function RoleFormSheet({ open, initialValues, saveMutation, onClose }: RoleFormSheetProps) {
  const [form, setForm] = useState(BLANK_FORM);
  const isEdit = !!initialValues;

  useEffect(() => {
    if (open) setForm(initialValues ? roleToForm(initialValues) : BLANK_FORM);
  }, [open, initialValues]);

  useEscapeKey(onClose, open);

  if (!open) return null;

  function togglePerm(key: string) {
    setForm((f) => ({
      ...f,
      permissions: f.permissions.includes(key)
        ? f.permissions.filter((p) => p !== key)
        : [...f.permissions, key],
    }));
  }

  function handleSubmit() {
    if (!form.display_name || (!isEdit && !form.slug)) return;
    saveMutation.mutate(
      isEdit
        ? {
            display_name: form.display_name,
            description: form.description || undefined,
            permissions: form.permissions,
            is_default: form.is_default,
          }
        : {
            slug: form.slug,
            display_name: form.display_name,
            description: form.description || undefined,
            permissions: form.permissions,
            is_default: form.is_default,
          }
    );
  }

  return (
    <SheetShell
      title={isEdit ? `Edit — ${initialValues!.slug}` : "New Role"}
      onClose={onClose}
      footer={
        <>
          <button className="g-btn g-btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button
            className="g-btn g-btn-primary"
            disabled={!form.display_name || (!isEdit && !form.slug) || saveMutation.isPending}
            onClick={handleSubmit}
          >
            <Save size={13} />
            {saveMutation.isPending ? "Saving…" : isEdit ? "Save Changes" : "Create Role"}
          </button>
        </>
      }
    >
          {!isEdit && (
            <label className="ev-field">
              <span className="ev-label">Slug</span>
              <input
                className="g-input"
                style={{ fontFamily: "var(--font-mono, monospace)" }}
                value={form.slug}
                onChange={(e) => setForm((f) => ({ ...f, slug: e.target.value }))}
                placeholder="custom-role"
              />
            </label>
          )}

          <label className="ev-field">
            <span className="ev-label">Display Name</span>
            <input
              className="g-input"
              value={form.display_name}
              onChange={(e) => setForm((f) => ({ ...f, display_name: e.target.value }))}
              placeholder="Custom Role"
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">Description</span>
            <input
              className="g-input"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              placeholder="What this role grants"
            />
          </label>

          <div className="field checkbox-field">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={form.is_default}
                onChange={(e) => setForm((f) => ({ ...f, is_default: e.target.checked }))}
              />
              <span className="text-sm">Assign automatically to new users</span>
            </label>
          </div>

          {PERMISSION_GROUPS.map((group) => (
            <div className="perm-group" key={group.label}>
              <div className="perm-group-title">{group.label}</div>
              {group.perms.map((perm) => (
                <label key={perm.key} className="perm-checkbox">
                  <input
                    type="checkbox"
                    checked={form.permissions.includes(perm.key)}
                    onChange={() => togglePerm(perm.key)}
                  />
                  {perm.label}
                </label>
              ))}
            </div>
          ))}
    </SheetShell>
  );
}
