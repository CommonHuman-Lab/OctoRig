"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Save } from "lucide-react";
import { listRoles } from "@/lib/api/admin";
import { useEscapeKey } from "@/hooks/useEscapeKey";
import { SheetShell } from "@/components/ui/SheetShell";

export function CreateUserForm({
  open,
  onSubmit,
  onClose,
  isPending,
}: {
  open: boolean;
  onSubmit: (username: string, email: string, password: string, roles: string[]) => void;
  onClose: () => void;
  isPending: boolean;
}) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [roles, setRoles] = useState<string[]>([]);

  const { data: availableRoles = [] } = useQuery({
    queryKey: ["admin-roles"],
    queryFn: listRoles,
  });

  useEscapeKey(onClose, open);

  if (!open) return null;

  function toggleRole(slug: string) {
    setRoles((r) => (r.includes(slug) ? r.filter((s) => s !== slug) : [...r, slug]));
  }

  function handleSubmit() {
    onSubmit(username, email, password, roles);
    setUsername("");
    setEmail("");
    setPassword("");
    setRoles([]);
  }

  return (
    <SheetShell
      title="New User"
      onClose={onClose}
      footer={
        <>
          <button className="g-btn g-btn-ghost" onClick={onClose}>Cancel</button>
          <button
            className="g-btn g-btn-primary"
            onClick={handleSubmit}
            disabled={!username || !email || !password || isPending}
          >
            <Save size={13} />
            {isPending ? "Creating…" : "Create User"}
          </button>
        </>
      }
    >
          <label className="ev-field">
            <span className="ev-label">Username</span>
            <input
              className="g-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="username"
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">Email</span>
            <input
              className="g-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@example.com"
            />
          </label>

          <label className="ev-field">
            <span className="ev-label">Password</span>
            <input
              className="g-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Initial password"
            />
          </label>

          <div className="ev-field">
            <span className="ev-label">Roles</span>
            {availableRoles.map((role) => (
              <label key={role.slug} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={roles.includes(role.slug)}
                  onChange={() => toggleRole(role.slug)}
                />
                <span className="text-sm">{role.display_name}</span>
              </label>
            ))}
          </div>
    </SheetShell>
  );
}
