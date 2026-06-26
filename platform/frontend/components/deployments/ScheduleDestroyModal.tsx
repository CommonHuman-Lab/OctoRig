"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useTranslations } from "next-intl";
import { addHours } from "@/lib/utils/date";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { Button } from "@/components/ui/Button";

const PRESETS: { label: string; hours: number }[] = [
  { label: "2 h", hours: 2 },
  { label: "24 h", hours: 24 },
  { label: "7 d", hours: 168 },
];

interface ScheduleDestroyModalProps {
  labName: string;
  scheduledAt: string;
  onChangeScheduledAt: (value: string) => void;
  onConfirm: () => void;
  onClose: () => void;
  isPending: boolean;
}

export function ScheduleDestroyModal({
  labName,
  scheduledAt,
  onChangeScheduledAt,
  onConfirm,
  onClose,
  isPending,
}: ScheduleDestroyModalProps) {
  const t = useTranslations("deployments");
  const tc = useTranslations("common");
  useEscapeKey(onClose, true);

  return (
    <div className="g-backdrop" onClick={onClose}>
      <div className="g-modal" onClick={(e) => e.stopPropagation()}>
        <div className="g-modal-header">
          <span className="font-mono text-sm">{t("scheduleModalTitle", { labName })}</span>
        </div>
        <div className="g-modal-body">
          <p className="text-muted text-11" style={{ marginBottom: "0.75rem" }}>
            {t("scheduleModalBody")}
          </p>
          <div className="dd-preset-row">
            {PRESETS.map((p) => (
              <Button
                key={p.label}
                size="sm"
                onClick={() => onChangeScheduledAt(addHours(p.hours))}
              >
                {p.label}
              </Button>
            ))}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            <label className="text-11 text-muted">{t("customTimeLabel")}</label>
            <input
              type="datetime-local"
              className="g-input"
              value={scheduledAt}
              min={addHours(0)}
              onChange={(e) => onChangeScheduledAt(e.target.value)}
            />
          </div>
        </div>
        <div className="g-modal-footer">
          <Button onClick={onClose}>
            {tc("cancel")}
          </Button>
          <Button
            variant="danger"
            onClick={onConfirm}
            disabled={isPending}
          >
            {isPending ? t("scheduling") : t("scheduleDestroy")}
          </Button>
        </div>
      </div>
    </div>
  );
}
