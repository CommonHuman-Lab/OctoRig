"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useConfirmStore } from "@/stores/confirm.store";
import { AlertTriangle } from "lucide-react";
import { Button } from "./Button";

export function ConfirmModal() {
  const { pending, resolve } = useConfirmStore();
  if (!pending) return null;

  const label = pending.confirmLabel ?? (pending.dangerous ? "Delete" : "Confirm");

  return (
    <div className="confirm-overlay" onClick={() => resolve(false)}>
      <div className="confirm-modal" onClick={(e) => e.stopPropagation()}>
        <div className="confirm-header">
          {pending.dangerous && (
            <AlertTriangle size={15} style={{ color: "var(--g-danger)", flexShrink: 0 }} />
          )}
          <span className="confirm-title">{pending.title}</span>
        </div>

        {pending.body && (
          <p className="confirm-body">{pending.body}</p>
        )}

        <div className="confirm-actions">
          <Button onClick={() => resolve(false)}>
            Cancel
          </Button>
          <Button
            variant={pending.dangerous ? "danger" : "primary"}
            onClick={() => resolve(true)}
          >
            {label}
          </Button>
        </div>
      </div>

      <style>{`
        .confirm-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0,0,0,0.55);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        .confirm-modal {
          background: var(--g-chrome);
          border: 1px solid var(--g-border);
          border-radius: 8px;
          padding: 1.5rem;
          width: min(420px, 95vw);
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .confirm-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        .confirm-title {
          font-size: 0.9rem;
          font-weight: 700;
          font-family: var(--font-mono, monospace);
          color: var(--g-text);
        }
        .confirm-body {
          font-size: 0.8125rem;
          color: var(--g-text-secondary);
          line-height: 1.5;
          margin: 0;
        }
        .confirm-actions {
          display: flex;
          justify-content: flex-end;
          gap: 0.5rem;
          margin-top: 0.25rem;
        }
      `}</style>
    </div>
  );
}
