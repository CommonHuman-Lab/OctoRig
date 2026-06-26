"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./users-admin.css";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Search, UserPlus } from "lucide-react";
import {
  getAdminUsers,
  createAdminUser,
  updateAdminUser,
  resetUserPassword,
  resetUserPoints,
  listRoles,
  type AdminUser,
} from "@/lib/api/admin";
import { useConfirmStore } from "@/stores/confirm.store";
import { useUserStore } from "@/stores/user.store";
import { UsersTable } from "@/components/admin/users/UsersTable";
import { CreateUserForm } from "@/components/admin/users/CreateUserForm";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";
import { Button } from "@/components/ui/Button";

export default function AdminUsersPage() {
  const t = useTranslations("admin.users");
  const tCommon = useTranslations("common");
  const tSettings = useTranslations("settings");
  const { confirm } = useConfirmStore();
  const { user: currentUser } = useUserStore();
  const [showCreate, setShowCreate] = useState(false);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<AdminUser | null>(null);
  const [showReset, setShowReset] = useState(false);
  const [newPw, setNewPw] = useState("");
  const [showRoles, setShowRoles] = useState(false);
  const [pendingRoles, setPendingRoles] = useState<string[]>([]);

  const { data: users = [], isLoading } = useQuery({
    queryKey: ["admin-users", search],
    queryFn: () => getAdminUsers({ search: search || undefined }),
  });

  const { data: availableRoles = [] } = useQuery({
    queryKey: ["admin-roles"],
    queryFn: listRoles,
  });

  const createMutation = useApiMutation({
    mutationFn: (payload: { username: string; email: string; password: string; platform_roles: string[] }) =>
      createAdminUser(payload),
    invalidateKeys: [["admin-users"]],
    successMessage: (data) => t("toastUserCreated", { username: data.username }),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("toastCreateUserFailed"),
    onSuccess: () => setShowCreate(false),
  });

  const updateMutation = useApiMutation({
    mutationFn: ({ id, patch }: { id: number; patch: Parameters<typeof updateAdminUser>[1] }) =>
      updateAdminUser(id, patch),
    invalidateKeys: [["admin-users"]],
    successMessage: t("toastUserUpdated"),
    errorMessage: t("toastUpdateUserFailed"),
    onSuccess: (updated) => setSelected(updated),
  });

  const resetMutation = useApiMutation({
    mutationFn: ({ id, password }: { id: number; password: string }) =>
      resetUserPassword(id, password),
    invalidateKeys: [],
    successMessage: t("toastPasswordReset"),
    errorMessage: t("toastResetPasswordFailed"),
    onSuccess: () => {
      setShowReset(false);
      setNewPw("");
    },
  });

  const resetPointsMutation = useApiMutation({
    mutationFn: (id: number) => resetUserPoints(id),
    invalidateKeys: [["admin-users"]],
    successMessage: t("toastPointsReset"),
    errorMessage: t("toastResetPointsFailed"),
  });

  useEscapeKey(() => setShowReset(false), showReset);
  useEscapeKey(() => setShowRoles(false), showRoles);

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">{t("title")}</h1>
        <div className="header-actions">
          <div className="g-input-icon">
            <Search size={13} className="icon-left" />
            <input
              className="g-input g-input-sm"
              placeholder={t("searchPlaceholder")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<UserPlus size={13} />}
            onClick={() => setShowCreate(true)}
          >
            {t("newUser")}
          </Button>
        </div>
      </div>

      <CreateUserForm
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onSubmit={(username, email, password, roles) =>
          createMutation.mutate({ username, email, password, platform_roles: roles })
        }
        isPending={createMutation.isPending}
      />

      <div className="table-wrap g-panel">
        <UsersTable
          users={users}
          isLoading={isLoading}
          onActivate={(u) => {
            if (!u.is_active) {
              updateMutation.mutate({ id: u.id, patch: { is_active: true } });
              return;
            }
            confirm({
              title: t("deactivateTitle", { username: u.username }),
              body: t("deactivateBody"),
              confirmLabel: t("deactivateConfirm"),
              dangerous: true,
              onConfirm: () => updateMutation.mutate({ id: u.id, patch: { is_active: false } }),
            });
          }}
          onManageRoles={(u) => { setSelected(u); setPendingRoles(u.platform_roles); setShowRoles(true); }}
          onResetPassword={(u) => { setSelected(u); setShowReset(true); }}
          onUnlock={(u) => updateMutation.mutate({ id: u.id, patch: { unlock: true } })}
          onResetPoints={(u) => confirm({
            title: t("resetPointsTitle", { username: u.username }),
            body: t("resetPointsBody"),
            confirmLabel: t("resetPointsConfirm"),
            dangerous: true,
            onConfirm: () => resetPointsMutation.mutate(u.id),
          })}
          isPending={resetPointsMutation.isPending}
          currentUserId={currentUser?.id}
        />
      </div>

      {showReset && selected && (
        <SheetShell
          title={t("resetPasswordTitle", { username: selected.username })}
          onClose={() => setShowReset(false)}
          footer={
            <>
              <Button onClick={() => setShowReset(false)}>{tCommon("cancel")}</Button>
              <Button
                variant="primary"
                disabled={!newPw || resetMutation.isPending}
                onClick={() => resetMutation.mutate({ id: selected.id, password: newPw })}
              >
                {resetMutation.isPending ? t("resetting") : t("resetPasswordBtn")}
              </Button>
            </>
          }
        >
          <label className="ev-field">
            <span className="ev-label">{tSettings("newPasswordLabel")}</span>
            <input
              className="g-input"
              type="password"
              value={newPw}
              onChange={(e) => setNewPw(e.target.value)}
              autoFocus
            />
          </label>
        </SheetShell>
      )}

      {showRoles && selected && (
        <SheetShell
          title={t("manageRolesTitle", { username: selected.username })}
          onClose={() => setShowRoles(false)}
          footer={
            <>
              <Button onClick={() => setShowRoles(false)}>{tCommon("cancel")}</Button>
              <Button
                variant="primary"
                disabled={updateMutation.isPending}
                onClick={() => {
                  updateMutation.mutate({ id: selected.id, patch: { platform_roles: pendingRoles } });
                  setShowRoles(false);
                }}
              >
                {updateMutation.isPending ? tCommon("saving") : t("saveRoles")}
              </Button>
            </>
          }
        >
          {availableRoles.map((role) => (
            <label key={role.slug} className="checkbox-label">
              <input
                type="checkbox"
                checked={pendingRoles.includes(role.slug)}
                onChange={() =>
                  setPendingRoles((r) =>
                    r.includes(role.slug) ? r.filter((s) => s !== role.slug) : [...r, role.slug]
                  )
                }
              />
              <span className="text-sm">{role.display_name}</span>
            </label>
          ))}
        </SheetShell>
      )}
    </div>
  );
}
