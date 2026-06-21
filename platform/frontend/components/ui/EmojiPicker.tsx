"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useRef, useState } from "react";
import { Button } from "./Button";

const EMOJI_OPTIONS = [
  "🐣", "🐛", "🔍", "🛡️", "⚔️", "🏹", "🔥", "⚡",
  "💀", "👾", "🕵️", "🦅", "🐉", "🦂", "🐺", "🦁",
  "👑", "🥇", "🥈", "🥉", "🏆", "🎯", "🧠", "💎",
  "🚀", "⭐", "💥", "🔓", "🔑", "🧨", "☠️", "👻",
  "🐍", "🕷️", "🦎", "🐙", "🦈", "🐊", "🦇", "🪰",
  "🧌", "🤖", "🎃", "🧟", "💊", "🦾", "🛰️", "🔭",
  "💻", "🖥️", "📡", "🛠️", "⚙️", "🔬", "🧪", "🧬",
  "📦", "🗝️", "🔐", "🔒", "🚨", "🛑", "⚠️", "📛",
  "🐲", "🦖", "🦴", "🩸", "🧊", "🌪️", "🌋", "🌩️",
  "💣", "🪓", "🗡️", "🔫", "🎲", "🃏", "♠️", "♣️",
  "🐯", "🐆", "🦊", "🐗", "🦏", "🦣", "🐻", "🦉",
  "🦋", "🐝", "🐞", "🦗", "🕸️", "🪲", "🐜", "🦟",
];

export function EmojiPicker({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    if (open) document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, [open]);

  return (
    <div className="emoji-picker" ref={ref}>
      <Button
        type="button"
        variant="ghost"
        className="emoji-picker-trigger"
        onClick={() => setOpen((o) => !o)}
      >
        <span className="emoji-picker-preview">{value || "🙂"}</span>
        <span className="text-11 text-muted">{value ? "Change icon" : "Choose icon"}</span>
      </Button>

      {open && (
        <div className="emoji-picker-popover">
          <div className="emoji-picker-grid">
            {EMOJI_OPTIONS.map((e) => (
              <button
                key={e}
                type="button"
                className={`emoji-picker-cell ${value === e ? "emoji-picker-cell--active" : ""}`}
                onClick={() => { onChange(e); setOpen(false); }}
                title={e}
              >
                {e}
              </button>
            ))}
          </div>
          {value && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="emoji-picker-clear"
              onClick={() => { onChange(""); setOpen(false); }}
            >
              Clear
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
