"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./lab-detail.css";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import {
  ArrowLeft, Play, Square, RotateCcw, ExternalLink,
  Network, Globe, Terminal, Server, CheckCircle2, Clock, Target,
} from "lucide-react";
import { getLabs, type LabTemplate } from "@/lib/api/labs";
import { getChallenges, type ChallengeListItem, type ChallengeDifficulty } from "@/lib/api/challenges";
import { stopDeployment, resetDeployment } from "@/lib/api/deployments";
import { LabCategoryBadge } from "@/components/labs/LabCategoryBadge";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { StartLabDialog } from "@/components/deployments/StartLabDialog";
import { PageSpinner } from "@/components/ui/Spinner";
import { CopyButton } from "@/components/ui/CopyButton";
import { Button } from "@/components/ui/Button";
import { DIFF_CLASS } from "@/lib/utils/difficulty";

function DiffBadge({ difficulty }: { difficulty: ChallengeDifficulty }) {
  return (
    <span className={`g-diff-badge ${DIFF_CLASS[difficulty]}`}>{difficulty}</span>
  );
}

function ChallengeRow({ ch }: { ch: ChallengeListItem }) {
  return (
    <Link href={`/challenges/${ch.slug}`} className="ld-ch-row">
      <div className="ld-ch-info">
        <span className="ld-ch-cat">{ch.category.replace("-", " ")}</span>
        <span className="ld-ch-title">{ch.title}</span>
        <div className="ld-ch-tags">
          {ch.tags.slice(0, 4).map((t) => (
            <span key={t} className="g-tag text-10">{t}</span>
          ))}
        </div>
      </div>
      <div className="ld-ch-right">
        <DiffBadge difficulty={ch.difficulty} />
        <span className="ld-ch-pts">{ch.points} pts</span>
        <div className="ld-ch-meta">
          {ch.estimated_minutes && (
            <span className="ld-ch-meta-item"><Clock size={10} />{ch.estimated_minutes}m</span>
          )}
          <span className="ld-ch-meta-item"><Target size={10} />{ch.solve_count}</span>
          {ch.solved_by_me && (
            <span className="ld-ch-solved"><CheckCircle2 size={10} />Solved</span>
          )}
        </div>
      </div>
    </Link>
  );
}

