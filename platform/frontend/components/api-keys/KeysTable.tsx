// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";
import type { ApiKey } from "@/lib/api/apiKeys";
import { formatDateTime } from "@/lib/utils/date";
import { Button } from "@/components/ui/Button";

export function KeysTable({
  keys,
  onRevoke,
  isPending,
}: {
  keys: ApiKey[];
  onRevoke: (id: number) => void;
  isPending: boolean;
}) {
  const t = useTranslations("apiKeys");
  const tc = useTranslations("common");
  if (keys.length === 0) {
    return (
      <div className="g-panel empty-state">
        <p className="text-muted text-sm">{t("noKeysYet")}</p>
        <p className="text-muted text-11">
          {t("noKeysHint")}
        </p>
      </div>
    );
  }

  return (
    <div className="keys-panel g-panel">
      <table className="g-table">
        <thead>
          <tr>
            <th>{tc("colName")}</th>
            <th>{t("colPrefix")}</th>
            <th>{tc("colStatus")}</th>
            <th>{t("colLastUsed")}</th>
            <th>{t("colExpires")}</th>
            <th>{t("colCreated")}</th>
            <th>{tc("actions")}</th>
          </tr>
        </thead>
        <tbody>
          {keys.map((key) => (
            <tr key={key.id} className={!key.is_active ? "row-inactive" : ""}>
              <td className="font-mono text-sm">{key.name}</td>
              <td className="font-mono text-11 text-muted">oktor_{key.key_prefix}…</td>
              <td>
                <span className={`g-status-dot ${key.is_active ? "g-status-dot--active" : "g-status-dot--inactive"}`}>
                  {key.is_active ? t("active") : t("revoked")}
                </span>
              </td>
              <td className="text-11 text-muted">
                {key.last_used_at ? formatDateTime(key.last_used_at) : t("never")}
              </td>
              <td className="text-11 text-muted">
                {key.expires_at ? formatDateTime(key.expires_at) : t("never")}
              </td>
              <td className="font-mono text-11 text-muted">
                {formatDateTime(key.created_at)}
              </td>
              <td>
                {key.is_active && (
                  <Button
                    variant="danger"
                    icon
                    onClick={() => {
                      if (confirm(t("revokeConfirm"))) {
                        onRevoke(key.id);
                      }
                    }}
                    disabled={isPending}
                    tooltip={t("revokeKeyTooltip")}
                    leftIcon={<Trash2 size={13} />}
                  />
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
