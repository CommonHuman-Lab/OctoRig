"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useRef, useState } from "react";
import { X } from "lucide-react";

export interface SearchableSelectOption {
  id: number;
  label: string;
}

interface SearchableSelectProps {
  options: SearchableSelectOption[];
  value: number | null;
  onChange: (id: number | null) => void;
  placeholder?: string;
}

export function SearchableSelect({ options, value, onChange, placeholder = "None" }: SearchableSelectProps) {
  const selected = options.find((o) => o.id === value) ?? null;
  const [query, setQuery] = useState(selected?.label ?? "");
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setQuery(selected?.label ?? "");
  }, [selected?.label]);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
        setQuery(selected?.label ?? "");
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [selected]);

  const filtered = query.trim()
    ? options.filter((o) => o.label.toLowerCase().includes(query.trim().toLowerCase()))
    : options;

  function handleSelect(option: SearchableSelectOption) {
    onChange(option.id);
    setQuery(option.label);
    setOpen(false);
  }

  function handleClear() {
    onChange(null);
    setQuery("");
    setOpen(false);
  }

  return (
    <div ref={containerRef} style={{ position: "relative" }}>
      <div style={{ position: "relative" }}>
        <input
          className="g-input"
          placeholder={placeholder}
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          autoComplete="off"
        />
        {selected && (
          <button
            type="button"
            onClick={handleClear}
            aria-label="Clear"
            style={{
              position: "absolute", right: "0.5rem", top: "50%", transform: "translateY(-50%)",
              background: "none", border: "none", cursor: "pointer", display: "flex",
              color: "var(--g-text-muted)", padding: 0,
            }}
          >
            <X size={13} />
          </button>
        )}
      </div>
      {open && filtered.length > 0 && (
        <div style={{
          position: "absolute", top: "100%", left: 0, right: 0, zIndex: "var(--z-popover)",
          background: "var(--g-chrome)", border: "1px solid var(--g-border)",
          borderRadius: "6px", marginTop: "2px", overflow: "auto", maxHeight: "12rem",
          boxShadow: "0 4px 12px rgba(0,0,0,0.45)",
        }}>
          {filtered.map((o) => (
            <div
              key={o.id}
              style={{
                padding: "0.4rem 0.6rem", cursor: "pointer", fontSize: "0.8125rem",
                color: "var(--g-text)",
              }}
              onMouseDown={() => handleSelect(o)}
              onMouseEnter={(e) => (e.currentTarget.style.background = "var(--g-surface-2)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "")}
            >
              {o.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
