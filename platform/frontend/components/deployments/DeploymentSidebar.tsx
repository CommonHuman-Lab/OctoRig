"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Clock, ExternalLink, Flag, Globe, Lock, Users } from "lucide-react";
import { useTranslations } from "next-intl";
import { CopyButton } from "@/components/ui/CopyButton";
import { type Deployment } from "@/lib/api/deployments";
import { type LabTemplate } from "@/lib/api/labs";
import { formatDateTime } from "@/lib/utils/date";

type Visibility = "private" | "team" | "public";

const VIS_ICON: Record<Visibility, React.ReactNode> = {
  private: <Lock size={11} />,
  team: <Users size={11} />,
  public: <Globe size={11} />,
};

const VIS_LABEL_KEY: Record<Visibility, string> = {
  private: "visPrivate",
  team: "visTeam",
  public: "visPublic",
};

function MetaRow({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="dd-meta-row">
      <span className="dd-meta-label">{label}</span>
      <span className={`dd-meta-value${mono ? " font-mono" : ""}`}>{value}</span>
    </div>
  );
}

interface DeploymentSidebarProps {
  deployment: Deployment;
  lab: LabTemplate | undefined;
  isActive: boolean;
  vis: Visibility;
  countdown: string;
  countdownMs: number;
  onVisibilityChange: (v: Visibility) => void;
  isChangingVisibility: boolean;
}

export function DeploymentSidebar({
  deployment,
  lab,
  isActive,
  vis,
  countdown,
  countdownMs,
  onVisibilityChange,
  isChangingVisibility,
}: DeploymentSidebarProps) {
  const t = useTranslations("deployments");
  const tev = useTranslations("events");
  return (
    <div className="dd-sidebar">
      {isActive && (deployment.access_info.length > 0 || (lab && lab.access_info.length > 0)) && (
        <div className="g-card dd-card">
          <div className="dd-section-title">{t("accessHeading")}</div>
          <div className="dd-access-rows">
            {(deployment.access_info.length > 0 ? deployment.access_info : lab!.access_info).map((row) => (
              <div key={row.key} className="dd-access-row">
                <span className="dd-access-key">{row.key}</span>
                <span className="dd-access-val font-mono">{row.value}</span>
                <CopyButton value={row.value} />
                {row.value.startsWith("http") && (
                  <a href={row.value} target="_blank" rel="noopener noreferrer" className="dd-access-link">
                    <ExternalLink size={11} />
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {deployment.dynamic_flag && (
        <div className="g-card dd-card">
          <div className="dd-section-title" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span><Flag size={11} /> {t("flagHeading")}</span>
            <CopyButton value={deployment.dynamic_flag!} />
          </div>
          <code className="dd-flag">{deployment.dynamic_flag}</code>
        </div>
      )}

      {deployment.auto_destroy_at && countdown && (
        <div className="g-card dd-card">
          <div className="dd-section-title"><Clock size={11} /> {t("autoDestroyHeading")}</div>
          <div
            className="dd-countdown"
            style={{
              color: countdownMs <= 15 * 60_000
                ? "var(--g-danger)"
                : countdownMs <= 60 * 60_000
                ? "var(--g-warning)"
                : undefined,
            }}
          >
            {countdown}
          </div>
          <div className="dd-autodestroy-at">{formatDateTime(deployment.auto_destroy_at)}</div>
        </div>
      )}

      <div className="g-card dd-card">
        <div className="dd-section-title">{t("detailsHeading")}</div>
        <div className="dd-meta-rows">
          <MetaRow label={t("colLab")} value={deployment.lab_name} />
          <MetaRow label={t("colCategory")} value={deployment.lab_category} />
          <MetaRow label={t("startedByLabel")} value={deployment.started_by_username} />
          {deployment.team_name && <MetaRow label={t("teamLabel")} value={deployment.team_name} />}
          <MetaRow label={t("startedLabel")} value={formatDateTime(deployment.started_at)} />
          {deployment.stopped_at && (
            <MetaRow label={t("stoppedLabel")} value={formatDateTime(deployment.stopped_at)} />
          )}
          {(deployment.subnet || deployment.app_ip) && (
            <>
              <MetaRow label={t("subnetLabel")} value={deployment.subnet ?? "—"} mono />
              <MetaRow label={t("appIpLabel")} value={deployment.app_ip ?? "—"} mono />
            </>
          )}
          <div className="dd-meta-row">
            <span className="dd-meta-label">{t("containersLabel")}</span>
            <div className="dd-meta-chips">
              {deployment.container_names.map((c) => (
                <span key={c} className="g-tag text-10">{c.split("-").pop()}</span>
              ))}
            </div>
          </div>
          {lab && Object.keys(lab.exposed_ports).length > 0 && (
            <div className="dd-meta-row">
              <span className="dd-meta-label">{t("portsLabel")}</span>
              <div className="dd-meta-chips">
                {Object.entries(lab.exposed_ports).map(([name, port]) => (
                  <span key={name} className="g-tag text-10">{name.toUpperCase()}:{port}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="g-card dd-card">
        <div className="dd-section-title">{tev("visibilityLabel")}</div>
        <div className="dd-vis-pills">
          {(["private", "team", "public"] as Visibility[]).map((v) => {
            const disabled = v === "team" && !deployment.team_id;
            return (
              <button
                key={v}
                className={`dd-vis-pill${vis === v ? " dd-vis-pill--active" : ""}`}
                onClick={() => !disabled && onVisibilityChange(v)}
                disabled={disabled || isChangingVisibility}
                title={disabled ? t("assignTeamFirstTooltip") : undefined}
              >
                {VIS_ICON[v]}
                {t(VIS_LABEL_KEY[v] as any)}
              </button>
            );
          })}
        </div>
      </div>

      {deployment.error_message && (
        <div className="g-card dd-card">
          <div className="dd-section-title">{t("errorHeading")}</div>
          <p className="dd-error-msg font-mono">{deployment.error_message}</p>
        </div>
      )}
    </div>
  );
}
