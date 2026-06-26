"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
import { useTranslations } from "next-intl";
import { Lightbulb, Eye, EyeOff } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { unlockHint, type HintSummary } from "@/lib/api/challenges";
import { useNotificationsStore } from "@/stores/notifications.store";
import { Button } from "@/components/ui/Button";

interface HintCardProps {
  hint: HintSummary;
  slug: string;
  userPoints: number;
  onUnlocked: (hintId: number, content: string) => void;
}

export function HintCard({ hint, slug, userPoints, onUnlocked }: HintCardProps) {
  const t = useTranslations("challenges.detail");
  const tCommon = useTranslations("common");
  const [visible, setVisible] = useState(false);
  const { push } = useNotificationsStore();
  const canAfford = hint.cost === 0 || userPoints >= hint.cost;

  const unlockMutation = useMutation({
    mutationFn: () => unlockHint(slug, hint.id),
    onSuccess: (res) => {
      onUnlocked(res.hint_id, res.content);
      setVisible(true);
      if (res.cost > 0) push("info", t("toastHintCostSpent", { cost: res.cost }));
    },
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail;
      push("error", detail ?? t("toastUnlockHintFailed"));
    },
  });

  if (!hint.unlocked && hint.content === null) {
    return (
      <div className="hint-card hint-locked">
        <div className="hint-header">
          <Lightbulb size={13} className="hint-icon" />
          <span className="hint-label">{t("hintLabel", { n: hint.order_num })}</span>
          {hint.cost > 0 && (
            <span className="hint-cost" style={{ color: canAfford ? undefined : "var(--g-danger)" }}>
              {tCommon("points", { count: hint.cost })}
            </span>
          )}
        </div>
        <Button
          variant="ghost"
          className="hint-unlock-btn"
          onClick={() => unlockMutation.mutate()}
          disabled={unlockMutation.isPending || !canAfford}
          tooltip={!canAfford ? t("notEnoughPtsTooltip", { cost: hint.cost, have: userPoints }) : undefined}
        >
          {unlockMutation.isPending
            ? t("unlockingBtn")
            : !canAfford
            ? t("notEnoughPtsBtn")
            : hint.cost > 0
            ? t("unlockWithCostBtn", { cost: hint.cost })
            : t("unlockBtn")}
        </Button>
      </div>
    );
  }

  const content = hint.content!;
  return (
    <div className="hint-card hint-unlocked">
      <div className="hint-header">
        <Lightbulb size={13} className="hint-icon hint-icon--unlocked" />
        <span className="hint-label">{t("hintLabel", { n: hint.order_num })}</span>
        {hint.cost > 0 && <span className="hint-cost hint-cost--paid">−{hint.cost} pts</span>}
        <button
          className="hint-toggle"
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? t("hideHintLabel") : t("showHintLabel")}
        >
          {visible ? <EyeOff size={12} /> : <Eye size={12} />}
        </button>
      </div>
      {visible && <p className="hint-content">{content}</p>}
    </div>
  );
}
