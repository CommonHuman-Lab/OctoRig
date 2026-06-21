"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { getDeployments, stopDeployment } from "@/lib/api/deployments";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { useApiMutation } from "@/hooks/useApiMutation";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { Button } from "@/components/ui/Button";
import { formatRelative } from "@/lib/utils/date";
import type { WidgetComponentProps } from "@/lib/widgets/types";

export function ActiveDeploymentsWidget({ widget }: WidgetComponentProps) {
  const router = useRouter();
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

  const activeDeployments = deployments.filter((d) => d.status !== "stopped");

  return (
    <AsyncContent
      isLoading={isLoading}
      data={activeDeployments}
      empty={
        <div className={`g-panel empty-state dash-panel-h-${widget.height}`}>
          <p className="text-muted text-sm">No active labs.</p>
          <Button href="/labs" variant="primary" className="mt-2">Browse Lab Catalog</Button>
        </div>
      }
    >
      {(rows) => (
        <div className={`g-panel dash-panel-h-${widget.height}`}>
          <div className="g-panel-header">
            <span className="text-secondary text-11 font-mono">Active Deployments</span>
          </div>
          <div className="dash-panel-scroll">
            <table className="g-table">
              <thead>
                <tr>
                  <th>Lab</th>
                  <th>Status</th>
                  <th>Started By</th>
                  <th>Started</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((d) => (
                  <tr key={d.id} onClick={() => router.push(`/deployments/${d.id}`)} style={{ cursor: "pointer" }}>
                    <td><span className="text-accent">{d.lab_name}</span></td>
                    <td><DeploymentStatusBadge status={d.status} /></td>
                    <td className="text-secondary">{d.started_by_username}</td>
                    <td className="text-muted font-mono" style={{ fontSize: "0.6875rem" }}>
                      {formatRelative(d.started_at)}
                    </td>
                    <td>
                      <Button
                        variant="danger"
                        icon
                        leftIcon="■"
                        onClick={(e) => { e.stopPropagation(); stopMutation.mutate(d.id); }}
                        disabled={d.status === "stopping" || stopMutation.isPending}
                        tooltip="Stop lab"
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </AsyncContent>
  );
}
