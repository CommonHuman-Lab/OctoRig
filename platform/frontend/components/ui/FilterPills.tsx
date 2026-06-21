// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { FilterPillGroup } from "./FilterPills.types";

function defaultLabel(v: string | undefined) {
  if (v === undefined) return "All";
  return v.charAt(0).toUpperCase() + v.slice(1);
}

export function FilterPills({ groups, size }: { groups: FilterPillGroup[]; size?: "sm" }) {
  return (
    <>
      {groups.map((group, i) => (
        <div key={i} className="filter-group">
          {group.options.map((opt) => (
            <button
              key={String(opt)}
              className={`filter-pill ${size === "sm" ? "filter-pill-sm" : ""} ${group.value === opt ? "active" : ""}`}
              onClick={() => group.onChange(opt)}
            >
              {group.label ? group.label(opt) : defaultLabel(opt)}
            </button>
          ))}
        </div>
      ))}
    </>
  );
}
