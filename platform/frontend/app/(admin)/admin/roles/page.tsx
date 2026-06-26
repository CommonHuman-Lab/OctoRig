"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./roles-admin.css";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Plus, Trash2 } from "lucide-react";
import {
  listRoles,
  createRole,
  updateRole,
  deleteRole,
  type PlatformRole,
} from "@/lib/api/admin";
import { useConfirmStore } from "@/stores/confirm.store";
import { useAdminGuard } from "@/hooks/useAdminGuard";
import { RoleFormSheet } from "@/components/admin/roles/RoleFormSheet";
import { Button } from "@/components/ui/Button";

export default function AdminRolesPage() {
  useAdminGuard();
  const t = useTranslations("admin.roles");
  const tCommon = useTranslations("common");
  const { confirm } = useConfirmStore();

  const [sheetOpen, setSheetOpen] = useState(false);
  const [selected, setSelected] = useState<PlatformRole | null>(null);

  const { data: roles = [], isLoading } = useQuery({
    queryKey: ["admin-roles"],
    queryFn: listRoles,
  });

  function openCreate() {
    setSelected(null);
    setSheetOpen(true);
  }

  function openEdit(role: PlatformRole) {
    setSelected(role);
    setSheetOpen(true);
  }

  function closeSheet() {
    setSheetOpen(false);
    setSelected(null);
  }

  const saveMutation = useApiMutation({
    mutationFn: (payload: any) =>
      selected ? updateRole(selected.slug, payload) : createRole(payload),
    invalidateKeys: [["admin-roles"]],
    successMessage: () => (selected ? t("toastRoleUpdated") : t("toastRoleCreated")),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("toastSaveRoleFailed"),
    onSuccess: closeSheet,
  });

  const deleteMutation = useApiMutation({
    mutationFn: (slug: string) => deleteRole(slug),
    invalidateKeys: [["admin-roles"]],
    successMessage: t("toastRoleDeleted"),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("toastDeleteRoleFailed"),
    onSuccess: closeSheet,
  });

  const toggleDefaultMutation = useApiMutation({
    mutationFn: ({ slug, is_default }: { slug: string; is_default: boolean }) =>
      updateRole(slug, { is_default }),
    invalidateKeys: [["admin-roles"]],
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("toastUpdateRoleFailed"),
  });

  function handleDelete(role: PlatformRole) {
    confirm({
      title: t("deleteRoleTitle"),
      body: t("deleteRoleBody", { name: role.display_name }),
      confirmLabel: tCommon("delete"),
      dangerous: true,
      onConfirm: () => deleteMutation.mutate(role.slug),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title font-mono">{t("title")}</h1>
          <p className="page-sub">{t("rolesConfigured", { count: roles.length })}</p>
        </div>
        <Button variant="primary" leftIcon={<Plus size={13} />} onClick={openCreate}>
          {t("newRole")}
        </Button>
      </div>

      <div className="g-card" style={{ padding: 0, overflow: "hidden" }}>
        {isLoading ? (
          <div className="loading-cell text-muted text-sm">{tCommon("loading")}</div>
        ) : (
          <table className="g-table">
            <thead>
              <tr>
                <th>{tCommon("colSlug")}</th>
                <th>{tCommon("colName")}</th>
                <th>{t("colPermissions")}</th>
                <th>{tCommon("colType")}</th>
                <th>{t("colDefault")}</th>
                <th>{tCommon("actions")}</th>
              </tr>
            </thead>
            <tbody>
              {roles.map((role) => {
                const isAdmin = role.slug === "admin";
                return (
                  <tr
                    key={role.slug}
                    onClick={() => !isAdmin && openEdit(role)}
                    style={{ cursor: isAdmin ? "default" : "pointer" }}
                  >
                    <td className="font-mono text-sm">{role.slug}</td>
                    <td className="text-sm">{role.display_name}</td>
                    <td className="text-11 text-muted">{role.permissions.length}</td>
                    <td>
                      <span className={`g-status-pill ${role.is_system ? "g-status-pill--on" : "g-status-pill--off"}`}>
                        {role.is_system ? t("system") : t("custom")}
                      </span>
                    </td>
                    <td>
                      <label
                        className="toggle"
                        title={isAdmin ? t("adminRoleLockedTooltip") : t("assignAutomatically")}
                        onClick={(e) => e.stopPropagation()}
                      >
                        <input
                          type="checkbox"
                          checked={role.is_default}
                          disabled={isAdmin || toggleDefaultMutation.isPending}
                          onChange={(e) =>
                            toggleDefaultMutation.mutate({ slug: role.slug, is_default: e.target.checked })
                          }
                        />
                        <span className="toggle-track" />
                      </label>
                    </td>
                    <td>
                      {!role.is_system && (
                        <Button
                          icon
                          tooltip={t("deleteRoleTooltip")}
                          leftIcon={<Trash2 size={13} />}
                          onClick={(e) => { e.stopPropagation(); handleDelete(role); }}
                        />
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      <RoleFormSheet
        open={sheetOpen}
        initialValues={selected}
        saveMutation={saveMutation}
        onClose={closeSheet}
      />
    </div>
  );
}
