"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bold, Italic, Heading2, Code, CodeSquare, Link, List, ListOrdered, Quote } from "lucide-react";
import { Button } from "./Button";

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  minHeight?: number;
  disabled?: boolean;
  fill?: boolean;
}

function insertWrap(
  el: HTMLTextAreaElement,
  setValue: (v: string) => void,
  prefix: string,
  suffix: string,
  fallback: string,
) {
  const { selectionStart: s, selectionEnd: e, value } = el;
  const selected = value.slice(s, e) || fallback;
  const next = value.slice(0, s) + prefix + selected + suffix + value.slice(e);
  setValue(next);
  requestAnimationFrame(() => {
    el.focus();
    el.setSelectionRange(s + prefix.length, s + prefix.length + selected.length);
  });
}

function insertPrefix(
  el: HTMLTextAreaElement,
  setValue: (v: string) => void,
  prefix: string,
) {
  const { selectionStart: s, value } = el;
  const lineStart = value.lastIndexOf("\n", s - 1) + 1;
  const next = value.slice(0, lineStart) + prefix + value.slice(lineStart);
  setValue(next);
  requestAnimationFrame(() => {
    el.focus();
    el.setSelectionRange(s + prefix.length, s + prefix.length);
  });
}

export function MarkdownEditor({
  value,
  onChange,
  placeholder = "Write markdown…",
  minHeight = 160,
  disabled = false,
  fill = false,
}: MarkdownEditorProps) {
  const [tab, setTab] = useState<"write" | "preview">("write");
  const ref = useRef<HTMLTextAreaElement>(null);

  const wrap = (pre: string, suf: string, fallback: string) =>
    ref.current && insertWrap(ref.current, onChange, pre, suf, fallback);
  const pfx = (str: string) =>
    ref.current && insertPrefix(ref.current, onChange, str);

  const tools = [
    { icon: <Bold size={13} />,         title: "Bold",          action: () => wrap("**", "**", "bold text") },
    { icon: <Italic size={13} />,       title: "Italic",        action: () => wrap("*", "*", "italic text") },
    { icon: <Heading2 size={13} />,     title: "Heading",       action: () => pfx("## ") },
    { icon: <Code size={13} />,         title: "Inline code",   action: () => wrap("`", "`", "code") },
    { icon: <CodeSquare size={13} />,   title: "Code block",    action: () => wrap("```\n", "\n```", "code") },
    { icon: <Link size={13} />,         title: "Link",          action: () => wrap("[", "](url)", "link text") },
    { icon: <List size={13} />,         title: "Bullet list",   action: () => pfx("- ") },
    { icon: <ListOrdered size={13} />,  title: "Ordered list",  action: () => pfx("1. ") },
    { icon: <Quote size={13} />,        title: "Blockquote",    action: () => pfx("> ") },
  ];

  return (
    <div
      className="md-editor"
      style={fill ? { display: "flex", flexDirection: "column", flex: 1, minHeight: 0 } : undefined}
    >
      <div className="md-editor-bar">
        <div className="md-editor-tabs">
          <Button
            type="button"
            size="sm"
            variant={tab === "write" ? "primary" : "ghost"}
            onClick={() => setTab("write")}
          >
            Write
          </Button>
          <Button
            type="button"
            size="sm"
            variant={tab === "preview" ? "primary" : "ghost"}
            onClick={() => setTab("preview")}
          >
            Preview
          </Button>
        </div>
        {tab === "write" && (
          <div className="md-editor-toolbar">
            {tools.map((t) => (
              <button
                key={t.title}
                type="button"
                className="md-toolbar-btn"
                title={t.title}
                disabled={disabled}
                onClick={t.action}
              >
                {t.icon}
              </button>
            ))}
          </div>
        )}
      </div>

      {tab === "write" ? (
        <textarea
          ref={ref}
          className="g-input md-editor-textarea"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          style={{
            minHeight,
            resize: "vertical",
            fontFamily: "var(--font-mono, monospace)",
            fontSize: "0.8125rem",
            ...(fill ? { flex: 1 } : undefined),
          }}
          spellCheck={false}
        />
      ) : (
        <div
          className="md-preview"
          style={{ minHeight, overflowY: "auto", ...(fill ? { flex: 1 } : undefined) }}
        >
          {value ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{value}</ReactMarkdown>
          ) : (
            <p className="md-preview-empty">Nothing to preview.</p>
          )}
        </div>
      )}
    </div>
  );
}
