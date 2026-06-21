// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Save, Droplets, Snowflake } from "lucide-react";
import type { SiteSettings } from "@/lib/api/settings";
import { SettingToggle } from "./SettingToggle";
import { SettingRow } from "./SettingRow";
import { Button } from "@/components/ui/Button";

function toISOOrNull(val: string | null | undefined): string | null {
  if (!val) return null;
  try { return new Date(val).toISOString(); } catch { return null; }
}

function toLocalInput(val: string | null | undefined): string {
  if (!val) return "";
  try { return new Date(val).toISOString().slice(0, 16); } catch { return ""; }
}

export function ScoringSection({
  scoring,
  onChange,
  onSave,
  isPending,
}: {
  scoring: Partial<SiteSettings>;
  onChange: (patch: Partial<SiteSettings>) => void;
  onSave: () => void;
  isPending: boolean;
}) {
  return (
    <section className="admin-settings-section">
      <h2 className="admin-settings-section-title">Scoring</h2>

      <SettingToggle
        label="First Blood"
        description="Track and display who was the first solver on each challenge."
        checked={scoring.first_blood_enabled ?? true}
        onChange={(v) => onChange({ first_blood_enabled: v })}
      />

      <SettingToggle
        label={<><Droplets size={13} style={{ display: "inline", marginRight: 4, verticalAlign: "middle" }} />Dynamic Scoring</>}
        description="Points decrease as more players solve a challenge. First blood gets full points."
        checked={scoring.dynamic_scoring_enabled ?? false}
        onChange={(v) => onChange({ dynamic_scoring_enabled: v })}
      />

      {scoring.dynamic_scoring_enabled && (
        <>
          <SettingRow
            label="Decay Factor"
            description="Multiplier per solve (0.0–1.0). Lower = faster decay. Default 0.9."
            indent
            control={
              <input
                type="number"
                className="g-input"
                style={{ width: 100, textAlign: "right" }}
                min={0} max={1} step={0.05}
                value={scoring.dynamic_decay_factor ?? 0.9}
                onChange={(e) => onChange({ dynamic_decay_factor: parseFloat(e.target.value) })}
              />
            }
          />
          <SettingRow
            label="Minimum Floor (%)"
            description="Points never drop below this percentage of the base value. Default 10%."
            indent
            control={
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <input
                  type="number"
                  className="g-input"
                  style={{ width: 80, textAlign: "right" }}
                  min={1} max={100}
                  value={scoring.dynamic_min_floor_pct ?? 10}
                  onChange={(e) => onChange({ dynamic_min_floor_pct: parseInt(e.target.value) })}
                />
                <span style={{ color: "var(--g-text-muted)", fontSize: "0.8125rem" }}>%</span>
              </div>
            }
          />
        </>
      )}

      <SettingRow
        label={<><Snowflake size={13} style={{ display: "inline", marginRight: 4, verticalAlign: "middle" }} />Freeze Scoreboard At</>}
        description="Lock the global leaderboard display at this time. New solves still record but won't move rankings."
        control={
          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <input
              type="datetime-local"
              className="g-input"
              style={{ width: 200 }}
              value={toLocalInput(scoring.scoreboard_frozen_at)}
              onChange={(e) => onChange({ scoreboard_frozen_at: toISOOrNull(e.target.value) })}
            />
            {scoring.scoreboard_frozen_at && (
              <Button
                size="sm"
                onClick={() => onChange({ scoreboard_frozen_at: null })}
              >
                Clear
              </Button>
            )}
          </div>
        }
      />

      <div className="settings-row-actions">
        <Button
          variant="primary"
          size="sm"
          disabled={isPending}
          onClick={onSave}
          leftIcon={<Save size={13} />}
        >
          Save Scoring Settings
        </Button>
      </div>
    </section>
  );
}
