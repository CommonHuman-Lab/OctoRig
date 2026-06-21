"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./labs-admin.css";

import { useState } from "react";
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

const CATEGORIES = [
  { id: undefined, label: "All" },
  { id: "world", label: "World" },
  { id: "firerange", label: "Fire Range" },
  { id: "thirdparty", label: "Third Party" },
] as const;

export default function AdminLabsPage() {
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
    successMessage: (updated) => `${updated.name} ${updated.is_active ? "enabled" : "disabled"}`,
    errorMessage: (err: any) => err?.response?.data?.detail ?? "Failed to update lab",
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
        title: `Disable ${lab.name}?`,
        body:
          lab.active_deployment_count > 0
            ? `${lab.active_deployment_count} deployment(s) are currently running. Disabling hides this lab from users but does not stop running deployments.`
            : "Users will no longer be able to deploy this lab.",
        confirmLabel: "Disable",
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
        <h1 className="page-title font-mono">Labs</h1>
        <SearchBar value={search} onChange={setSearch} placeholder="Search labs…" />
      </div>

      <div className="filter-bar">
        <FilterPills
          size="sm"
          groups={[
            {
              options: CATEGORIES.map((c) => c.id),
              value: category,
              onChange: setCategory,
              label: (v) => CATEGORIES.find((c) => c.id === v)?.label ?? "All",
            },
          ]}
        />
      </div>

      <div className="g-panel">
        <AsyncContent
          isLoading={isLoading}
          data={filtered}
          empty={<EmptyCell label="No labs found." />}
        >
          {(filtered) => (
            <table className="g-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Slug</th>
                  <th>Category</th>
                  <th>Active deployments</th>
                  <th>Enabled</th>
                  <th>Actions</th>
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
                      <label className="toggle" title={lab.is_active ? "Disable lab" : "Enable lab"}>
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
                          Details
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
            <Button variant="ghost" onClick={() => setSelected(null)}>Close</Button>
          }
        >
              <div className="lab-detail-section">
                <div className="lab-detail-label">Description</div>
                <p className="text-sm">{selected.description}</p>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">Slug</div>
                <span className="font-mono text-11 text-muted">{selected.slug}</span>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">Category</div>
                <span className="text-sm">{selected.category}</span>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">Containers</div>
                <div className="lab-detail-containers">
                  {selected.container_names.map((name) => (
                    <span key={name} className="font-mono text-11 text-muted">{name}</span>
                  ))}
                </div>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">Exposed ports</div>
                <div className="lab-detail-ports">
                  {Object.entries(selected.exposed_ports).map(([role, port]) => (
                    <span key={role} className="g-badge">{role}: {port}</span>
                  ))}
                </div>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">Deployments</div>
                <span className="text-sm">
                  {selected.active_deployment_count} active / {selected.total_deployment_count} total
                </span>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">Requires privileged</div>
                <span className="text-sm">{selected.requires_privileged ? "Yes" : "No"}</span>
              </div>

              <div className="lab-detail-section">
                <div className="lab-detail-label">Last updated</div>
                <span className="font-mono text-11 text-muted">{formatDateTime(selected.updated_at)}</span>
              </div>
        </SheetShell>
      )}
    </div>
  );
}
