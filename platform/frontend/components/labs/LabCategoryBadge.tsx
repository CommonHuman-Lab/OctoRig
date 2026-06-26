// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useTranslations } from "next-intl";

const COLORS: Record<string, string> = {
  world: "var(--g-sky)",
  firerange: "var(--g-orange)",
  thirdparty: "var(--g-zinc)",
};

export function LabCategoryBadge({ category }: { category: string }) {
  const t = useTranslations("labs");
  const LABELS: Record<string, string> = {
    world: t("categoryWorld"),
    firerange: t("categoryFirerange"),
    thirdparty: t("categoryThirdparty"),
  };
  return (
    <span
      className="g-badge"
      style={{ color: COLORS[category] ?? "var(--g-text-muted)", borderColor: COLORS[category] ?? "var(--g-border)" }}
    >
      {LABELS[category] ?? category}
    </span>
  );
}
