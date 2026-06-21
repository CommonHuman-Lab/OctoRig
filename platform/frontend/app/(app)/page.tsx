"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ExternalLink, LayoutDashboard } from "lucide-react";
import { getDeployments, stopDeployment } from "@/lib/api/deployments";
import { getHealth, getContainers } from "@/lib/api/system";
import { getLabs, type LabTemplate } from "@/lib/api/labs";
import { getMyProfile } from "@/lib/api/profiles";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { useApiMutation } from "@/hooks/useApiMutation";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { Button } from "@/components/ui/Button";

function formatRelative(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60_000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export default function Dashboard() {
  const router = useRouter();

  const { data: deployments = [], isLoading } = useQuery({
    queryKey: ["deployments"],
    queryFn: () => getDeployments(),
  });
  const { data: containers = [] } = useQuery({
    queryKey: ["containers"],
    queryFn: getContainers,
  });
  const { data: labs = [] } = useQuery<LabTemplate[]>({
    queryKey: ["labs"],
    queryFn: () => getLabs(),
    staleTime: 60_000,
  });
  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 30_000,
  });
  const { data: profile } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: getMyProfile,
    staleTime: 60_000,
  });

  const stopMutation = useApiMutation({
    mutationFn: stopDeployment,
    invalidateKeys: [["deployments"], ["labs"]],
    successMessage: "Lab stop requested",
    errorMessage: "Failed to stop lab",
  });

  const activeDeployments = deployments.filter((d) => d.status !== "stopped");
  const knownNames = new Set(deployments.flatMap((d) => d.container_names));
  const externalContainers = containers.filter(
    (c) =>
      !knownNames.has(c.name) &&
      c.name.startsWith("octorig-") &&
      !c.name.includes("platform") &&
      c.name !== "octorig-socket-proxy"
  );

  // Best-effort label for untracked containers: match by base-name prefix (names are per-deployment)
  const getLabUrl = (containerName: string) => {
    const lab = labs.find((l) => l.container_names.some((cn) => containerName.startsWith(`${cn}-`)));
    const url = lab?.access_info.find((a) => a.key === "URL")?.value ?? null;
    // Template access_info is just a placeholder unless tied to a real deployment
    return url && url.startsWith("http") ? url : null;
  };

  return (
    <div className="page">
      <h1 className="page-title font-mono">
        <LayoutDashboard size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
        Dashboard
      </h1>

      {/* Stat cards */}
      <div className="stat-row">
        <div className="g-card stat-card">
          <span className="text-muted text-11">Running Labs</span>
          <span className="stat-value text-accent">{health?.running_labs ?? "—"}</span>
        </div>
        <div className="g-card stat-card">
          <span className="text-muted text-11">Total Containers</span>
          <span className="stat-value">{health?.total_containers ?? "—"}</span>
        </div>
        <div className="g-card stat-card">
          <span className="text-muted text-11">Docker</span>
          <span className={`stat-value ${health?.docker === "ok" ? "text-success" : "text-danger"}`}>
            {health?.docker === "ok" ? "Healthy" : "-"}
          </span>
        </div>
        <div className="g-card stat-card">
          <span className="text-muted text-11">Database</span>
          <span className={`stat-value ${health?.database === "ok" ? "text-success" : "text-danger"}`}>
            {health?.database === "ok" ? "Healthy" : "-"}
          </span>
        </div>
        <div className="g-card stat-card">
          <span className="text-muted text-11">Labs Available</span>
          <span className="stat-value">{labs.length > 0 ? labs.length : "—"}</span>
        </div>
        <div className="g-card stat-card">
          <span className="text-muted text-11">My Solves</span>
          <span className="stat-value text-accent">{profile?.solve_count ?? "—"}</span>
        </div>
        <div className="g-card stat-card">
          <span className="text-muted text-11">Total Points</span>
          <span className="stat-value text-accent">{profile?.total_points ?? "—"}</span>
        </div>
        <div className="g-card stat-card">
          <span className="text-muted text-11">First Bloods</span>
          <span className="stat-value text-danger">{profile?.first_bloods ?? "—"}</span>
        </div>
      </div>

      {/* Active deployments */}
      <section className="mt-4">
        <h2 className="section-title font-mono">Active Deployments</h2>
        <AsyncContent
          isLoading={isLoading}
          data={activeDeployments}
          empty={
            <div className="g-panel empty-state">
              <p className="text-muted text-sm">No active labs.</p>
              <Link href="/labs" className="g-btn g-btn-primary mt-2">Browse Lab Catalog</Link>
            </div>
          }
        >
          {(activeDeployments) => (
            <div className="g-panel">
              <table className="g-table">
                <thead>
                  <tr>
                    <th>Lab</th>
                    <th>Status</th>
                    <th>Started By</th>
                    <th>Started</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {activeDeployments.map((d) => (
                    <tr
                      key={d.id}
                      onClick={() => router.push(`/deployments/${d.id}`)}
                      style={{ cursor: "pointer" }}
                    >
                      <td>
                        <span className="text-accent">{d.lab_name}</span>
                      </td>
                      <td><DeploymentStatusBadge status={d.status} /></td>
                      <td className="text-secondary">{d.started_by_username}</td>
                      <td className="text-muted font-mono" style={{ fontSize: "0.6875rem" }}>
                        {d.started_at ? formatRelative(d.started_at) : "—"}
                      </td>
                      <td>
                        <Button
                          variant="danger"
                          icon
                          leftIcon="■"
                          onClick={(e) => { e.stopPropagation(); stopMutation.mutate(d.id); }}
                          disabled={d.status === "stopping" || stopMutation.isPending}
                          tooltip="Stop lab"
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </AsyncContent>
      </section>

      {/* Externally managed (CLI-started) */}
      {externalContainers.length > 0 && (
        <section className="mt-4">
          <h2 className="section-title font-mono">
            Externally Managed
            <span className="g-badge ml-2" style={{ color: "var(--g-warning)" }}>CLI</span>
          </h2>
          <div className="g-panel">
            <p className="text-muted text-11 mb-3">Containers started via the CLI — read-only in this view.</p>
            <table className="g-table">
              <thead><tr><th>Container</th><th>Status</th><th>Access</th></tr></thead>
              <tbody>
                {externalContainers.map((c) => {
                  const url = getLabUrl(c.name);
                  return (
                    <tr key={c.name}>
                      <td className="font-mono text-11">{c.name}</td>
                      <td><DeploymentStatusBadge status={c.status === "running" ? "running" : "stopped"} /></td>
                      <td>
                        {url ? (
                          <a href={url} target="_blank" rel="noopener" className="text-accent flex items-center gap-1 text-11">
                            {url}
                            <ExternalLink size={11} />
                          </a>
                        ) : (
                          <span className="text-muted text-11">{c.image}</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
