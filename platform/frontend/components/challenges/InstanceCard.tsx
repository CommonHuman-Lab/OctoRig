"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { Container, Clock, Trash2, Copy } from "lucide-react";
import { type Deployment } from "@/lib/api/deployments";
import { useCountdown } from "@/hooks/useCountdown";
import { Button } from "@/components/ui/Button";
import { TIMING } from "@/lib/config";

interface InstanceCardProps {
  instance: Deployment;
  onStop: () => void;
  isStopping: boolean;
}

export function InstanceCard({ instance, onStop, isStopping }: InstanceCardProps) {
  const { label: countdown } = useCountdown(instance.auto_destroy_at);
  const [copied, setCopied] = useState(false);

  function copyFlag() {
    if (!instance.dynamic_flag) return;
    navigator.clipboard.writeText(instance.dynamic_flag).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), TIMING.COPY_FEEDBACK_MS);
    });
  }

  const isActive = instance.status === "running" || instance.status === "starting";

  return (
    <div
      className="g-card"
      style={{ borderColor: isActive ? "var(--g-accent)" : "var(--g-border)" }}
    >
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <Container size={14} style={{ color: "var(--g-accent)" }} />
          <span className="text-11 font-mono" style={{ color: "var(--g-text)" }}>
            Instance #{instance.id}
          </span>
          <span
            className="text-9px font-mono uppercase px-1.5 py-0.5 rounded"
            style={{
              background: isActive ? "color-mix(in srgb, var(--g-accent) 15%, transparent)" : "var(--g-surface)",
              color: isActive ? "var(--g-accent)" : "var(--g-text-muted)",
            }}
          >
            {instance.status}
          </span>
        </div>
        <Button
          variant="danger"
          icon
          onClick={onStop}
          disabled={isStopping || instance.status === "stopping"}
          tooltip="Destroy instance"
          leftIcon={<Trash2 size={12} />}
        />
      </div>

      {instance.auto_destroy_at && (
        <div className="flex items-center gap-1.5 mb-2 text-9px font-mono" style={{ color: "var(--g-warning)" }}>
          <Clock size={10} />
          Auto-destroys in {countdown}
        </div>
      )}

      {instance.dynamic_flag && (
        <div className="mt-2">
          <div className="text-9px font-mono uppercase mb-1" style={{ color: "var(--g-text-muted)" }}>
            Dynamic Flag
          </div>
          <div className="flex items-center gap-2">
            <code
              className="flex-1 text-11 font-mono px-2 py-1 rounded truncate"
              style={{ background: "var(--g-surface)", color: "var(--g-success)", border: "1px solid var(--g-border)" }}
            >
              {instance.dynamic_flag}
            </code>
            <Button
              icon
              onClick={copyFlag}
              tooltip="Copy flag"
              style={{ flexShrink: 0 }}
              leftIcon={<Copy size={12} style={{ color: copied ? "var(--g-success)" : undefined }} />}
            />
          </div>
        </div>
      )}
    </div>
  );
}
