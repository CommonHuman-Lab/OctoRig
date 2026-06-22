"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useEffect, useRef } from "react";
import { getDeployment } from "@/lib/api/deployments";
import { usePendingLabsStore } from "@/stores/pending-labs.store";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useQueryClient } from "@tanstack/react-query";
import { TIMING } from "@/lib/config";

export function LabPoller() {
  const { pending, remove } = usePendingLabsStore();
  const { update } = useNotificationsStore();
  const qc = useQueryClient();
  const activeRef = useRef<Set<number>>(new Set());

  useEffect(() => {
    for (const lab of pending) {
      if (activeRef.current.has(lab.deploymentId)) continue;
      activeRef.current.add(lab.deploymentId);

      const interval = setInterval(async () => {
        try {
          const d = await getDeployment(lab.deploymentId);
          if (d.status === "running") {
            clearInterval(interval);
            activeRef.current.delete(lab.deploymentId);
            remove(lab.deploymentId);
            update(lab.toastId, "success", `${lab.labName} is running`);
            qc.invalidateQueries({ queryKey: ["labs"] });
            qc.invalidateQueries({ queryKey: ["deployments"] });
          } else if (d.status === "error") {
            clearInterval(interval);
            activeRef.current.delete(lab.deploymentId);
            remove(lab.deploymentId);
            update(lab.toastId, "error", `Failed to start ${lab.labName}`);
          }
        } catch {
          // transient network error — keep polling
        }
      }, TIMING.LAB_POLL_INTERVAL_MS);
    }
  }, [pending, remove, update, qc]);

  return null;
}
