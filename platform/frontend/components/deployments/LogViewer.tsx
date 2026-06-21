"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useRef, useEffect, useState } from "react";
import { Download, Trash2, Wifi, WifiOff } from "lucide-react";
import { useLogStream } from "@/hooks/useLogStream";
import { Button } from "@/components/ui/Button";

interface Props {
  deploymentId: number;
  containerNames: string[];
}

export function LogViewer({ deploymentId, containerNames }: Props) {
  const [selectedContainer, setSelectedContainer] = useState("app");
  const [filterText, setFilterText] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const userScrolledUp = useRef(false);

  const roles = containerNames.map((name) => {
    const parts = name.split("-");
    return parts[parts.length - 1] ?? name;
  });

  const { lines, connected, clearLines } = useLogStream({
    deploymentId,
    container: selectedContainer,
    tail: 100,
    enabled: true,
  });

  const filteredLines = filterText
    ? lines.filter((l) => l.toLowerCase().includes(filterText.toLowerCase()))
    : lines;

  // block/inline: "nearest" avoids "start" alignment scrolling the whole page on every new line
  useEffect(() => {
    if (!filterText && !userScrolledUp.current) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
    }
  }, [lines, filterText]);

  useEffect(() => {
    if (!filterText) {
      userScrolledUp.current = false;
      bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
    }
  }, [filterText]);

  function downloadLogs() {
    const blob = new Blob([lines.join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `octorig-${deploymentId}-${selectedContainer}.log`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function highlightMatch(line: string) {
    if (!filterText) return line;
    const idx = line.toLowerCase().indexOf(filterText.toLowerCase());
    if (idx === -1) return line;
    return (
      <>
        {line.slice(0, idx)}
        <mark style={{ background: "var(--g-warning)", color: "var(--g-bg)", borderRadius: "2px" }}>
          {line.slice(idx, idx + filterText.length)}
        </mark>
        {line.slice(idx + filterText.length)}
      </>
    );
  }

  return (
    <div className="log-viewer">
      <div className="log-toolbar">
        {/* Container selector */}
        {roles.length > 1 && (
          <select
            className="g-select"
            value={selectedContainer}
            onChange={(e) => setSelectedContainer(e.target.value)}
          >
            {roles.map((role) => (
              <option key={role} value={role}>{role}</option>
            ))}
          </select>
        )}

        {/* Filter input */}
        <input
          className="g-input log-filter"
          placeholder="Filter logs…"
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
          spellCheck={false}
        />
        {filterText && (
          <span className="log-filter-count">
            {filteredLines.length} match{filteredLines.length !== 1 ? "es" : ""}
          </span>
        )}

        <div className="log-toolbar-actions">
          <span className="log-status">
            {connected
              ? <><Wifi size={12} className="text-success" /> connected</>
              : <><WifiOff size={12} className="text-muted" /> disconnected</>
            }
          </span>
          <Button icon leftIcon={<Trash2 size={14} />} onClick={clearLines} tooltip="Clear" />
          <Button icon leftIcon={<Download size={14} />} onClick={downloadLogs} tooltip="Download" />
        </div>
      </div>

      <div
        className="log-body"
        onScroll={(e) => {
          const el = e.currentTarget;
          userScrolledUp.current = el.scrollTop + el.clientHeight < el.scrollHeight - 20;
        }}
      >
        {filteredLines.length === 0 ? (
          <span className="log-empty">
            {lines.length === 0 ? "Waiting for logs…" : "No lines match filter."}
          </span>
        ) : (
          filteredLines.map((line, i) => (
            <div key={i} className="log-line">{highlightMatch(line)}</div>
          ))
        )}
        <div ref={bottomRef} />
      </div>

      <style>{`
        .log-viewer { display: flex; flex-direction: column; height: 100%; }
        .log-toolbar { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; border-bottom: 1px solid var(--g-border); background: var(--g-raised); flex-wrap: wrap; }
        .log-filter { flex: 1; min-width: 8rem; max-width: 16rem; font-size: 0.7rem; padding: 0.2rem 0.5rem; height: 1.75rem; }
        .log-filter-count { font-size: 0.65rem; color: var(--g-text-muted); white-space: nowrap; }
        .log-toolbar-actions { display: flex; align-items: center; gap: 0.25rem; margin-left: auto; }
        .log-status { display: flex; align-items: center; gap: 0.25rem; font-size: 0.625rem; color: var(--g-text-muted); }
        .log-body { flex: 1; overflow-y: auto; padding: 0.75rem; background: var(--g-code-bg); font-family: var(--font-mono); font-size: 0.7rem; line-height: 1.6; color: var(--g-text-secondary); }
        .log-line { white-space: pre-wrap; word-break: break-all; }
        .log-empty { color: var(--g-text-muted); }
      `}</style>
    </div>
  );
}
