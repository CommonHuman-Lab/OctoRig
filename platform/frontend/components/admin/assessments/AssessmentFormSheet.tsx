"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Save } from "lucide-react";
import { type LabTemplate } from "@/lib/api/labs";
import { type Assessment, type CreateAssessmentPayload } from "@/lib/api/assessments";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";
import { Button } from "@/components/ui/Button";

const BLANK_FORM = {
  name: "",
  slug: "",
  slugEdited: false,
  companyName: "",
  companyLogoUrl: "",
  description: "",
  instructions: "",
  durationHours: 48,
  selectedSlugs: [] as string[],
  displayNames: {} as Record<string, string>,
};

function assessmentToForm(a: Assessment) {
  return {
    name: a.name,
    slug: a.slug,
    slugEdited: true,
    companyName: a.company_name ?? "",
    companyLogoUrl: a.company_logo_url ?? "",
    description: a.description ?? "",
    instructions: a.candidate_instructions ?? "",
    durationHours: a.duration_hours,
    selectedSlugs: a.lab_slugs,
    displayNames: { ...a.lab_display_names },
  };
}

function slugify(s: string) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

interface AssessmentFormSheetProps {
  open: boolean;
  labs: LabTemplate[];
  labsLoading: boolean;
  saveMutation: { mutate: (data: CreateAssessmentPayload) => void; isPending: boolean };
  onClose: () => void;
  initialValues?: Assessment | null;
}

