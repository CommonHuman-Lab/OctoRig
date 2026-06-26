"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./creator.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { Plus, PenTool } from "lucide-react";
import { getMySubmissions } from "@/lib/api/content";
import { CreateModal } from "@/components/creator/CreateModal";
import { SubmissionRow } from "@/components/creator/SubmissionRow";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { Button } from "@/components/ui/Button";

export default function CreatorPage() {
  const t = useTranslations("creator");
  const td = useTranslations("deployments");
  const tc = useTranslations("common");
  const [showCreate, setShowCreate] = useState(false);

  const { data: submissions = [], isLoading } = useQuery({
    queryKey: ["content", "mine"],
    queryFn: () => getMySubmissions(),
  });

  return (
    <div className="page">
      <div className="creator-header page-header">
        <h1 className="page-title font-mono">
          <PenTool size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
          {t("title")}
        </h1>
        <Button variant="primary" leftIcon={<Plus size={14} />} onClick={() => setShowCreate(true)}>
          {t("newDraft")}
        </Button>
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={submissions}
        empty={
          <div className="creator-empty">
            {t("noSubmissions")}
          </div>
        }
      >
        {(submissions) => (
          <div className="creator-table-wrap">
            <table className="g-table">
              <thead>
                <tr>
                  <th>{t("colTitle")}</th>
                  <th>{t("colType")}</th>
                  <th>{td("colStatus")}</th>
                  <th>{t("colLastUpdated")}</th>
                  <th>{tc("actions")}</th>
                </tr>
              </thead>
              <tbody>
                {submissions.map((sub) => (
                  <SubmissionRow key={sub.id} sub={sub} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </AsyncContent>

      {showCreate && <CreateModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}
