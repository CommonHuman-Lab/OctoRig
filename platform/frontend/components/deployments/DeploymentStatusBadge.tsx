// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { clsx } from "clsx";
import { useTranslations } from "next-intl";

type Status = "starting" | "running" | "stopping" | "stopped" | "error";

const LABEL_KEY: Record<Status, string> = {
  starting: "statusStarting",
  running: "running",
  stopping: "statusStopping",
  stopped: "statusStopped",
  error: "statusError",
};

const VAR: Record<Status, string> = {
  starting: "var(--g-lab-starting)",
  running: "var(--g-lab-running)",
  stopping: "var(--g-lab-stopping)",
  stopped: "var(--g-lab-stopped)",
  error: "var(--g-lab-error)",
};

export function DeploymentStatusBadge({ status }: { status: string }) {
  const t = useTranslations("deployments");
  const tc = useTranslations("common");
  const s = status as Status;
  const label = s === "running" ? tc("running") : LABEL_KEY[s] ? t(LABEL_KEY[s] as any) : status;
  return (
    <span
      className="g-badge"
      style={{ color: VAR[s] ?? "var(--g-text-muted)", borderColor: VAR[s] ?? "var(--g-border)" }}
    >
      {s === "starting" || s === "stopping" ? (
        <span className="g-dot animate-pulse" style={{ background: VAR[s] }} />
      ) : null}
      {label}
    </span>
  );
}
