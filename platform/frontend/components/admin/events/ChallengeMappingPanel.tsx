"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { X } from "lucide-react";
import type { CtfEvent } from "@/lib/api/events";
import { Button } from "@/components/ui/Button";

interface EventChallenge {
  id: number;
  title: string;
  category: string;
  points: number;
}

interface FilteredChallenge {
  id: number;
  title: string;
  category: string;
}

interface ChallengeMappingPanelProps {
  mapEvent: CtfEvent;
  eventChallenges: EventChallenge[];
  filteredAll: FilteredChallenge[];
  challSearch: string;
  onChallSearch: (v: string) => void;
  onClose: () => void;
  addChallMutation: { mutate: (id: number) => void; isPending: boolean };
  removeChallMutation: { mutate: (id: number) => void; isPending: boolean };
}

export function ChallengeMappingPanel({
  mapEvent, eventChallenges, filteredAll, challSearch, onChallSearch,
  onClose, addChallMutation, removeChallMutation,
}: ChallengeMappingPanelProps) {
  return (
    <div className="g-card" style={{ marginTop: "1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h3 style={{ margin: 0, fontSize: "0.875rem", fontWeight: 600 }}>
          Challenges in <em>{mapEvent.title}</em>
        </h3>
        <Button size="sm" onClick={onClose} leftIcon={<X size={12} />}>
          Close
        </Button>
      </div>

      {eventChallenges.length === 0 ? (
        <p style={{ color: "var(--g-text-muted)", fontSize: "0.8125rem" }}>No challenges mapped yet.</p>
      ) : (
        <table className="g-table" style={{ marginBottom: "1rem" }}>
          <thead>
            <tr>
              <th>Challenge</th>
              <th>Category</th>
              <th>Points</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {eventChallenges.map((c) => (
              <tr key={c.id}>
                <td style={{ fontSize: "0.8125rem" }}>{c.title}</td>
                <td style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>{c.category}</td>
                <td style={{ fontSize: "0.75rem" }}>{c.points}</td>
                <td>
                  <Button
                    variant="danger"
                    size="sm"
                    disabled={removeChallMutation.isPending}
                    onClick={() => removeChallMutation.mutate(c.id)}
                  >
                    Remove
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ borderTop: "1px solid var(--g-border)", paddingTop: "1rem" }}>
        <p style={{ fontSize: "0.75rem", color: "var(--g-text-muted)", marginBottom: "0.5rem" }}>Add challenge:</p>
        <input
          className="g-input"
          placeholder="Search challenges…"
          value={challSearch}
          onChange={(e) => onChallSearch(e.target.value)}
          style={{ marginBottom: "0.5rem", width: 280 }}
        />
        <div style={{ maxHeight: 200, overflowY: "auto", display: "flex", flexDirection: "column", gap: 4 }}>
          {filteredAll.slice(0, 20).map((c) => (
            <div key={c.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.25rem 0" }}>
              <span style={{ fontSize: "0.8125rem" }}>
                {c.title}{" "}
                <span style={{ color: "var(--g-text-muted)", fontSize: "0.6875rem" }}>({c.category})</span>
              </span>
              <Button
                size="sm"
                disabled={addChallMutation.isPending}
                onClick={() => addChallMutation.mutate(c.id)}
              >
                + Add
              </Button>
            </div>
          ))}
          {filteredAll.length === 0 && (
            <p style={{ color: "var(--g-text-muted)", fontSize: "0.75rem" }}>All challenges added.</p>
          )}
        </div>
      </div>
    </div>
  );
}
