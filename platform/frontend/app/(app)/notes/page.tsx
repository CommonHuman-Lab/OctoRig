"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./notes.css";

import { useState } from "react";
import { Search, NotebookPen } from "lucide-react";
import { NoteList } from "@/components/notes/NoteList";

export default function NotesPage() {
  const [search, setSearch] = useState("");
  const [tag, setTag] = useState("");

  return (
    <div className="page">
      <div className="page-header page-header--top">
        <div>
          <h1 className="page-title font-mono">
            <NotebookPen size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
            Notes
          </h1>
          <p className="page-sub">Personal notes — optionally linked to a lab or challenge, exportable as markdown anytime.</p>
        </div>
      </div>

      <div className="filter-bar">
        <div className="g-input-icon">
          <Search size={14} className="icon-left" />
          <input
            className="g-input"
            placeholder="Search notes…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <input
          className="g-input"
          style={{ maxWidth: "12rem" }}
          placeholder="Filter by tag…"
          value={tag}
          onChange={(e) => setTag(e.target.value)}
        />
      </div>

      <NoteList
        filter={{ q: search || undefined, tag: tag || undefined }}
        emptyMessage="No notes yet. Create one to start keeping track of what you find."
      />
    </div>
  );
}
