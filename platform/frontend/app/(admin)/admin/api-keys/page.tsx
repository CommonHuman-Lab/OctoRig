"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../admin.css";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Key, ShieldOff } from "lucide-react";
import { getAdminApiKeys } from "@/lib/api/admin";
import { revokeAdminApiKey } from "@/lib/api/settings";
import { useConfirmStore } from "@/stores/confirm.store";
import { useUserStore } from "@/stores/user.store";
import { useAdminGuard } from "@/hooks/useAdminGuard";
import { formatDateTime } from "@/lib/utils/date";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { Button } from "@/components/ui/Button";

export default function AdminApiKeysPage() {
  const t = useTranslations("admin.apiKeys");
  const tApiKeys = useTranslations("apiKeys");
  const tNav = useTranslations("nav");
  const tCommon = useTranslations("common");
  const { confirm } = useConfirmStore();
  const { user } = useUserStore();

  useAdminGuard();

  const [activeOnly, setActiveOnly] = useState(true);

  const { data: keys = [], isLoading } = useQuery({
    queryKey: ["admin-api-keys", activeOnly],
    queryFn: () => getAdminApiKeys({ active_only: activeOnly }),
    enabled: !!user?.permissions?.includes("admin.panel"),
  });

  const revokeMutation = useApiMutation({
    mutationFn: revokeAdminApiKey,
    invalidateKeys: [["admin-api-keys"]],
    successMessage: tApiKeys("revokedToast"),
    errorMessage: tApiKeys("revokeFailed"),
  });

  function handleRevoke(id: number, name: string, username: string) {
    confirm({
      title: t("revokeTitle"),
      body: t("revokeBody", { name, username }),
      confirmLabel: t("revokeBtn"),
      dangerous: true,
      onConfirm: () => revokeMutation.mutate(id),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">
          <Key size={16} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
          {tNav("apiKeys")}
        </h1>
        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8125rem", color: "var(--g-text-muted)", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(e) => setActiveOnly(e.target.checked)}
          />
          {t("activeOnlyLabel")}
        </label>
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={keys}
        empty={
          <div className="g-card" style={{ textAlign: "center", padding: "2rem", color: "var(--g-text-muted)" }}>
            {t("noKeysFound")}
          </div>
        }
      >
        {(keys) => (
          <div className="g-card" style={{ padding: 0, overflow: "hidden" }}>
            <table className="g-table">
              <thead>
                <tr>
                  <th>{t("colKey")}</th>
                  <th>{tCommon("owner")}</th>
                  <th>{tApiKeys("colCreated")}</th>
                  <th>{tApiKeys("colLastUsed")}</th>
                  <th>{tApiKeys("colExpires")}</th>
                  <th>{tCommon("colStatus")}</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {keys.map((k) => (
                  <tr key={k.id} style={{ opacity: k.is_active ? 1 : 0.5 }}>
                    <td>
                      <div style={{ fontWeight: 600, fontSize: "0.8125rem", fontFamily: "monospace" }}>{k.name}</div>
                      <div style={{ fontSize: "0.6875rem", color: "var(--g-text-muted)", fontFamily: "monospace" }}>{k.key_prefix}…</div>
                    </td>
                    <td style={{ fontSize: "0.8125rem" }}>{k.username}</td>
                    <td style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>
                      {formatDateTime(k.created_at)}
                    </td>
                    <td style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>
                      {k.last_used_at ? formatDateTime(k.last_used_at) : tApiKeys("never")}
                    </td>
                    <td style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>
                      {k.expires_at ? formatDateTime(k.expires_at) : tApiKeys("never")}
                    </td>
                    <td>
                      <span style={{
                        fontSize: "0.6875rem", fontWeight: 700, fontFamily: "monospace",
                        textTransform: "uppercase",
                        color: k.is_active ? "var(--g-success)" : "var(--g-text-muted)",
                      }}>
                        {k.is_active ? tApiKeys("active") : tApiKeys("revoked")}
                      </span>
                    </td>
                    <td>
                      {k.is_active && (
                        <Button
                          variant="danger"
                          size="sm"
                          leftIcon={<ShieldOff size={12} />}
                          disabled={revokeMutation.isPending}
                          onClick={() => handleRevoke(k.id, k.name, k.username)}
                        >
                          {t("revokeBtn")}
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </AsyncContent>
    </div>
  );
}
