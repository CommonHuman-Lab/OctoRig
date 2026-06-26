"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { Save } from "lucide-react";
import { listRoles } from "@/lib/api/admin";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";
import { Button } from "@/components/ui/Button";

export function CreateUserForm({
  open,
  onSubmit,
  onClose,
  isPending,
}: {
  open: boolean;
  onSubmit: (username: string, email: string, password: string, roles: string[]) => void;
  onClose: () => void;
  isPending: boolean;
}) {
  const t = useTranslations("admin.users");
  const tCommon = useTranslations("common");
  const tSettings = useTranslations("settings");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [roles, setRoles] = useState<string[]>([]);

  const { data: availableRoles = [] } = useQuery({
    queryKey: ["admin-roles"],
    queryFn: listRoles,
  });

  useEscapeKey(onClose, open);

  if (!open) return null;

  function toggleRole(slug: string) {
    setRoles((r) => (r.includes(slug) ? r.filter((s) => s !== slug) : [...r, slug]));
  }

  function handleSubmit() {
    onSubmit(username, email, password, roles);
    setUsername("");
    setEmail("");
    setPassword("");
    setRoles([]);
  }

  return (
    <SheetShell
      title={t("newUserTitle")}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose}>{tCommon("cancel")}</Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={!username || !email || !password || isPending}
            leftIcon={<Save size={13} />}
          >
            {isPending ? t("creating") : t("createUserBtn")}
          </Button>
        </>
      }
    >
          <label className="ev-field">
            <span className="ev-label">{tSettings("usernameLabel")}</span>
            <input
              className="g-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={t("usernamePlaceholder")}
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">{tSettings("emailLabel")}</span>
            <input
              className="g-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t("emailPlaceholder")}
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">{t("passwordLabel")}</span>
            <input
              className="g-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t("passwordPlaceholder")}
            />
          </label>

          <div className="ev-field">
            <span className="ev-label">{t("rolesLabel")}</span>
            {availableRoles.map((role) => (
              <label key={role.slug} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={roles.includes(role.slug)}
                  onChange={() => toggleRole(role.slug)}
                />
                <span className="text-sm">{role.display_name}</span>
              </label>
            ))}
          </div>
    </SheetShell>
  );
}
