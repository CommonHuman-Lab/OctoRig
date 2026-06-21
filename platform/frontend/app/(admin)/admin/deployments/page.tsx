"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { useRouter } from "next/navigation";
import { Trash2, RefreshCw, StopCircle, Play, X } from "lucide-react";
import { SearchBar } from "@/components/ui/SearchBar";
import { getAdminDeployments, stopAllDeployments, type AdminDeployment } from "@/lib/api/admin";
import { stopDeployment, resetDeployment, restartDeployment, removeDeployment } from "@/lib/api/deployments";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { EmptyCell } from "@/components/ui/TableStates";
import { useConfirmStore } from "@/stores/confirm.store";
import { formatDateTime } from "@/lib/utils/date";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { Button } from "@/components/ui/Button";

const ACTIVE_STATUSES = new Set(["starting", "running", "error"]);
const STOPPABLE_STATUSES = new Set(["stopped", "error"]);
const VISIBILITY_BADGE: Record<string, string> = {
  private: "g-badge--muted",
  team: "g-badge--accent",
  public: "g-badge--success",
};

export default function AdminDeploymentsPage() {
  const [search, setSearch] = useState("");
  const { confirm } = useConfirmStore();
  const router = useRouter();

  const { data: deployments = [], isLoading } = useQuery<AdminDeployment[]>({
    queryKey: ["admin-deployments", search],
    queryFn: () => getAdminDeployments({ search: search || undefined }),
  });

  const destroyMutation = useApiMutation({
    mutationFn: stopDeployment,
    invalidateKeys: [["admin-deployments"]],
    successMessage: "Deployment stopped",
    errorMessage: "Failed to stop deployment",
  });

  const resetMutation = useApiMutation({
    mutationFn: resetDeployment,
    invalidateKeys: [["admin-deployments"]],
    successMessage: "Deployment reset",
    errorMessage: "Failed to reset deployment",
  });

  function handleDestroy(d: AdminDeployment) {
    confirm({
      title: "Destroy deployment?",
      body: `Stop and destroy the "${d.lab_name}" lab for ${d.started_by_username}? The container will be removed.`,
      confirmLabel: "Destroy",
      dangerous: true,
      onConfirm: () => destroyMutation.mutate(d.id),
    });
  }

  function handleReset(d: AdminDeployment) {
    confirm({
      title: "Reset deployment?",
      body: `Reset the "${d.lab_name}" lab for ${d.started_by_username}? The container will restart with a fresh state.`,
      confirmLabel: "Reset",
      onConfirm: () => resetMutation.mutate(d.id),
    });
  }

  const startMutation = useApiMutation({
    mutationFn: restartDeployment,
    invalidateKeys: [["admin-deployments"]],
    successMessage: "Deployment start requested",
    errorMessage: "Failed to start deployment",
  });

  const removeMutation = useApiMutation({
    mutationFn: removeDeployment,
    invalidateKeys: [["admin-deployments"]],
    successMessage: "Deployment removed",
    errorMessage: "Failed to remove deployment",
  });

  function handleRemove(d: AdminDeployment) {
    confirm({
      title: "Remove deployment?",
      body: `Permanently remove the "${d.lab_name}" deployment record for ${d.started_by_username}? This cannot be undone.`,
      confirmLabel: "Remove",
      dangerous: true,
      onConfirm: () => removeMutation.mutate(d.id),
    });
  }

  const stopAllMutation = useApiMutation<void, void>({
    mutationFn: stopAllDeployments,
    invalidateKeys: [["admin-deployments"]],
    successMessage: "All labs are being stopped",
    errorMessage: "Failed to stop all deployments",
  });

  function handleStopAll() {
    const activeCount = deployments.filter((d) => ACTIVE_STATUSES.has(d.status)).length;
    confirm({
      title: "Stop all labs?",
      body: `This will stop all ${activeCount} running or starting deployment${activeCount !== 1 ? "s" : ""} across every user. This cannot be undone.`,
      confirmLabel: "Stop All",
      dangerous: true,
      onConfirm: () => stopAllMutation.mutate(),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">All Deployments</h1>
        <SearchBar value={search} onChange={setSearch} placeholder="Filter by user or lab…" />
        {deployments.some((d) => ACTIVE_STATUSES.has(d.status)) && (
          <Button
            variant="danger"
            size="sm"
            leftIcon={<StopCircle size={14} />}
            disabled={stopAllMutation.isPending}
            onClick={handleStopAll}
          >
            {stopAllMutation.isPending ? "Stopping…" : "Stop All"}
          </Button>
        )}
      </div>

      <div className="g-panel">
        <AsyncContent
          isLoading={isLoading}
          data={deployments}
          empty={<EmptyCell label="No deployments." />}
        >
          {(deployments) => (
            <table className="g-table">
              <thead>
                <tr>
                  <th>Lab</th>
                  <th>User</th>
                  <th>Team</th>
                  <th>Visibility</th>
                  <th>Status</th>
                  <th>Started</th>
                  <th>Stopped</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {deployments.map((d) => {
                  const isActive = ACTIVE_STATUSES.has(d.status);
                  const isStoppable = STOPPABLE_STATUSES.has(d.status);
                  return (
                    <tr
                      key={d.id}
                      className="g-table-row-link"
                      onClick={() => router.push(`/deployments/${d.id}`)}
                    >
                      <td className="font-mono text-sm">{d.lab_name}</td>
                      <td className="text-11 text-secondary">{d.started_by_username}</td>
                      <td className="text-11 text-muted">{d.team_name ?? "—"}</td>
                      <td>
                        <span className={`g-badge ${VISIBILITY_BADGE[d.visibility ?? "private"]}`}>
                          {d.visibility ?? "private"}
                        </span>
                      </td>
                      <td>
                        <DeploymentStatusBadge status={d.status} />
                      </td>
                      <td className="font-mono text-11 text-muted">
                        {formatDateTime(d.started_at)}
                      </td>
                      <td className="font-mono text-11 text-muted">
                        {formatDateTime(d.stopped_at)}
                      </td>
                      <td onClick={(e) => e.stopPropagation()}>
                        <div style={{ display: "flex", gap: 4 }}>
                          {isActive && (
                            <>
                              <Button
                                size="sm"
                                tooltip="Reset"
                                leftIcon={<RefreshCw size={12} />}
                                disabled={resetMutation.isPending}
                                onClick={() => handleReset(d)}
                              />
                              <Button
                                variant="danger"
                                size="sm"
                                tooltip="Destroy"
                                leftIcon={<Trash2 size={12} />}
                                disabled={destroyMutation.isPending}
                                onClick={() => handleDestroy(d)}
                              />
                            </>
                          )}
                          {isStoppable && (
                            <>
                              <Button
                                variant="primary"
                                size="sm"
                                tooltip="Start"
                                leftIcon={<Play size={12} />}
                                disabled={startMutation.isPending}
                                onClick={() => startMutation.mutate(d.id)}
                              />
                              <Button
                                variant="danger"
                                size="sm"
                                tooltip="Remove"
                                leftIcon={<X size={12} />}
                                disabled={removeMutation.isPending}
                                onClick={() => handleRemove(d)}
                              />
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </AsyncContent>
      </div>
    </div>
  );
}
