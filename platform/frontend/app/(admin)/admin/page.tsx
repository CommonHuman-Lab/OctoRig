"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./admin.css";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Users, FolderGit2, Container, KeyRound, Activity, ClipboardList } from "lucide-react";
import { getStats, type SystemStats } from "@/lib/api/admin";
import { getPlugins } from "@/lib/api/system";
import { useUserStore } from "@/stores/user.store";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/Button";

function StatCard({
  icon,
  label,
  value,
  href,
}: {
  icon: React.ReactNode;
  label: string;
  value: number | undefined;
  href: string;
}) {
  return (
    <Link href={href} className="stat-card g-card">
      <div className="stat-icon">{icon}</div>
      <div className="stat-body">
        <span className="stat-value font-mono">
          {value === undefined ? "—" : value.toLocaleString()}
        </span>
        <span className="stat-label text-11 text-muted">{label}</span>
      </div>
    </Link>
  );
}

export default function AdminDashboard() {
  const t = useTranslations("admin");
  const tNav = useTranslations("nav");
  const tCommon = useTranslations("common");
  const { user } = useUserStore();
  const router = useRouter();

  useEffect(() => {
    if (user && !user.permissions?.includes("admin.panel")) {
      router.replace("/");
    }
  }, [user, router]);

  const { data: stats, isLoading } = useQuery<SystemStats>({
    queryKey: ["admin-stats"],
    queryFn: getStats,
  });

  const { data: plugins = [] } = useQuery({
    queryKey: ["admin", "plugins"],
    queryFn: getPlugins,
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">{tNav("adminSection")}</h1>
        {user?.platform_roles?.includes("admin") && (
          <span className="superadmin-badge text-11">{t("superAdmin")}</span>
        )}
      </div>

      {isLoading ? (
        <div className="text-muted text-sm">{tCommon("loading")}</div>
      ) : (
        <div className="g-grid-auto stats-grid">
          <StatCard
            icon={<Users size={20} />}
            label={t("totalUsers")}
            value={stats?.user_count}
            href="/admin/users"
          />
          <StatCard
            icon={<FolderGit2 size={20} />}
            label={t("totalTeams")}
            value={stats?.team_count}
            href="/admin/teams"
          />
          <StatCard
            icon={<Container size={20} />}
            label={t("activeDeployments")}
            value={stats?.active_deployments}
            href="/admin/deployments"
          />
          <StatCard
            icon={<Activity size={20} />}
            label={t("totalDeployments")}
            value={stats?.total_deployments}
            href="/admin/deployments"
          />
          <StatCard
            icon={<KeyRound size={20} />}
            label={tNav("apiKeys")}
            value={stats?.api_key_count}
            href="/admin/users"
          />
          <StatCard
            icon={<ClipboardList size={20} />}
            label={tNav("adminAssessments")}
            value={undefined}
            href="/admin/assessments"
          />
        </div>
      )}

      <div className="quick-links">
        <h2 className="section-title text-11 text-muted">{t("quickLinks")}</h2>
        <div className="link-row">
          <Button href="/admin/users" size="sm">{tNav("adminUsers")}</Button>
          <Button href="/admin/teams" size="sm">{tNav("teams")}</Button>
          <Button href="/admin/deployments" size="sm">{tNav("deployments")}</Button>
          <Button href="/admin/audit" size="sm">{tNav("adminAuditLog")}</Button>
          <Button href="/admin/assessments" size="sm">{tNav("adminAssessments")}</Button>
        </div>
      </div>

      <div className="mt-6">
        <h2 className="section-title text-11 text-muted">{t("plugins")}</h2>
        {plugins.length === 0 ? (
          <p className="text-muted text-sm mt-2">
            {t.rich("noPlugins", { code: (chunks) => <code>{chunks}</code> })}
          </p>
        ) : (
          <table className="g-table mt-2">
            <thead>
              <tr>
                <th>{t("name")}</th>
                <th>{t("version")}</th>
                <th>{t("type")}</th>
                <th>{t("entryPoint")}</th>
              </tr>
            </thead>
            <tbody>
              {plugins.map((p) => (
                <tr key={p.entry_point}>
                  <td style={{ color: "var(--g-text)" }}>{p.name}</td>
                  <td style={{ color: "var(--g-text-muted)", fontFamily: "var(--font-mono, monospace)", fontSize: "0.75rem" }}>{p.version}</td>
                  <td><span className="g-status-pill g-status-pill--on">{p.plugin_type}</span></td>
                  <td style={{ color: "var(--g-text-muted)", fontFamily: "var(--font-mono, monospace)", fontSize: "0.75rem" }}>{p.entry_point}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
