"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../deployment-detail.css";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useApiMutation } from "@/hooks/useApiMutation";
import {
  ArrowLeft, CheckCircle2, Clock, ExternalLink,
  Play, RotateCcw, Square, Target, Trash2,
} from "lucide-react";
import Link from "next/link";
import {
  getDeployment,
  removeDeployment,
  resetDeployment,
  restartDeployment,
  setDeploymentVisibility,
  stopDeployment,
  type Deployment,
} from "@/lib/api/deployments";
import { getLabs, type LabTemplate } from "@/lib/api/labs";
import { getChallenges, type ChallengeDifficulty } from "@/lib/api/challenges";
import { createScheduledAction, type ScheduledAction } from "@/lib/api/scheduler";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { DeploymentSidebar } from "@/components/deployments/DeploymentSidebar";
import { ScheduleDestroyModal } from "@/components/deployments/ScheduleDestroyModal";
import { LabCategoryBadge } from "@/components/labs/LabCategoryBadge";
import { LogViewer } from "@/components/deployments/LogViewer";
import { useCountdown } from "@/hooks/useCountdown";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { PageSpinner } from "@/components/ui/Spinner";
import { Button } from "@/components/ui/Button";
import { DIFF_COLOR } from "@/lib/utils/difficulty";
import { addHours } from "@/lib/utils/date";
import { STALE_TIME } from "@/lib/config";

type Visibility = "private" | "team" | "public";

function DiffBadge({ difficulty }: { difficulty: ChallengeDifficulty }) {
  const tc = useTranslations("common");
  return (
    <span className="g-diff-badge" style={{ color: DIFF_COLOR[difficulty] }}>{tc(difficulty)}</span>
  );
}

