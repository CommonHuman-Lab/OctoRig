"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./deployments.css";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useApiMutation } from "@/hooks/useApiMutation";
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
  const t = useTranslations("deployments");
  const tn = useTranslations("nav");
  const tl = useTranslations("labs");
  const tc = useTranslations("common");
  const router = useRouter();
  const { confirm } = useConfirmStore();

  const { data: deployments = [], isLoading } = useQuery({
    queryKey: ["deployments"],
    queryFn: () => getDeployments(),
  });

  const stopMutation = useApiMutation({
    mutationFn: stopDeployment,
    invalidateKeys: [["deployments"], ["labs"]],
    successMessage: tl("stopRequested"),
    errorMessage: tl("stopFailed"),
  });

  const resetMutation = useApiMutation({
    mutationFn: resetDeployment,
    invalidateKeys: [["deployments"], ["labs"]],
    successMessage: tl("resetRequested"),
    errorMessage: tl("resetFailed"),
  });

  const startMutation = useApiMutation({
    mutationFn: restartDeployment,
    invalidateKeys: [["deployments"], ["labs"]],
    successMessage: t("startRequested"),
    errorMessage: t("startFailed"),
  });

  const removeMutation = useApiMutation({
    mutationFn: removeDeployment,
    invalidateKeys: [["deployments"]],
    successMessage: t("removedToast"),
    errorMessage: t("removeFailed"),
  });

  function handleRemove(id: number, labName: string) {
    confirm({
      title: t("removeConfirmTitle"),
      body: t("removeConfirmBody", { name: labName }),
      confirmLabel: t("removeLabel"),
      dangerous: true,
      onConfirm: () => removeMutation.mutate(id),
    });
  }

  return (
    <div className="page">
      <h1 className="page-title font-mono">
        <Rocket size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
        {tn("deployments")}
      </h1>

      <AsyncContent
        isLoading={isLoading}
        data={deployments}
        empty={
          <div className="g-panel empty-state">
            <p className="text-muted text-sm">{t("noDeployments")}</p>
            <Button href="/labs" variant="primary" className="mt-2">{t("startALab")}</Button>
          </div>
        }
      >
        {(deployments) => (
          <table className="g-table">
            <thead>
              <tr>
                <th>{t("colLab")}</th>
                <th>{tc("colCategory")}</th>
                <th>{tc("colStatus")}</th>
                <th>{t("colStartedBy")}</th>
                <th>{t("colStartedAt")}</th>
                <th>{t("colStoppedAt")}</th>
                <th>{tc("actions")}</th>
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
                            tooltip={t("stopLabTooltip")}
                          />
                        )}
                        {canReset && (
                          <Button
                            icon
                            leftIcon={<RotateCcw size={13} />}
                            onClick={() => resetMutation.mutate(d.id)}
                            disabled={resetMutation.isPending}
                            tooltip={t("resetScoreboardTooltip")}
                          />
                        )}
                        {canStart && (
                          <Button
                            variant="primary"
                            icon
                            leftIcon={<Play size={13} />}
                            onClick={() => startMutation.mutate(d.id)}
                            disabled={startMutation.isPending}
                            tooltip={t("startLabTooltip")}
                          />
                        )}
                        {canRemove && (
                          <Button
                            variant="danger"
                            icon
                            leftIcon={<Trash2 size={13} />}
                            onClick={() => handleRemove(d.id, d.lab_name)}
                            disabled={removeMutation.isPending}
                            tooltip={t("removeDeploymentTooltip")}
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