export function AssessmentFormSheet({
  open,
  labs,
  labsLoading,
  saveMutation,
  onClose,
  initialValues,
}: AssessmentFormSheetProps) {
  const t = useTranslations("admin.assessments");
  const tCommon = useTranslations("common");
  const [form, setForm] = useState(BLANK_FORM);
  const isEdit = !!initialValues;

  useEffect(() => {
    if (open) setForm(initialValues ? assessmentToForm(initialValues) : BLANK_FORM);
  }, [open, initialValues]);

  useEscapeKey(onClose, open);

  if (!open) return null;

  function handleNameChange(value: string) {
    setForm((f) => ({
      ...f,
      name: value,
      slug: f.slugEdited ? f.slug : slugify(value),
    }));
  }

  function toggleLab(labSlug: string) {
    setForm((f) => ({
      ...f,
      selectedSlugs: f.selectedSlugs.includes(labSlug)
        ? f.selectedSlugs.filter((s) => s !== labSlug)
        : [...f.selectedSlugs, labSlug],
    }));
  }

  function handleSubmit() {
    if (!form.name || form.selectedSlugs.length === 0) return;
    saveMutation.mutate({
      name: form.name,
      slug: form.slug || undefined,
      company_name: form.companyName || undefined,
      company_logo_url: form.companyLogoUrl || undefined,
      description: form.description || undefined,
      candidate_instructions: form.instructions || undefined,
      duration_hours: form.durationHours,
      lab_slugs: form.selectedSlugs,
      lab_display_names: form.displayNames,
    });
  }

  return (
    <SheetShell
      title={isEdit ? t("editTitle") : t("newAssessmentBtn")}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose}>
            {tCommon("cancel")}
          </Button>
          <Button
            variant="primary"
            disabled={!form.name || form.selectedSlugs.length === 0 || saveMutation.isPending}
            onClick={handleSubmit}
            leftIcon={<Save size={13} />}
          >
            {saveMutation.isPending ? (isEdit ? tCommon("saving") : tCommon("creating")) : (isEdit ? tCommon("saveChanges") : t("createAssessmentBtn"))}
          </Button>
        </>
      }
    >
          <label className="ev-field">
            <span className="ev-label">{tCommon("colName")}</span>
            <input
              className="g-input"
              placeholder={t("namePlaceholder")}
              value={form.name}
              onChange={(e) => handleNameChange(e.target.value)}
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">{tCommon("colSlug")}</span>
            <input
              className="g-input"
              style={{ fontFamily: "var(--font-mono, monospace)" }}
              placeholder={t("slugPlaceholder")}
              value={form.slug}
              onChange={(e) =>
                setForm((f) => ({ ...f, slug: e.target.value, slugEdited: true }))
              }
            />
          </label>

          <div className="ev-field-row">
            <label className="ev-field">
              <span className="ev-label">{t("durationHoursLabel")}</span>
              <input
                className="g-input"
                type="number"
                min={1}
                max={720}
                value={form.durationHours}
                onChange={(e) =>
                  setForm((f) => ({ ...f, durationHours: Number(e.target.value) }))
                }
              />
            </label>
            <label className="ev-field">
              <span className="ev-label">{t("companyNameLabel")}</span>
              <input
                className="g-input"
                placeholder={t("companyNamePlaceholder")}
                value={form.companyName}
                onChange={(e) => setForm((f) => ({ ...f, companyName: e.target.value }))}
              />
            </label>
          </div>

          <label className="ev-field">
            <span className="ev-label">{t("companyLogoUrlLabel")}</span>
            <input
              className="g-input"
              placeholder={t("companyLogoUrlPlaceholder")}
              value={form.companyLogoUrl}
              onChange={(e) => setForm((f) => ({ ...f, companyLogoUrl: e.target.value }))}
            />
          </label>

          <div className="ev-field">
            <span className="ev-label">{tCommon("colDescription")}</span>
            <textarea
              className="g-input"
              rows={3}
              placeholder={t("descriptionPlaceholder")}
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            />
          </div>

          <div className="ev-field">
            <span className="ev-label">{t("candidateInstructionsLabel")}</span>
            <textarea
              className="g-input"
              rows={5}
              placeholder={t("candidateInstructionsPlaceholder")}
              value={form.instructions}
              onChange={(e) => setForm((f) => ({ ...f, instructions: e.target.value }))}
            />
          </div>

          <div className="ev-field">
            <span className="ev-label">{t("labsRequiredLabel")}</span>
            {labsLoading ? (
              <p style={{ color: "var(--g-text-muted)", fontSize: "0.8rem", margin: 0 }}>
                {t("loadingLabs")}
              </p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                {labs.map((lab) => {
                  const checked = form.selectedSlugs.includes(lab.slug);
                  return (
                    <div key={lab.slug}>
                      <div
                        onClick={() => toggleLab(lab.slug)}
                        style={{
                          display: "flex",
                          alignItems: "flex-start",
                          gap: 10,
                          padding: "8px 10px",
                          border: `1px solid ${checked ? "var(--g-accent)" : "var(--g-border)"}`,
                          borderRadius: checked ? "6px 6px 0 0" : 6,
                          background: checked
                            ? "color-mix(in srgb, var(--g-accent) 8%, var(--g-surface))"
                            : "var(--g-surface)",
                          cursor: "pointer",
                          transition: "border-color 0.12s, background 0.12s",
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          readOnly
                          style={{ marginTop: 2, cursor: "pointer", flexShrink: 0 }}
                        />
                        <div>
                          <div
                            style={{ fontSize: "0.825rem", fontWeight: 500, color: "var(--g-text)" }}
                          >
                            {lab.name}
                          </div>
                          <div
                            style={{ fontSize: "0.75rem", color: "var(--g-text-muted)", marginTop: 1 }}
                          >
                            {lab.description}
                          </div>
                        </div>
                      </div>
                      {checked && (
                        <div
                          style={{
                            padding: "8px 10px",
                            border: "1px solid var(--g-accent)",
                            borderTop: "1px solid var(--g-border)",
                            borderRadius: "0 0 6px 6px",
                            background: "var(--g-surface)",
                          }}
                        >
                          <input
                            className="g-input"
                            placeholder={t("displayNamePlaceholder", { name: lab.name })}
                            value={form.displayNames[lab.slug] ?? ""}
                            onClick={(e) => e.stopPropagation()}
                            onChange={(e) =>
                              setForm((f) => ({
                                ...f,
                                displayNames: { ...f.displayNames, [lab.slug]: e.target.value },
                              }))
                            }
                          />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
            {form.selectedSlugs.length > 0 && (
              <span style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>
                {t("labsSelectedCount", { count: form.selectedSlugs.length })}
              </span>
            )}
          </div>
    </SheetShell>
  );
}
