"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./labs-admin.css";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { useApiMutation } from "@/hooks/useApiMutation";
import { SearchBar } from "@/components/ui/SearchBar";
import { EmptyCell } from "@/components/ui/TableStates";
import { getAdminLabs, updateAdminLab, type AdminLab } from "@/lib/api/admin";
import { formatDateTime } from "@/lib/utils/date";
import { useConfirmStore } from "@/stores/confirm.store";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { AsyncContent } from "@/components/ui/AsyncContent";
import { SheetShell } from "@/components/ui/SheetShell";
import { FilterPills } from "@/components/ui/FilterPills";
import { Button } from "@/components/ui/Button";

const CATEGORY_IDS: (string | undefined)[] = [undefined, "world", "firerange", "thirdparty"];

export default function AdminLabsPage() {
  const t = useTranslations("admin.labs");
  const tLabs = useTranslations("labs");
  const tCommon = useTranslations("common");
  const tNav = useTranslations("nav");

  function categoryLabel(id: string | undefined) {
    if (id === "world") return tLabs("categoryWorld");
    if (id === "firerange") return tLabs("categoryFirerange");
    if (id === "thirdparty") return tLabs("categoryThirdparty");
    return tCommon("all");
  }

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [selected, setSelected] = useState<AdminLab | null>(null);
  const { confirm } = useConfirmStore();

  const { data: labs = [], isLoading } = useQuery({
    queryKey: ["admin-labs", category],
    queryFn: () => getAdminLabs({ category }),
  });

  const toggleMutation = useApiMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) =>
      updateAdminLab(id, { is_active }),
    invalidateKeys: [["admin-labs"]],
    successMessage: (updated) =>
      updated.is_active ? t("enabledToast", { name: updated.name }) : t("disabledToast", { name: updated.name }),
    errorMessage: (err: any) => err?.response?.data?.detail ?? t("toastUpdateLabFailed"),
    onSuccess: (updated) => setSelected((prev) => (prev && prev.id === updated.id ? updated : prev)),
  });

  useEscapeKey(() => setSelected(null), !!selected);

  const filtered = labs.filter((l) => {
    const q = search.trim().toLowerCase();
    if (!q) return true;
    return l.name.toLowerCase().includes(q) || l.slug.toLowerCase().includes(q) || l.category.toLowerCase().includes(q);
  });

  function handleToggle(lab: AdminLab) {
    if (lab.is_active) {
      confirm({
        title: t("disableTitle", { name: lab.name }),
        body:
          lab.active_deployment_count > 0
            ? t("disableBodyWithDeployments", { count: lab.active_deployment_count })
            : t("disableBodyNoDeployments"),
        confirmLabel: t("disableConfirm"),
        dangerous: true,
        onConfirm: () => toggleMutation.mutate({ id: lab.id, is_active: false }),
      });
      return;
    }
    toggleMutation.mutate({ id: lab.id, is_active: true });
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">{tNav("labs")}</h1>
        <SearchBar value={search} onChange={setSearch} placeholder={tLabs("searchPlaceholder")} />
      </div>

      <div className="filter-bar">
        <FilterPills
          size="sm"
          groups={[
            {
              options: CATEGORY_IDS,
              value: category,
              onChange: setCategory,
              label: categoryLabel,
            },
          ]}
        />
      </div>

      <div className="g-panel">
        <AsyncContent
          isLoading={isLoading}
          data={filtered}
          empty={<EmptyCell label={t("noLabsFound")} />}
        >
          {(filtered) => (
            <table className="g-table">
              <thead>
                <tr>
                  <th>{tCommon("colName")}</th>
                  <th>{tCommon("colSlug")}</th>
                  <th>{tCommon("colCategory")}</th>
                  <th>{t("colActiveDeployments")}</th>
                  <th>{t("colEnabled")}</th>
                  <th>{tCommon("actions")}</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((lab) => (
                  <tr key={lab.id}>
                    <td className="font-mono text-sm">{lab.name}</td>
                    <td className="font-mono text-11 text-muted">{lab.slug}</td>
                    <td className="text-11 text-secondary">{lab.category}</td>
                    <td className="text-11 text-muted">{lab.active_deployment_count}</td>
                    <td>
                      <label className="toggle" title={lab.is_active ? t("disableLabTooltip") : t("enableLabTooltip")}>
                        <input
                          type="checkbox"
                          checked={lab.is_active}
                          disabled={toggleMutation.isPending}
                          onChange={() => handleToggle(lab)}
                        />
                        <span className="toggle-track" />
                      </label>
                    </td>
                    <td>
                      <div className="row-actions">
                        <Button variant="ghost" size="sm" onClick={() => setSelected(lab)}>
                          {t("detailsBtn")}
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </AsyncContent>
      </div>

      {selected && (
        <SheetShell
          title={<>{selected.name}</>}
          onClose={() => setSelected(null)}
          footer={
            <Button variant="ghost" onClick={() => setSelected(null)}>{tLabs("close")}</Button>
          }
        >
              <div className="lab-detail-section">
                <div className="lab-detail-label">{tCommon("colDescription")}</div>
                <p className="text-sm">{selected.description}</p>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">{tCommon("colSlug")}</div>
                <span className="font-mono text-11 text-muted">{selected.slug}</span>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">{tCommon("colCategory")}</div>
                <span className="text-sm">{selected.category}</span>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">{t("containersLabel")}</div>
                <div className="lab-detail-containers">
                  {selected.container_names.map((name) => (
                    <span key={name} className="font-mono text-11 text-muted">{name}</span>
                  ))}
                </div>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">{t("exposedPortsLabel")}</div>
                <div className="lab-detail-ports">
                  {Object.entries(selected.exposed_ports).map(([role, port]) => (
                    <span key={role} className="g-badge">{role}: {port}</span>
                  ))}
                </div>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">{t("deploymentsLabel")}</div>
                <span className="text-sm">
                  {t("activeOfTotal", { active: selected.active_deployment_count, total: selected.total_deployment_count })}
                </span>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">{t("requiresPrivilegedLabel")}</div>
                <span className="text-sm">{selected.requires_privileged ? t("yes") : t("no")}</span>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">{t("lastUpdatedLabel")}</div>
                <span className="font-mono text-11 text-muted">{formatDateTime(selected.updated_at)}</span>
              </div>
        </SheetShell>
      )}
    </div>
  );
}
