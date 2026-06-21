// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { clsx } from "clsx";

type Status = "starting" | "running" | "stopping" | "stopped" | "error";

const LABEL: Record<Status, string> = {
  starting: "Starting",
  running: "Running",
  stopping: "Stopping",
  stopped: "Stopped",
  error: "Error",
};

const VAR: Record<Status, string> = {
  starting: "var(--g-lab-starting)",
  running: "var(--g-lab-running)",
  stopping: "var(--g-lab-stopping)",
  stopped: "var(--g-lab-stopped)",
  error: "var(--g-lab-error)",
};

export function DeploymentStatusBadge({ status }: { status: string }) {
  const s = status as Status;
  return (
    <span
      className="g-badge"
      style={{ color: VAR[s] ?? "var(--g-text-muted)", borderColor: VAR[s] ?? "var(--g-border)" }}
    >
      {s === "starting" || s === "stopping" ? (
        <span className="g-dot animate-pulse" style={{ background: VAR[s] }} />
      ) : null}
      {LABEL[s] ?? status}
    </span>
  );
}
