"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./api-keys.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Plus, KeyRound } from "lucide-react";
import { getApiKeys, createApiKey, revokeApiKey, type ApiKeyCreated } from "@/lib/api/apiKeys";
import { KeyReveal } from "@/components/api-keys/KeyReveal";
import { CreateKeyForm } from "@/components/api-keys/CreateKeyForm";
import { KeysTable } from "@/components/api-keys/KeysTable";
import { Button } from "@/components/ui/Button";

export default function ApiKeysPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [createdKey, setCreatedKey] = useState<ApiKeyCreated | null>(null);

  const { data: keys = [], isLoading } = useQuery({
    queryKey: ["api-keys"],
    queryFn: getApiKeys,
  });

  const createMutation = useApiMutation({
    mutationFn: (payload: { name: string; expires_at: string | null }) =>
      createApiKey(payload),
    invalidateKeys: [["api-keys"]],
    errorMessage: (err: any) => err?.response?.data?.detail ?? "Failed to create key",
    onSuccess: (key) => {
      setCreatedKey(key);
      setShowCreate(false);
    },
  });

  const revokeMutation = useApiMutation({
    mutationFn: revokeApiKey,
    invalidateKeys: [["api-keys"]],
    successMessage: "API key revoked",
    errorMessage: "Failed to revoke key",
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">
          <KeyRound size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
          API Keys
        </h1>
        <Button
          variant="primary"
          leftIcon={<Plus size={14} />}
          onClick={() => { setShowCreate(true); setCreatedKey(null); }}
        >
          New Key
        </Button>
      </div>

      {createdKey && (
        <KeyReveal createdKey={createdKey} onDismiss={() => setCreatedKey(null)} />
      )}

      {showCreate && (
        <CreateKeyForm
          onSubmit={(name, expiry) =>
            createMutation.mutate({ name, expires_at: expiry || null })
          }
          isPending={createMutation.isPending}
          onCancel={() => setShowCreate(false)}
        />
      )}

      {isLoading ? (
        <div className="text-muted text-sm">Loading…</div>
      ) : (
        <KeysTable
          keys={keys}
          onRevoke={(id) => revokeMutation.mutate(id)}
          isPending={revokeMutation.isPending}
        />
      )}
    </div>
  );
}
