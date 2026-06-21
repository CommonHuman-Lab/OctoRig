"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { ReactNode } from "react";
import { X } from "lucide-react";

interface Props {
  title: ReactNode;
  onClose: () => void;
  footer?: ReactNode;
  children: ReactNode;
}

export function SheetShell({ title, onClose, footer, children }: Props) {
  return (
    <>
      <div className="g-backdrop" onClick={onClose} />
      <div className="ev-sheet">
        <div className="ev-sheet-header">
          <h2 style={{ margin: 0, fontSize: "1rem", fontWeight: 700 }}>{title}</h2>
          <button className="g-btn g-btn-ghost g-btn-sm" onClick={onClose}>
            <X size={14} />
          </button>
        </div>
        <div className="ev-sheet-body">{children}</div>
        {footer && <div className="ev-sheet-footer">{footer}</div>}
      </div>
    </>
  );
}
