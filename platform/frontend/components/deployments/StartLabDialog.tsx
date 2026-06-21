"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import type { LabTemplate } from "@/lib/api/labs";
import { startDeployment } from "@/lib/api/deployments";
import { getTeams } from "@/lib/api/teams";
import { useNotificationsStore } from "@/stores/notifications.store";
import { usePendingLabsStore } from "@/stores/pending-labs.store";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { IconSpinner } from "@/components/ui/IconSpinner";
import { Button } from "@/components/ui/Button";

interface Props {
  lab: LabTemplate;
  open: boolean;
  onClose: () => void;
}

export function StartLabDialog({ lab, open, onClose }: Props) {
  const [phase, setPhase] = useState<"confirm" | "starting" | "error">("confirm");
  const [errorMsg, setErrorMsg] = useState("");
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
  const [visibility, setVisibility] = useState<"private" | "team" | "public">("private");
  const { pushPersistent } = useNotificationsStore();
  const { add: addPending } = usePendingLabsStore();

  const { data: teams = [] } = useQuery({
    queryKey: ["teams"],
    queryFn: getTeams,
    enabled: open,
  });

  const teamOptions = teams.filter((t) => !t.is_personal);

  useEffect(() => {
    if (!open) {
      setPhase("confirm");
      setErrorMsg("");
      setSelectedTeamId(null);
      setVisibility("private");
    }
  }, [open]);


  async function handleStart() {
    setPhase("starting");
    try {
      const d = await startDeployment(lab.id, {
        team_id: selectedTeamId ?? undefined,
        visibility,
      });
      const toastId = pushPersistent("info", `Starting ${lab.name}…`);
      addPending({ deploymentId: d.id, labName: lab.name, toastId });
      onClose();
    } catch (err: any) {
      setPhase("error");
      setErrorMsg(err.response?.data?.detail ?? "Failed to start lab");
    }
  }

  useEscapeKey(onClose, open);

  if (!open) return null;

  return (
    <div className="g-backdrop" onClick={onClose}>
      <div className="g-modal start-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="g-modal-header">
          <span className="font-mono text-sm">{lab.name}</span>
          <Button icon leftIcon={<X size={16} />} onClick={onClose} />
        </div>

        <div className="g-modal-body">
          {phase === "starting" && (
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <IconSpinner size={18} color="var(--g-accent)" />
              <span className="text-sm text-muted">Submitting…</span>
            </div>
          )}

          {phase === "confirm" && (
            <>
              <p className="text-body text-sm mb-1">{lab.description}</p>
              <p className="text-muted text-11">
                A private subnet and IP will be assigned to this lab when it starts.
              </p>
              {lab.requires_privileged && (
                <p className="text-warning text-11 mt-1">⚠ This lab requires --privileged mode</p>
              )}

              {/* Team + visibility options */}
              <div className="deploy-options">
                {teamOptions.length > 0 && (
                  <div className="option-row">
                    <label className="text-11 text-muted">Deploy to</label>
                    <select
                      className="g-select g-select-sm"
                      value={selectedTeamId ?? ""}
                      onChange={(e) =>
                        setSelectedTeamId(e.target.value ? Number(e.target.value) : null)
                      }
                    >
                      <option value="">Personal</option>
                      {teamOptions.map((t) => (
                        <option key={t.id} value={t.id}>{t.name}</option>
                      ))}
                    </select>
                  </div>
                )}
                <div className="option-row">
                  <label className="text-11 text-muted">Visibility</label>
                  <select
                    className="g-select g-select-sm"
                    value={visibility}
                    onChange={(e) => setVisibility(e.target.value as typeof visibility)}
                  >
                    <option value="private">Private</option>
                    {selectedTeamId && <option value="team">Team</option>}
                    <option value="public">Public (read-only)</option>
                  </select>
                </div>
              </div>
            </>
          )}

          {phase === "error" && (
            <div>
              <p className="text-danger text-sm">Failed to start lab</p>
              <p className="text-muted text-11 mt-1 font-mono">{errorMsg}</p>
            </div>
          )}
        </div>

        <div className="g-modal-footer">
          {phase === "confirm" && (
            <>
              <Button onClick={onClose}>Cancel</Button>
              <Button variant="primary" onClick={handleStart}>
                Start Lab
              </Button>
            </>
          )}
          {phase === "error" && (
            <Button onClick={onClose}>Close</Button>
          )}
        </div>
      </div>

      <style>{`
        .start-dialog { max-width: 480px; width: 100%; }
        .access-info-table { display: flex; flex-direction: column; gap: 0; }
        .access-row { display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: 0.6rem 0; border-bottom: 1px solid var(--g-border); }
        .access-row:last-child { border-bottom: none; }
        .deploy-options { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--g-border); }
        .option-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
        .flex { display: flex; }
        .items-center { align-items: center; }
        .gap-2 { gap: 0.5rem; }
        .gap-3 { gap: 0.75rem; }
        .mb-3 { margin-bottom: 0.75rem; }
        .mb-4 { margin-bottom: 1rem; }
        .mt-1 { margin-top: 0.25rem; }
        .mb-1 { margin-bottom: 0.25rem; }
        .text-success { color: var(--g-success); }
        .text-danger { color: var(--g-danger); }
        .text-warning { color: var(--g-warning); }
        .text-accent { color: var(--g-accent); }
      `}</style>
    </div>
  );
}
