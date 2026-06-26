"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./notes.css";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { Search, NotebookPen } from "lucide-react";
import { NoteList } from "@/components/notes/NoteList";

export default function NotesPage() {
  const t = useTranslations("notes");
  const tn = useTranslations("nav");
  const [search, setSearch] = useState("");
  const [tag, setTag] = useState("");

  return (
    <div className="page">
      <div className="page-header page-header--top">
        <div>
          <h1 className="page-title font-mono">
            <NotebookPen size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
            {tn("notes")}
          </h1>
          <p className="page-sub">{t("subtitle")}</p>
        </div>
      </div>

      <div className="filter-bar">
        <div className="g-input-icon">
          <Search size={14} className="icon-left" />
          <input
            className="g-input"
            placeholder={t("searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <input
          className="g-input"
          style={{ maxWidth: "12rem" }}
          placeholder={t("filterByTagPlaceholder")}
          value={tag}
          onChange={(e) => setTag(e.target.value)}
        />
      </div>

      <NoteList
        filter={{ q: search || undefined, tag: tag || undefined }}
        emptyMessage={t("emptyMessage")}
      />
    </div>
  );
}
