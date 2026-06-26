"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useTranslations } from "next-intl";
import { CheckCircle2, XCircle, Zap } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function SubmitForm({
  codeSnippet,
  flag,
  onFlagChange,
  onSubmit,
  isLoading,
  submitResult,
  cooldownRemaining,
}: {
  codeSnippet?: string;
  flag: string;
  onFlagChange: (v: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
  submitResult: { correct: boolean; message: string; firstBlood: boolean; points: number } | null;
  cooldownRemaining: number;
}) {
  const t = useTranslations("challenges.detail");
  const tAssessment = useTranslations("assessment");
  const tCreator = useTranslations("creator");
  const tProfile = useTranslations("profile");
  const btnLabel = isLoading
    ? t("checkingBtn")
    : cooldownRemaining > 0
    ? t("tryAgainInBtn", { s: cooldownRemaining })
    : tAssessment("submit");

  return (
    <form onSubmit={onSubmit} className="submit-form">
      <div className={codeSnippet ? undefined : "submit-row"}>
        {codeSnippet ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            <textarea
              className="g-input font-mono"
              placeholder={t("answerPlaceholder")}
              rows={3}
              value={flag}
              onChange={(e) => onFlagChange(e.target.value)}
              disabled={isLoading}
              spellCheck={false}
              autoComplete="off"
              style={{ resize: "vertical" }}
            />
            <Button
              type="submit"
              variant="primary"
              style={{ alignSelf: "flex-end" }}
              disabled={isLoading || !flag.trim() || cooldownRemaining > 0}
            >
              {btnLabel}
            </Button>
          </div>
        ) : (
          <input
            className="g-input submit-input font-mono"
            placeholder={tCreator("flagValuePlaceholderFlag")}
            value={flag}
            onChange={(e) => onFlagChange(e.target.value)}
            disabled={isLoading || cooldownRemaining > 0}
            spellCheck={false}
            autoComplete="off"
          />
        )}
        {!codeSnippet && (
          <Button
            type="submit"
            variant="primary"
            disabled={isLoading || !flag.trim() || cooldownRemaining > 0}
          >
            {btnLabel}
          </Button>
        )}
      </div>

      {submitResult && (
        <div className={`submit-feedback ${submitResult.correct ? "fb-correct" : "fb-wrong"}`}>
          {submitResult.correct ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
          <span>{submitResult.message}</span>
          {submitResult.firstBlood && (
            <span className="fb-firstblood">
              <Zap size={12} /> {tProfile("firstBloodLabel")}
            </span>
          )}
        </div>
      )}
    </form>
  );
}
