"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../profile.css";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft, MapPin, Globe, Link2,
  Trophy, Target, Droplets, Users, Pencil,
} from "lucide-react";
import { getUserProfile, type UserProfile } from "@/lib/api/profiles";
import { getUserRank, type UserRank } from "@/lib/api/ranks";
import { formatDate } from "@/lib/utils/date";
import { useUserStore } from "@/stores/user.store";
import { ICON_MAP } from "@/lib/utils/badge-icons";
import { EditProfileSheet } from "@/components/profile/EditProfileSheet";

function StatBlock({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="stat-block">
      <div className="stat-icon">{icon}</div>
      <div className="profile-stat-value">{value.toLocaleString()}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function ProfileView({ profile, rankData }: { profile: UserProfile; rankData?: UserRank }) {
  const initials = profile.username.slice(0, 2).toUpperCase();

  return (
    <div className="profile-layout">
      {/* Left sidebar */}
      <aside className="profile-aside">
        <div className="avatar-wrap">
          {profile.avatar_url
            ? <img src={profile.avatar_url} alt={profile.username} className="avatar-img" />
            : <div className="avatar-placeholder">{initials}</div>
          }
        </div>
        <h1 className="profile-username">{profile.username}</h1>
        {rankData?.rank && (
          <div style={{ marginBottom: "0.5rem" }}>
            <span
              style={{
                display: "inline-block",
                padding: "0.15rem 0.6rem",
                borderRadius: 99,
                fontSize: "0.65rem",
                fontFamily: "var(--font-mono, monospace)",
                fontWeight: 600,
                border: `1px solid ${rankData.rank.color ?? "var(--g-border)"}`,
                color: rankData.rank.color ?? "var(--g-text-muted)",
              }}
            >
              {rankData.rank.name}
            </span>
          </div>
        )}
        {profile.bio && <p className="profile-bio">{profile.bio}</p>}

        <div className="profile-links">
          {profile.location && (
            <span className="profile-link-item"><MapPin size={12} />{profile.location}</span>
          )}
          {profile.website_url && (
            <a href={profile.website_url} className="profile-link-item profile-link" target="_blank" rel="noopener">
              <Globe size={12} />{profile.website_url.replace(/^https?:\/\//, "")}
            </a>
          )}
          {profile.github_handle && (
            <a href={`https://github.com/${profile.github_handle}`} className="profile-link-item profile-link" target="_blank" rel="noopener">
              <Link2 size={12} />@{profile.github_handle}
            </a>
          )}
        </div>
      </aside>

      {/* Main content */}
      <div className="profile-main">
        {/* Stats row */}
        <div className="stats-row g-card">
          <StatBlock icon={<Trophy size={16} />} label="Points" value={profile.total_points} />
          <StatBlock icon={<Target size={16} />} label="Solves" value={profile.solve_count} />
          <StatBlock icon={<Droplets size={16} />} label="First Bloods" value={profile.first_bloods} />
          <StatBlock icon={<Users size={16} />} label="Teams" value={profile.team_count} />
        </div>

        {/* Badges */}
        {profile.badges.length > 0 && (
          <section className="g-card">
            <h2 className="section-title">Badges</h2>
            <div className="badge-row">
              {profile.badges.map((b) => (
                <div key={b.slug} className="g-badge g-badge--accent" title={b.name}>
                  <span>{ICON_MAP[b.icon] ?? "🏅"}</span>
                  <span>{b.name}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Recent solves */}
        {profile.recent_solves.length > 0 && (
          <section className="g-card">
            <h2 className="section-title">Recent Solves</h2>
            <div className="solves-list">
              {profile.recent_solves.map((s, i) => (
                <div key={i} className="solve-row">
                  <Link href={`/challenges/${s.challenge_slug}`} className="solve-title">
                    {s.challenge_title}
                  </Link>
                  <span className="solve-pts">+{s.points_awarded} pts</span>
                  {s.is_first_blood && <span className="solve-fb">🩸 First Blood</span>}
                  <span className="solve-date">
                    {formatDate(s.submitted_at)}
                  </span>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export default function UserProfilePage() {
  const { username } = useParams<{ username: string }>();
  const { user } = useUserStore();
  const isOwnProfile = user?.username === username;
  const [editOpen, setEditOpen] = useState(false);

  const { data: profile, isLoading, isError } = useQuery({
    queryKey: ["profile", username],
    queryFn: () => getUserProfile(username),
  });

  const { data: rankData } = useQuery({
    queryKey: ["rank", "user", profile?.user_id],
    queryFn: () => getUserRank(profile!.user_id),
    enabled: !!profile,
    staleTime: 60_000,
  });

  return (
    <div className="page">
      <div className="page-header">
        <Link href="/" className="back-link">
          <ArrowLeft size={14} />
          <span>Back</span>
        </Link>
        {isOwnProfile && (
          <button
            className="g-btn g-btn-ghost g-btn-sm"
            style={{ display: "inline-flex", alignItems: "center", gap: "0.4rem" }}
            onClick={() => setEditOpen(true)}
          >
            <Pencil size={13} />
            Edit Profile
          </button>
        )}
      </div>

      {isLoading && <div className="text-muted text-sm">Loading profile…</div>}
      {isError && <div className="text-muted text-sm">Profile not found.</div>}
      {profile && <ProfileView profile={profile} rankData={rankData} />}

      {isOwnProfile && (
        <EditProfileSheet open={editOpen} profile={profile} onClose={() => setEditOpen(false)} />
      )}
    </div>
  );
}
