"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../admin.css";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { Plus, ClipboardList, Users } from "lucide-react";
import { listAssessments, createAssessment, type Assessment } from "@/lib/api/assessments";
import { getLabs, type LabTemplate } from "@/lib/api/labs";
import { useUserStore } from "@/stores/user.store";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { AssessmentFormSheet } from "@/components/admin/assessments/AssessmentFormSheet";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { Button } from "@/components/ui/Button";
import { STALE_TIME } from "@/lib/config";

function StatusBadge({ isActive }: { isActive: boolean }) {
  const tUsers = useTranslations("admin.users");
  return (
    <span className={`g-status-pill ${isActive ? "g-status-pill--on" : "g-status-pill--off"}`}>
      {isActive ? tUsers("active") : tUsers("inactive")}
    </span>
  );
}

export default function AdminAssessmentsPage() {
  const t = useTranslations("admin.assessments");
  const tNav = useTranslations("nav");
  const tUsers = useTranslations("admin.users");
  const tCommon = useTranslations("common");
  const { user } = useUserStore();
  const router = useRouter();
  const [sheetOpen, setSheetOpen] = useState(false);

  useEffect(() => {
    if (user && !user.permissions?.includes("admin.panel")) router.replace("/");
  }, [user, router]);

  const { data: assessments = [], isLoading } = useQuery({
    queryKey: ["admin-assessments"],
    queryFn: listAssessments,
    enabled: !!user?.permissions?.includes("admin.panel"),
  });

  const { data: labs = [], isLoading: labsLoading } = useQuery<LabTemplate[]>({
    queryKey: ["labs", "world"],
    queryFn: () => getLabs("world"),
    staleTime: STALE_TIME.MEDIUM,
  });

  const createMutation = useApiMutation({
    mutationFn: createAssessment,
    invalidateKeys: [["admin-assessments"]],
    successMessage: (assessment) => t("toastAssessmentCreated", { name: assessment.name }),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("toastCreateAssessmentFailed"),
    onSuccess: (assessment) => {
      setSheetOpen(false);
      router.push(`/admin/assessments/${assessment.id}`);
    },
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">{tNav("adminAssessments")}</h1>
        <Button
          variant="primary"
          size="sm"
          leftIcon={<Plus size={14} />}
          onClick={() => setSheetOpen(true)}
        >
          {t("newAssessmentBtn")}
        </Button>
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={assessments}
        empty={
          <div className="empty-state">
            <ClipboardList size={40} strokeWidth={1.2} />
            <p>{t("noAssessmentsYet")}</p>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setSheetOpen(true)}
            >
              {t("createFirstBtn")}
            </Button>
          </div>
        }
      >
        {(assessments) => (
          <table className="g-table g-table-hover">
            <thead>
              <tr>
                <th>{tCommon("colName")}</th>
                <th>{t("colCompany")}</th>
                <th>{tNav("labs")}</th>
                <th>{t("colDuration")}</th>
                <th>{t("colCandidates")}</th>
                <th>{t("colActive")}</th>
                <th>{tCommon("colStatus")}</th>
              </tr>
            </thead>
            <tbody>
              {assessments.map((a: Assessment) => (
                <tr
                  key={a.id}
                  style={{ cursor: "pointer" }}
                  onClick={() => router.push(`/admin/assessments/${a.id}`)}
                >
                  <td style={{ fontWeight: 500, color: "var(--g-text)" }}>{a.name}</td>
                  <td style={{ color: "var(--g-text-muted)", fontSize: "0.8rem" }}>
                    {a.company_name ?? <span style={{ opacity: 0.4 }}>—</span>}
                  </td>
                  <td style={{ fontFamily: "var(--font-mono, monospace)", fontSize: "0.75rem" }}>
                    {a.lab_slugs.length}
                  </td>
                  <td style={{ color: "var(--g-text-muted)", fontSize: "0.8rem" }}>
                    {a.duration_hours}h
                  </td>
                  <td>
                    <span style={{ display: "flex", alignItems: "center", gap: 4, color: "var(--g-text-muted)", fontSize: "0.8rem" }}>
                      <Users size={12} />
                      {a.invite_count}
                    </span>
                  </td>
                  <td>
                    <span style={{ color: a.active_invite_count > 0 ? "var(--g-accent)" : "var(--g-text-muted)", fontSize: "0.8rem" }}>
                      {a.active_invite_count}
                    </span>
                  </td>
                  <td>
                    <StatusBadge isActive={a.is_active} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </AsyncContent>

      <AssessmentFormSheet
        open={sheetOpen}
        labs={labs}
        labsLoading={labsLoading}
        saveMutation={createMutation}
        onClose={() => setSheetOpen(false)}
      />
    </div>
  );
}
