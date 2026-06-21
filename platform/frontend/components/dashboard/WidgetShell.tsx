"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { ReactNode } from "react";
import { GripVertical, X } from "lucide-react";
import { Button } from "@/components/ui/Button";
import type { WidgetCategory, WidgetHeight, WidgetInstance } from "@/lib/widgets/types";

interface Props {
  widget: WidgetInstance;
  category: WidgetCategory;
  customizing: boolean;
  onRemove: () => void;
  onSetHeight?: (height: WidgetHeight) => void;
  children: ReactNode;
}

const HEIGHTS: WidgetHeight[] = ["sm", "md", "lg"];

export function WidgetShell({ widget, category, customizing, onRemove, onSetHeight, children }: Props) {
  if (!customizing) return <>{children}</>;

  return (
    <div className="dash-widget-edit">
      <div className="dash-widget-toolbar">
        <GripVertical size={13} className="dash-widget-grip" />
        {category === "panel" && onSetHeight && (
          <div className="dash-widget-heights">
            {HEIGHTS.map((h) => (
              <button
                key={h}
                type="button"
                className={`dash-height-btn ${widget.height === h ? "active" : ""}`}
                onClick={() => onSetHeight(h)}
                title={`${h} height`}
              >
                {h.toUpperCase()}
              </button>
            ))}
          </div>
        )}
        <Button size="sm" icon leftIcon={<X size={12} />} variant="danger-ghost" onClick={onRemove} tooltip="Remove widget" />
      </div>
      {children}
    </div>
  );
}
