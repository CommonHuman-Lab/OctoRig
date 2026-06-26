"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { useTranslations } from "next-intl";
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
  const t = useTranslations("admin.deployments");
  const tDeployments = useTranslations("deployments");
  const tCommon = useTranslations("common");
  const VISIBILITY_LABEL: Record<string, string> = {
    private: tDeployments("visPrivate"),
    team: tDeployments("visTeam"),
    public: tDeployments("visPublic"),
  };
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
    successMessage: t("toastDeploymentStopped"),
    errorMessage: t("toastStopFailed"),
  });

  const resetMutation = useApiMutation({
    mutationFn: resetDeployment,
    invalidateKeys: [["admin-deployments"]],
    successMessage: t("toastDeploymentReset"),
    errorMessage: t("toastResetFailed"),
  });

  function handleDestroy(d: AdminDeployment) {
    confirm({
      title: t("destroyTitle"),
      body: t("destroyBody", { lab: d.lab_name, username: d.started_by_username }),
      confirmLabel: t("destroyConfirm"),
      dangerous: true,
      onConfirm: () => destroyMutation.mutate(d.id),
    });
  }

  function handleReset(d: AdminDeployment) {
    confirm({
      title: t("resetTitle"),
      body: t("resetBody", { lab: d.lab_name, username: d.started_by_username }),
      confirmLabel: tDeployments("reset"),
      onConfirm: () => resetMutation.mutate(d.id),
    });
  }

  const startMutation = useApiMutation({
    mutationFn: restartDeployment,
    invalidateKeys: [["admin-deployments"]],
    successMessage: t("toastStartRequested"),
    errorMessage: t("toastStartFailed"),
  });

  const removeMutation = useApiMutation({
    mutationFn: removeDeployment,
    invalidateKeys: [["admin-deployments"]],
    successMessage: tDeployments("removedToast"),
    errorMessage: tDeployments("removeFailed"),
  });

  function handleRemove(d: AdminDeployment) {
    confirm({
      title: tDeployments("removeConfirmTitle"),
      body: t("removeBody", { lab: d.lab_name, username: d.started_by_username }),
      confirmLabel: tDeployments("removeLabel"),
      dangerous: true,
      onConfirm: () => removeMutation.mutate(d.id),
    });
  }

  const stopAllMutation = useApiMutation<void, void>({
    mutationFn: stopAllDeployments,
    invalidateKeys: [["admin-deployments"]],
    successMessage: t("toastStopAllRequested"),
    errorMessage: t("toastStopAllFailed"),
  });

  function handleStopAll() {
    const activeCount = deployments.filter((d) => ACTIVE_STATUSES.has(d.status)).length;
    confirm({
      title: t("stopAllTitle"),
      body: t("stopAllBody", { count: activeCount }),
      confirmLabel: t("stopAllBtn"),
      dangerous: true,
      onConfirm: () => stopAllMutation.mutate(),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">{t("title")}</h1>
        <SearchBar value={search} onChange={setSearch} placeholder={t("filterPlaceholder")} />
        {deployments.some((d) => ACTIVE_STATUSES.has(d.status)) && (
          <Button
            variant="danger"
            size="sm"
            leftIcon={<StopCircle size={14} />}
            disabled={stopAllMutation.isPending}
            onClick={handleStopAll}
          >
            {stopAllMutation.isPending ? t("stoppingBtn") : t("stopAllBtn")}
          </Button>
        )}
      </div>

      <div className="g-panel">
        <AsyncContent
          isLoading={isLoading}
          data={deployments}
          empty={<EmptyCell label={t("noDeploymentsFound")} />}
        >
          {(deployments) => (
            <table className="g-table">
              <thead>
                <tr>
                  <th>{tDeployments("colLab")}</th>
                  <th>{tCommon("colUser")}</th>
                  <th>{tCommon("colTeam")}</th>
                  <th>{tCommon("colVisibility")}</th>
                  <th>{tCommon("colStatus")}</th>
                  <th>{tDeployments("startedLabel")}</th>
                  <th>{tDeployments("stoppedLabel")}</th>
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
                          {VISIBILITY_LABEL[d.visibility ?? "private"]}
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
                                tooltip={tDeployments("reset")}
                                leftIcon={<RefreshCw size={12} />}
                                disabled={resetMutation.isPending}
                                onClick={() => handleReset(d)}
                              />
                              <Button
                                variant="danger"
                                size="sm"
                                tooltip={t("destroyTooltip")}
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
                                tooltip={tDeployments("start")}
                                leftIcon={<Play size={12} />}
                                disabled={startMutation.isPending}
                                onClick={() => startMutation.mutate(d.id)}
                              />
                              <Button
                                variant="danger"
                                size="sm"
                                tooltip={tDeployments("removeLabel")}
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