export default function DeploymentDetailPage() {
  const t = useTranslations("deployments");
  const tn = useTranslations("nav");
  const tl = useTranslations("labs");
  const tch = useTranslations("challenges");
  const tc = useTranslations("common");
  const { id } = useParams<{ id: string }>();
  const deploymentId = Number(id);
  const qc = useQueryClient();
  const router = useRouter();
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();

  const [showSchedule, setShowSchedule] = useState(false);
  const [scheduledAt, setScheduledAt] = useState(() => addHours(2));

  const { data: deployment, isLoading } = useQuery({
    queryKey: ["deployment", deploymentId],
    queryFn: () => getDeployment(deploymentId),
  });

  const { data: labs = [] } = useQuery<LabTemplate[]>({
    queryKey: ["labs"],
    queryFn: () => getLabs(),
    staleTime: STALE_TIME.SHORT,
    enabled: !!deployment,
  });

  const lab = deployment ? labs.find((l) => l.slug === deployment.lab_slug) : undefined;

  const { data: challenges = [] } = useQuery({
    queryKey: ["challenges", { lab_slug: deployment?.lab_slug }],
    queryFn: () => getChallenges({ lab_slug: deployment!.lab_slug }),
    enabled: !!deployment?.lab_slug,
  });

  const stopMutation = useApiMutation<Deployment, void>({
    mutationFn: () => stopDeployment(deploymentId),
    invalidateKeys: [["deployment", deploymentId], ["deployments"], ["labs"]],
    successMessage: tl("stopRequested"),
    errorMessage: tl("stopFailed"),
  });

  const resetMutation = useApiMutation<Deployment, void>({
    mutationFn: () => resetDeployment(deploymentId),
    invalidateKeys: [["deployment", deploymentId]],
    successMessage: tl("resetRequested"),
    errorMessage: tl("resetFailed"),
  });

  const startMutation = useApiMutation<Deployment, void>({
    mutationFn: () => restartDeployment(deploymentId),
    invalidateKeys: [["deployment", deploymentId], ["deployments"], ["labs"]],
    successMessage: t("startRequested"),
    errorMessage: t("startFailed"),
  });

  const removeMutation = useApiMutation<void, void>({
    mutationFn: () => removeDeployment(deploymentId),
    invalidateKeys: [["deployments"]],
    successMessage: t("removedToast"),
    errorMessage: t("removeFailed"),
    onSuccess: () => router.push("/deployments"),
  });

  function handleRemove() {
    if (!deployment) return;
    confirm({
      title: t("removeConfirmTitle"),
      body: t("removeConfirmBody", { name: deployment.lab_name }),
      confirmLabel: t("removeLabel"),
      dangerous: true,
      onConfirm: () => removeMutation.mutate(),
    });
  }

  const visMutation = useMutation({
    mutationFn: (v: Visibility) => setDeploymentVisibility(deploymentId, v),
    onSuccess: (updated) => {
      qc.setQueryData(["deployment", deploymentId], updated);
      push("success", t("visibilitySetToast", { vis: updated.visibility }));
    },
    onError: () => push("error", t("visibilityUpdateFailed")),
  });

  const scheduleMutation = useApiMutation<ScheduledAction, void>({
    mutationFn: () =>
      createScheduledAction({
        action: "destroy",
        deployment_id: deploymentId,
        scheduled_at: new Date(scheduledAt).toISOString(),
      }),
    invalidateKeys: [],
    successMessage: t("destroyScheduledToast"),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("destroyScheduleFailed"),
    onSuccess: () => setShowSchedule(false),
  });

  const { label: countdown, remainingMs: countdownMs } = useCountdown(deployment?.auto_destroy_at ?? null);

  if (isLoading) return <div className="page"><PageSpinner /></div>;
  if (!deployment) return <div className="page text-muted text-sm">{t("notFound")}</div>;

  const isActive = deployment.status === "running" || deployment.status === "starting";
  const canStop = deployment.status === "running" || deployment.status === "error";
  const canReset = deployment.status === "running" && deployment.lab_category === "firerange";
  const canSchedule = deployment.status === "running";
  const canStart = deployment.status === "stopped" || deployment.status === "error";
  const canRemove = deployment.status === "stopped" || deployment.status === "error";
  const vis = (deployment.visibility ?? "private") as Visibility;

  const accessInfo = deployment.access_info.length > 0 ? deployment.access_info : (lab?.access_info ?? []);
  const labUrl = accessInfo.find((a) => a.key === "URL")?.value;

  return (
    <div className="page">
      <Link href="/deployments" className="back-link">
        <ArrowLeft size={14} /> {tn("deployments")}
      </Link>

      <div className="dd-header">
        <div className="dd-title-row">
          <h1 className="dd-title font-mono">{deployment.lab_name}</h1>
          <div className="dd-badges">
            <DeploymentStatusBadge status={deployment.status} />
            <LabCategoryBadge category={deployment.lab_category} />
          </div>
        </div>

        {lab?.description && <p className="dd-desc">{lab.description}</p>}

        <div className="dd-controls">
          {canStop && (
            <Button
              variant="danger"
              leftIcon={<Square size={14} />}
              onClick={() => stopMutation.mutate()}
              disabled={stopMutation.isPending || deployment.status === "stopping"}
            >
              {t("stop")}
            </Button>
          )}
          {canReset && (
            <Button
              leftIcon={<RotateCcw size={14} />}
              onClick={() => resetMutation.mutate()}
              disabled={resetMutation.isPending}
            >
              {t("reset")}
            </Button>
          )}
          {canStart && (
            <Button
              variant="primary"
              leftIcon={<Play size={14} />}
              onClick={() => startMutation.mutate()}
              disabled={startMutation.isPending}
            >
              {t("start")}
            </Button>
          )}
          {canRemove && (
            <Button
              variant="danger"
              leftIcon={<Trash2 size={14} />}
              onClick={handleRemove}
              disabled={removeMutation.isPending}
            >
              {t("removeLabel")}
            </Button>
          )}
          {labUrl && isActive && (
            <Button href={labUrl} leftIcon={<ExternalLink size={14} />}>
              {t("openLab")}
            </Button>
          )}
          {canSchedule && (
            <Button
              size="sm"
              leftIcon={<Clock size={13} />}
              onClick={() => { setShowSchedule(true); setScheduledAt(addHours(2)); }}
            >
              {t("scheduleDestroy")}
            </Button>
          )}
        </div>
      </div>

      <div className="dd-body">
        <div className="dd-logs g-panel">
          <LogViewer
            deploymentId={deploymentId}
            containerNames={deployment.container_names}
          />
        </div>

        <DeploymentSidebar
          deployment={deployment}
          lab={lab}
          isActive={isActive}
          vis={vis}
          countdown={countdown}
          countdownMs={countdownMs}
          onVisibilityChange={(v) => visMutation.mutate(v)}
          isChangingVisibility={visMutation.isPending}
        />
      </div>

      {challenges.length > 0 && (
        <div className="g-card dd-challenges">
          <div className="dd-section-title">
            {tn("challenges")}
            <span className="dd-ch-count">{challenges.length}</span>
          </div>
          <div className="dd-ch-list">
            {challenges.map((ch) => (
              <Link key={ch.id} href={`/challenges/${ch.slug}`} className="dd-ch-row">
                <div className="dd-ch-info">
                  <span className="dd-ch-cat">{ch.category.replace("-", " ")}</span>
                  <span className="dd-ch-title">{ch.title}</span>
                  <div className="dd-ch-tags">
                    {ch.tags.slice(0, 4).map((t) => (
                      <span key={t} className="g-tag text-10">{t}</span>
                    ))}
                  </div>
                </div>
                <div className="dd-ch-right">
                  <DiffBadge difficulty={ch.difficulty} />
                  <span className="dd-ch-pts">{tc("points", { count: ch.points })}</span>
                  <div className="dd-ch-meta">
                    {ch.estimated_minutes && (
                      <span className="dd-ch-meta-item">
                        <Clock size={10} />{ch.estimated_minutes}m
                      </span>
                    )}
                    <span className="dd-ch-meta-item">
                      <Target size={10} />{ch.solve_count}
                    </span>
                    {ch.solved_by_me && (
                      <span className="dd-ch-solved">
                        <CheckCircle2 size={10} />{tch("solvedLabel")}
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {showSchedule && (
        <ScheduleDestroyModal
          labName={deployment.lab_name}
          scheduledAt={scheduledAt}
          onChangeScheduledAt={setScheduledAt}
          onConfirm={() => scheduleMutation.mutate()}
          onClose={() => setShowSchedule(false)}
          isPending={scheduleMutation.isPending}
        />
      )}
    </div>
  );
}
