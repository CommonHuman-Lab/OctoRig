"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./deployments.css";

import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Square, RotateCcw, Play, Trash2, Rocket } from "lucide-react";
import {
  getDeployments, stopDeployment, resetDeployment, restartDeployment, removeDeployment,
} from "@/lib/api/deployments";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { useConfirmStore } from "@/stores/confirm.store";
import { formatDateTime } from "@/lib/utils/date";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { Button } from "@/components/ui/Button";

export default function DeploymentsPage() {
  const router = useRouter();
  const { confirm } = useConfirmStore();

  const { data: deployments = [], isLoading } = useQuery({
    queryKey: ["deployments"],
    queryFn: () => getDeployments(),
  });

  const stopMutation = useApiMutation({
    mutationFn: stopDeployment,
    invalidateKeys: [["deployments"], ["labs"]],
    successMessage: "Lab stop requested",
    errorMessage: "Failed to stop lab",
  });

  const resetMutation = useApiMutation({
    mutationFn: resetDeployment,
    invalidateKeys: [["deployments"], ["labs"]],
    successMessage: "Lab reset requested",
    errorMessage: "Failed to reset lab",
  });

  const startMutation = useApiMutation({
    mutationFn: restartDeployment,
    invalidateKeys: [["deployments"], ["labs"]],
    successMessage: "Lab start requested",
    errorMessage: "Failed to start lab",
  });

  const removeMutation = useApiMutation({
    mutationFn: removeDeployment,
    invalidateKeys: [["deployments"]],
    successMessage: "Deployment removed",
    errorMessage: "Failed to remove deployment",
  });

  function handleRemove(id: number, labName: string) {
    confirm({
      title: "Remove deployment?",
      body: `Permanently remove the "${labName}" deployment record? This cannot be undone.`,
      confirmLabel: "Remove",
      dangerous: true,
      onConfirm: () => removeMutation.mutate(id),
    });
  }

  return (
    <div className="page">
      <h1 className="page-title font-mono">
        <Rocket size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
        Deployments
      </h1>

      <AsyncContent
        isLoading={isLoading}
        data={deployments}
        empty={
          <div className="g-panel empty-state">
            <p className="text-muted text-sm">No deployments yet.</p>
            <Link href="/labs" className="g-btn g-btn-primary mt-2">Start a Lab</Link>
          </div>
        }
      >
        {(deployments) => (
          <table className="g-table">
            <thead>
              <tr>
                <th>Lab</th>
                <th>Category</th>
                <th>Status</th>
                <th>Started By</th>
                <th>Started At</th>
                <th>Stopped At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {deployments.map((d) => {
                const canStop = d.status === "running" || d.status === "starting";
                const canReset = d.status === "running" && d.lab_category === "firerange";
                const canStart = d.status === "stopped" || d.status === "error";
                const canRemove = d.status === "stopped" || d.status === "error";
                return (
                  <tr
                    key={d.id}
                    className="g-table-row-link"
                    onClick={() => router.push(`/deployments/${d.id}`)}
                  >
                    <td className="text-secondary">{d.lab_name}</td>
                    <td className="text-secondary text-11">{d.lab_category}</td>
                    <td><DeploymentStatusBadge status={d.status} /></td>
                    <td className="text-secondary">{d.started_by_username}</td>
                    <td className="font-mono text-11 text-secondary">
                      {formatDateTime(d.started_at)}
                    </td>
                    <td className="font-mono text-11 text-muted">
                      {formatDateTime(d.stopped_at)}
                    </td>
                    <td onClick={(e) => e.stopPropagation()}>
                      <div className="flex gap-1">
                        {canStop && (
                          <Button
                            variant="danger"
                            icon
                            leftIcon={<Square size={13} />}
                            onClick={() => stopMutation.mutate(d.id)}
                            disabled={stopMutation.isPending || d.status === "stopping"}
                            tooltip="Stop lab"
                          />
                        )}
                        {canReset && (
                          <Button
                            icon
                            leftIcon={<RotateCcw size={13} />}
                            onClick={() => resetMutation.mutate(d.id)}
                            disabled={resetMutation.isPending}
                            tooltip="Reset scoreboard"
                          />
                        )}
                        {canStart && (
                          <Button
                            variant="primary"
                            icon
                            leftIcon={<Play size={13} />}
                            onClick={() => startMutation.mutate(d.id)}
                            disabled={startMutation.isPending}
                            tooltip="Start lab"
                          />
                        )}
                        {canRemove && (
                          <Button
                            variant="danger"
                            icon
                            leftIcon={<Trash2 size={13} />}
                            onClick={() => handleRemove(d.id, d.lab_name)}
                            disabled={removeMutation.isPending}
                            tooltip="Remove deployment"
                          />
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
  );
}
