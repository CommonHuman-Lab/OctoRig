"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useQuery } from "@tanstack/react-query";
import { ExternalLink } from "lucide-react";
import { getDeployments } from "@/lib/api/deployments";
import { getContainers } from "@/lib/api/system";
import { getLabs, type LabTemplate } from "@/lib/api/labs";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import type { WidgetComponentProps } from "@/lib/widgets/types";

function getLabUrl(labs: LabTemplate[], containerName: string): string | null {
  const lab = labs.find((l) => l.container_names.some((cn) => containerName.startsWith(`${cn}-`)));
  const url = lab?.access_info.find((a) => a.key === "URL")?.value ?? null;
  return url && url.startsWith("http") ? url : null;
}

export function ExternalContainersWidget({ widget }: WidgetComponentProps) {
  const { data: deployments = [] } = useQuery({ queryKey: ["deployments"], queryFn: () => getDeployments() });
  const { data: containers = [] } = useQuery({ queryKey: ["containers"], queryFn: getContainers });
  const { data: labs = [] } = useQuery<LabTemplate[]>({ queryKey: ["labs"], queryFn: () => getLabs(), staleTime: 60_000 });

  const knownNames = new Set(deployments.flatMap((d) => d.container_names));
  const externalContainers = containers.filter(
    (c) =>
      !knownNames.has(c.name) &&
      c.name.startsWith("octorig-") &&
      !c.name.includes("platform") &&
      c.name !== "octorig-socket-proxy"
  );

  if (externalContainers.length === 0) return null;

  return (
    <div className={`g-panel dash-panel-h-${widget.height}`}>
      <div className="g-panel-header">
        <span className="text-secondary text-11 font-mono">Externally Managed</span>
        <span className="g-badge" style={{ color: "var(--g-warning)" }}>CLI</span>
      </div>
      <div className="dash-panel-scroll">
        <table className="g-table">
          <thead><tr><th>Container</th><th>Status</th><th>Access</th></tr></thead>
          <tbody>
            {externalContainers.map((c) => {
              const url = getLabUrl(labs, c.name);
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
    </div>
  );
}
