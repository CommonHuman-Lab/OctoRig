// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import Link from "next/link";
import { CheckCircle2, Clock, Target, Flag, Droplets, FlaskConical, ExternalLink } from "lucide-react";
import type { ChallengeDetail } from "@/lib/api/challenges";
import { DIFF_COLOR } from "@/lib/utils/difficulty";

export function ChallengeHeader({
  challenge,
  solvedByMe,
  labIsLive,
  labUrl,
}: {
  challenge: ChallengeDetail;
  solvedByMe: boolean;
  labIsLive?: boolean;
  labUrl?: string | null;
}) {
  const diffColor = DIFF_COLOR[challenge.difficulty];

  return (
    <div className="ch-header">
      <div className="ch-meta-row">
        {challenge.lab_name && (
          <span className="ch-lab-status-group">
            <Link href="/labs" className="ch-lab-badge">
              <FlaskConical size={10} />
              {challenge.lab_name}
            </Link>
            {labIsLive !== undefined && (
              <span
                className={`ch-lab-status-dot ${labIsLive ? "ch-lab-status-dot--live" : "ch-lab-status-dot--off"}`}
                title={labIsLive ? "Lab is running" : "Lab is offline"}
              />
            )}
            {labIsLive && labUrl && (
              <a
                href={labUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="ch-lab-open-link"
                title={`Open ${challenge.lab_name}`}
              >
                <ExternalLink size={10} />
                Open Lab
              </a>
            )}
          </span>
        )}
        <span className="ch-cat">{challenge.category.replace(/-/g, " ")}</span>
        <span className="ch-diff" style={{ color: diffColor }}>{challenge.difficulty}</span>
        {solvedByMe && (
          <span className="ch-solved">
            <CheckCircle2 size={12} />
            Solved
          </span>
        )}
      </div>
      <h1 className="ch-detail-title">{challenge.title}</h1>
      <div className="ch-stats">
        <span className="ch-stat">
          <Flag size={12} />
          {challenge.points} pts
        </span>
        {challenge.estimated_minutes && (
          <span className="ch-stat">
            <Clock size={12} />
            ~{challenge.estimated_minutes}m
          </span>
        )}
        <span className="ch-stat">
          <Target size={12} />
          {challenge.solve_count} solve{challenge.solve_count !== 1 ? "s" : ""}
        </span>
        {challenge.first_blood_user && (
          <span className="ch-stat ch-stat--blood" title={`First blood: ${challenge.first_blood_user}`}>
            <Droplets size={12} />
            {challenge.first_blood_user}
          </span>
        )}
      </div>
    </div>
  );
}
