"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Save } from "lucide-react";
import { type PlatformRole, type PlatformRoleCreate, type PlatformRoleUpdate } from "@/lib/api/admin";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";
import { Button } from "@/components/ui/Button";

function usePermissionGroups() {
  const t = useTranslations("admin.roles");
  const tNav = useTranslations("nav");

  return [
    {
      label: t("permGroupPlatformPages"),
      perms: [
        { key: "platform.dashboard", label: tNav("dashboard") },
        { key: "platform.challenges", label: tNav("challenges") },
        { key: "platform.events", label: tNav("events") },
        { key: "platform.scoreboard", label: tNav("scoreboard") },
        { key: "platform.badges", label: tNav("badges") },
        { key: "platform.labs", label: tNav("labs") },
        { key: "platform.deployments", label: tNav("deployments") },
        { key: "platform.teams", label: tNav("teams") },
      ],
    },
    {
      label: t("permGroupAdminSection"),
      perms: [
        { key: "admin.panel", label: t("permAdminPanelAccess") },
        { key: "admin.users.view", label: t("permViewUsers") },
        { key: "admin.users.manage", label: t("permManageUsers") },
        { key: "admin.teams.view", label: t("permViewTeams") },
        { key: "admin.deployments.view", label: t("permViewDeployments") },
        { key: "admin.deployments.manage", label: t("permManageDeployments") },
        { key: "admin.audit.view", label: t("permViewAuditLog") },
        { key: "admin.challenges.manage", label: t("permManageChallenges") },
        { key: "admin.events.manage", label: t("permManageEvents") },
        { key: "admin.api_keys.view", label: t("permViewApiKeys") },
        { key: "admin.ranks.manage", label: t("permManageRanks") },
        { key: "admin.assessments.manage", label: t("permManageAssessments") },
        { key: "admin.content.manage", label: t("permContentModeration") },
        { key: "admin.settings.manage", label: t("permPlatformSettings") },
      ],
    },
    {
      label: tNav("creator"),
      perms: [{ key: "creator.access", label: t("permCreatorAccess") }],
    },
  ];
}

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
  const t = useTranslations("admin.roles");
  const tCommon = useTranslations("common");
  const PERMISSION_GROUPS = usePermissionGroups();
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
      title={isEdit ? t("editTitle", { slug: initialValues!.slug }) : t("newRole")}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose}>
            {tCommon("cancel")}
          </Button>
          <Button
            variant="primary"
            disabled={!form.display_name || (!isEdit && !form.slug) || saveMutation.isPending}
            onClick={handleSubmit}
            leftIcon={<Save size={13} />}
          >
            {saveMutation.isPending ? tCommon("saving") : isEdit ? t("saveChanges") : t("createRoleBtn")}
          </Button>
        </>
      }
    >
          {!isEdit && (
            <label className="ev-field">
              <span className="ev-label">{t("slugLabel")}</span>
              <input
                className="g-input"
                style={{ fontFamily: "var(--font-mono, monospace)" }}
                value={form.slug}
                onChange={(e) => setForm((f) => ({ ...f, slug: e.target.value }))}
                placeholder={t("slugPlaceholder")}
              />
            </label>
          )}

          <label className="ev-field">
            <span className="ev-label">{t("displayNameLabel")}</span>
            <input
              className="g-input"
              value={form.display_name}
              onChange={(e) => setForm((f) => ({ ...f, display_name: e.target.value }))}
              placeholder={t("displayNamePlaceholder")}
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">{t("descriptionLabel")}</span>
            <input
              className="g-input"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              placeholder={t("descriptionPlaceholder")}
            />
          </label>

          <div className="field checkbox-field">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={form.is_default}
                onChange={(e) => setForm((f) => ({ ...f, is_default: e.target.checked }))}
              />
              <span className="text-sm">{t("assignAutomatically")}</span>
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
