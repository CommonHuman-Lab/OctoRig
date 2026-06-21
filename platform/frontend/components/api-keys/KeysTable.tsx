// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Trash2 } from "lucide-react";
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
  if (keys.length === 0) {
    return (
      <div className="g-panel empty-state">
        <p className="text-muted text-sm">No API keys yet.</p>
        <p className="text-muted text-11">
          Create a key to authenticate via CLI, CI/CD pipelines, or external integrations.
        </p>
      </div>
    );
  }

  return (
    <div className="keys-panel g-panel">
      <table className="g-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Prefix</th>
            <th>Status</th>
            <th>Last Used</th>
            <th>Expires</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {keys.map((key) => (
            <tr key={key.id} className={!key.is_active ? "row-inactive" : ""}>
              <td className="font-mono text-sm">{key.name}</td>
              <td className="font-mono text-11 text-muted">oktor_{key.key_prefix}…</td>
              <td>
                <span className={`g-status-dot ${key.is_active ? "g-status-dot--active" : "g-status-dot--inactive"}`}>
                  {key.is_active ? "Active" : "Revoked"}
                </span>
              </td>
              <td className="text-11 text-muted">
                {key.last_used_at ? formatDateTime(key.last_used_at) : "Never"}
              </td>
              <td className="text-11 text-muted">
                {key.expires_at ? formatDateTime(key.expires_at) : "Never"}
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
                      if (confirm("Revoke this API key? This cannot be undone.")) {
                        onRevoke(key.id);
                      }
                    }}
                    disabled={isPending}
                    tooltip="Revoke key"
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
