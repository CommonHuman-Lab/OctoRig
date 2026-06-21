"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useState } from "react";
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
  const [visible, setVisible] = useState(false);
  const { push } = useNotificationsStore();
  const canAfford = hint.cost === 0 || userPoints >= hint.cost;

  const unlockMutation = useMutation({
    mutationFn: () => unlockHint(slug, hint.id),
    onSuccess: (res) => {
      onUnlocked(res.hint_id, res.content);
      setVisible(true);
      if (res.cost > 0) push("info", `-${res.cost} pts spent to unlock hint`);
    },
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail;
      push("error", detail ?? "Failed to unlock hint");
    },
  });

  if (!hint.unlocked && hint.content === null) {
    return (
      <div className="hint-card hint-locked">
        <div className="hint-header">
          <Lightbulb size={13} className="hint-icon" />
          <span className="hint-label">Hint {hint.order_num}</span>
          {hint.cost > 0 && (
            <span className="hint-cost" style={{ color: canAfford ? undefined : "var(--g-danger)" }}>
              {hint.cost} pts
            </span>
          )}
        </div>
        <Button
          variant="ghost"
          className="hint-unlock-btn"
          onClick={() => unlockMutation.mutate()}
          disabled={unlockMutation.isPending || !canAfford}
          tooltip={!canAfford ? `Not enough points (need ${hint.cost}, have ${userPoints})` : undefined}
        >
          {unlockMutation.isPending
            ? "Unlocking…"
            : !canAfford
            ? `Not enough pts`
            : `Unlock${hint.cost > 0 ? ` (−${hint.cost} pts)` : ""}`}
        </Button>
      </div>
    );
  }

  const content = hint.content!;
  return (
    <div className="hint-card hint-unlocked">
      <div className="hint-header">
        <Lightbulb size={13} className="hint-icon hint-icon--unlocked" />
        <span className="hint-label">Hint {hint.order_num}</span>
        {hint.cost > 0 && <span className="hint-cost hint-cost--paid">−{hint.cost} pts</span>}
        <button
          className="hint-toggle"
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? "Hide hint" : "Show hint"}
        >
          {visible ? <EyeOff size={12} /> : <Eye size={12} />}
        </button>
      </div>
      {visible && <p className="hint-content">{content}</p>}
    </div>
  );
}
