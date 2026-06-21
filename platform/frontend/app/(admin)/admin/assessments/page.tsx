"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../admin.css";

import { useState } from "react";
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

function StatusBadge({ isActive }: { isActive: boolean }) {
  return (
    <span className={`g-status-pill ${isActive ? "g-status-pill--on" : "g-status-pill--off"}`}>
      {isActive ? "active" : "inactive"}
    </span>
  );
}

export default function AdminAssessmentsPage() {
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
    staleTime: 60_000,
  });

  const createMutation = useApiMutation({
    mutationFn: createAssessment,
    invalidateKeys: [["admin-assessments"]],
    successMessage: (assessment) => `Assessment "${assessment.name}" created`,
    errorMessage: (err: any) => err?.response?.data?.detail ?? "Failed to create assessment",
    onSuccess: (assessment) => {
      setSheetOpen(false);
      router.push(`/admin/assessments/${assessment.id}`);
    },
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Assessments</h1>
        <Button
          variant="primary"
          size="sm"
          leftIcon={<Plus size={14} />}
          onClick={() => setSheetOpen(true)}
        >
          New Assessment
        </Button>
      </div>

      <AsyncContent
        isLoading={isLoading}
        data={assessments}
        empty={
          <div className="empty-state">
            <ClipboardList size={40} strokeWidth={1.2} />
            <p>No assessments yet.</p>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setSheetOpen(true)}
            >
              Create your first assessment
            </Button>
          </div>
        }
      >
        {(assessments) => (
          <table className="g-table g-table-hover">
            <thead>
              <tr>
                <th>Name</th>
                <th>Company</th>
                <th>Labs</th>
                <th>Duration</th>
                <th>Candidates</th>
                <th>Active</th>
                <th>Status</th>
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
