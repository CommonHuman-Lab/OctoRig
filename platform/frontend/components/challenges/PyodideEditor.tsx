// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
"use client";
import { useRef, useState, useCallback } from "react";
import { Play, RotateCcw } from "lucide-react";
import { IconSpinner } from "@/components/ui/IconSpinner";

const PYODIDE_CDN = "https://cdn.jsdelivr.net/pyodide/v0.27.5/full/pyodide.js";

declare global {
  interface Window {
    loadPyodide: (opts?: Record<string, unknown>) => Promise<PyodideInterface>;
  }
}

interface PyodideInterface {
  runPythonAsync: (code: string) => Promise<unknown>;
  setStdout: (opts: { batched: (msg: string) => void }) => void;
  setStderr: (opts: { batched: (msg: string) => void }) => void;
}

type Status = "idle" | "loading" | "running" | "done" | "error";

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      // Already injected — wait for window.loadPyodide to appear
      const poll = setInterval(() => {
        if (typeof window.loadPyodide === "function") { clearInterval(poll); resolve(); }
      }, 50);
      return;
    }
    const s = document.createElement("script");
    s.src = src;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error("Failed to load Pyodide script"));
    document.head.appendChild(s);
  });
}

export function PyodideEditor({ starterCode }: { starterCode?: string }) {
  const [code, setCode] = useState(starterCode ?? "");
  const [output, setOutput] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const pyodideRef = useRef<PyodideInterface | null>(null);

  const appendOutput = useCallback((msg: string) => {
    setOutput((prev) => prev + msg + "\n");
  }, []);

  async function handleRun() {
    if (status === "loading" || status === "running") return;
    setOutput("");
    setStatus("running");

    try {
      if (!pyodideRef.current) {
        setStatus("loading");
        await loadScript(PYODIDE_CDN);
        const py = await window.loadPyodide();
        py.setStdout({ batched: appendOutput });
        py.setStderr({ batched: appendOutput });
        pyodideRef.current = py;
        setStatus("running");
      }

      await pyodideRef.current.runPythonAsync(code);
      setStatus("done");
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setOutput((prev) => prev + msg);
      setStatus("error");
    }
  }

  const isbusy = status === "loading" || status === "running";
  const outputEmpty = output === "";

  return (
    <div className="g-panel" style={{ height: "100%", minHeight: 420 }}>
      <div className="g-panel-header">
        <span style={{ fontSize: "0.6875rem", fontWeight: 600, color: "var(--g-text)", fontFamily: "var(--font-mono, monospace)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
          Python
        </span>
        <div style={{ display: "flex", gap: "0.375rem" }}>
          <button
            className="g-btn g-btn-sm"
            title="Clear output"
            onClick={() => { setOutput(""); setStatus("idle"); }}
            disabled={isbusy}
            style={{ padding: "0.2rem 0.5rem" }}
          >
            <RotateCcw size={11} />
          </button>
          <button
            className="g-btn g-btn-primary g-btn-sm"
            onClick={handleRun}
            disabled={isbusy}
          >
            {isbusy ? <IconSpinner size={12} /> : <Play size={12} />}
            {status === "loading" ? "Loading…" : "Run"}
          </button>
        </div>
      </div>

      <textarea
        className="g-input"
        value={code}
        onChange={(e) => setCode(e.target.value)}
        spellCheck={false}
        placeholder="# Write Python here…"
        style={{
          flex: 1,
          resize: "none",
          borderRadius: 0,
          border: "none",
          borderBottom: "1px solid var(--g-border)",
          fontFamily: "var(--font-mono, monospace)",
          fontSize: "0.8125rem",
          lineHeight: 1.6,
          minHeight: 220,
          padding: "0.75rem",
          background: "var(--g-surface)",
          outline: "none",
        }}
        onKeyDown={(e) => {
          // Ctrl/Cmd+Enter runs code
          if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            handleRun();
          }
          // Tab inserts spaces instead of blurring
          if (e.key === "Tab") {
            e.preventDefault();
            const el = e.currentTarget;
            const start = el.selectionStart;
            const end = el.selectionEnd;
            const next = code.substring(0, start) + "    " + code.substring(end);
            setCode(next);
            requestAnimationFrame(() => { el.selectionStart = el.selectionEnd = start + 4; });
          }
        }}
      />

      <pre
        style={{
          flex: 1,
          margin: 0,
          padding: "0.75rem",
          fontFamily: "var(--font-mono, monospace)",
          fontSize: "0.75rem",
          lineHeight: 1.5,
          overflowY: "auto",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          minHeight: 100,
          color: status === "error" ? "var(--g-danger)" : "var(--g-text-secondary)",
          background: "var(--g-surface-2, var(--g-surface))",
        }}
      >
        {outputEmpty && status === "idle"
          ? <span style={{ color: "var(--g-text-muted)", fontStyle: "italic" }}>▶ Press Run to execute — Python runtime loads on first run (~6 MB)</span>
          : outputEmpty && status === "loading"
          ? <span style={{ color: "var(--g-text-muted)" }}>Loading Python runtime…</span>
          : output || " "}
      </pre>
    </div>
  );
}