export default function LabDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [startOpen, setStartOpen] = useState(false);

  const { data: labs = [], isLoading: labsLoading } = useQuery<LabTemplate[]>({
    queryKey: ["labs"],
    queryFn: () => getLabs(),
    staleTime: 30_000,
  });

  const lab = labs.find((l) => l.slug === slug) as LabTemplate | undefined;

  const { data: challenges = [], isLoading: chLoading } = useQuery({
    queryKey: ["challenges", { lab_slug: slug }],
    queryFn: () => getChallenges({ lab_slug: slug }),
    enabled: !!lab,
  });

  const stopMutation = useApiMutation({
    mutationFn: stopDeployment,
    invalidateKeys: [["labs"]],
    successMessage: "Stop requested",
    errorMessage: "Failed to stop lab",
  });

  const resetMutation = useApiMutation({
    mutationFn: resetDeployment,
    invalidateKeys: [["labs"]],
    successMessage: "Reset requested",
    errorMessage: "Failed to reset lab",
  });

  if (labsLoading) {
    return (
      <div className="page">
        <PageSpinner />
      </div>
    );
  }

  if (!lab) {
    return (
      <div className="page">
        <Link href="/labs" className="back-link">
          <ArrowLeft size={14} /> Labs
        </Link>
        <p className="text-muted text-sm mt-4">Lab not found.</p>
      </div>
    );
  }

  const deployment = lab.current_deployment;
  const isRunning = deployment?.status === "running" || deployment?.status === "starting";
  const accessInfo = deployment?.access_info.length ? deployment.access_info : lab.access_info;
  // Subnet/IP/container names are per-deployment; only show them once a deployment exists
  const subnet = deployment?.subnet ?? null;
  const appIp = deployment?.app_ip ?? null;
  const containerNames = deployment?.container_names?.length ? deployment.container_names : null;
  const labUrl = accessInfo.find((a) => a.key === "URL")?.value;

  const portChips = Object.entries(lab.exposed_ports).map(([name, port]) => (
    <span key={name} className="g-tag text-10">{name.toUpperCase()}:{port}</span>
  ));

  return (
    <div className="page">
      <Link href="/labs" className="back-link">
        <ArrowLeft size={14} /> Labs
      </Link>

      {/* Header */}
      <div className="ld-header">
        <div className="ld-title-row">
          <h1 className="ld-title font-mono">{lab.name}</h1>
          <div className="ld-badges">
            <LabCategoryBadge category={lab.category} />
            {deployment && <DeploymentStatusBadge status={deployment.status} />}
          </div>
        </div>
        <p className="ld-desc">{lab.description}</p>

        {/* Controls */}
        <div className="ld-controls">
          {!isRunning ? (
            <Button variant="primary" leftIcon={<Play size={14} />} onClick={() => setStartOpen(true)}>
              Start Lab
            </Button>
          ) : (
            <>
              <Button
                variant="danger"
                leftIcon={<Square size={14} />}
                onClick={() => deployment && stopMutation.mutate(deployment.id)}
                disabled={deployment?.status === "stopping"}
              >
                Stop
              </Button>
              {lab.category === "firerange" && (
                <Button
                  leftIcon={<RotateCcw size={14} />}
                  onClick={() => deployment && resetMutation.mutate(deployment.id)}
                >
                  Reset
                </Button>
              )}
              {labUrl && (
                <Button href={labUrl} leftIcon={<ExternalLink size={14} />}>
                  Open Lab
                </Button>
              )}
            </>
          )}
        </div>
      </div>

      <div className="ld-body">
        {/* Network info */}
        <div className="g-card ld-info-card">
          <h2 className="ld-section-title">Network</h2>
          <div className="ld-info-rows">
            {subnet && appIp ? (
              <>
                <div className="ld-info-row">
                  <span className="ld-info-key"><Network size={12} /> Subnet</span>
                  <span className="ld-info-val font-mono">{subnet}</span>
                </div>
                <div className="ld-info-row">
                  <span className="ld-info-key"><Server size={12} /> App IP</span>
                  <span className="ld-info-val font-mono">{appIp}</span>
                </div>
              </>
            ) : (
              <div className="ld-info-row">
                <span className="ld-info-key"><Network size={12} /> Subnet / App IP</span>
                <span className="ld-info-val text-muted">Assigned when started</span>
              </div>
            )}
            <div className="ld-info-row">
              <span className="ld-info-key"><Terminal size={12} /> Containers</span>
              <span className="ld-info-val font-mono">
                {containerNames ? containerNames.join(", ") : "Assigned when started"}
              </span>
            </div>
            <div className="ld-info-row">
              <span className="ld-info-key"><Globe size={12} /> Ports</span>
              <div className="ld-info-chips">{portChips}</div>
            </div>
          </div>
        </div>

        {/* Access info — only shown when running */}
        {isRunning && accessInfo.length > 0 && (
          <div className="g-card ld-info-card">
            <h2 className="ld-section-title">Access</h2>
            <div className="ld-access-rows">
              {accessInfo.map((row) => (
                <div key={row.key} className="ld-access-row">
                  <span className="ld-access-key">{row.key}</span>
                  <span className="ld-access-val font-mono">{row.value}</span>
                  <CopyButton value={row.value} />
                  {row.value.startsWith("http") && (
                    <a href={row.value} target="_blank" rel="noopener noreferrer" className="ld-access-link">
                      <ExternalLink size={11} />
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Challenges */}
        <div className="g-card ld-ch-card">
          <h2 className="ld-section-title">
            Challenges
            {!chLoading && (
              <span className="ld-ch-count">{challenges.length}</span>
            )}
          </h2>
          {chLoading ? (
            <div className="text-muted text-sm">Loading challenges…</div>
          ) : challenges.length === 0 ? (
            <div className="text-muted text-sm">No challenges linked to this lab.</div>
          ) : (
            <div className="ld-ch-list">
              {challenges.map((ch) => (
                <ChallengeRow key={ch.id} ch={ch} />
              ))}
            </div>
          )}
        </div>
      </div>

      {lab && (
        <StartLabDialog lab={lab} open={startOpen} onClose={() => setStartOpen(false)} />
      )}

    </div>
  );
}
