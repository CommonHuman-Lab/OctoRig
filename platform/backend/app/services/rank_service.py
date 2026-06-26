# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab

from sqlalchemy.orm import Session

from app.models.rank import Rank

RANK_SEED = [
    {"name": "Recruit",      "min_points": 0,         "icon": "🐣",  "color": "#6b7280"},
    {"name": "Trainee",      "min_points": 100,        "icon": "🛡️", "color": "#64748b"},
    {"name": "Novice",       "min_points": 500,        "icon": "🎯",  "color": "#22c55e"},
    {"name": "Apprentice",   "min_points": 1_000,      "icon": "🔑",  "color": "#16a34a"},
    {"name": "Explorer",     "min_points": 2_500,      "icon": "🧭",  "color": "#3b82f6"},
    {"name": "Initiate",     "min_points": 5_000,      "icon": "🔓",  "color": "#2563eb"},
    {"name": "Hacker",       "min_points": 10_000,     "icon": "💻",  "color": "#a855f7"},
    {"name": "Specialist",   "min_points": 20_000,     "icon": "🧑‍💻", "color": "#9333ea"},
    {"name": "Operator",     "min_points": 35_000,     "icon": "⚡",  "color": "#f59e0b"},
    {"name": "Expert",       "min_points": 50_000,     "icon": "⚙️",  "color": "#d97706"},
    {"name": "Infiltrator",  "min_points": 75_000,     "icon": "👁️", "color": "#ef4444"},
    {"name": "Phantom",      "min_points": 100_000,    "icon": "👻",  "color": "#dc2626"},
    {"name": "Shadow",       "min_points": 150_000,    "icon": "🌙",  "color": "#ec4899"},
    {"name": "Ghost",        "min_points": 250_000,    "icon": "📡",  "color": "#db2777"},
    {"name": "Veteran",      "min_points": 400_000,    "icon": "💀",  "color": "#f97316"},
    {"name": "Elite",        "min_points": 600_000,    "icon": "🔥",  "color": "#ea580c"},
    {"name": "Master",       "min_points": 900_000,    "icon": "👑",  "color": "#eab308"},
    {"name": "Legend",       "min_points": 1_500_000,  "icon": "🏅",  "color": "#ca8a04"},
    {"name": "Grandmaster",  "min_points": 2_500_000,  "icon": "🏆",  "color": "#06b6d4"},
    {"name": "Apex",         "min_points": 5_000_000,  "icon": "🚀",  "color": "#0891b2"},
]

# Backfilled to emoji on startup for ranks still untouched by an admin (old seed used lucide names)
_LEGACY_ICONS = {
    "Recruit": "user", "Trainee": "shield", "Novice": "target", "Apprentice": "key",
    "Explorer": "compass", "Initiate": "unlock", "Hacker": "terminal", "Specialist": "code-2",
    "Operator": "zap", "Expert": "cpu", "Infiltrator": "eye", "Phantom": "ghost",
    "Shadow": "moon", "Ghost": "radar", "Veteran": "skull", "Elite": "flame",
    "Master": "crown", "Legend": "award", "Grandmaster": "trophy", "Apex": "octagon",
}


def get_rank_for_points(db: Session, points: int) -> Rank | None:
    return (
        db.query(Rank)
        .filter(Rank.is_active.is_(True), Rank.min_points <= points)
        .order_by(Rank.min_points.desc())
        .first()
    )


def get_next_rank(db: Session, points: int) -> Rank | None:
    return (
        db.query(Rank)
        .filter(Rank.is_active.is_(True), Rank.min_points > points)
        .order_by(Rank.min_points.asc())
        .first()
    )


def seed_ranks(db: Session) -> int:
    inserted = 0
    if db.query(Rank).count() == 0:
        for entry in RANK_SEED:
            db.add(Rank(**entry))
            inserted += 1
    else:
        new_icons = {entry["name"]: entry["icon"] for entry in RANK_SEED}
        for rank in db.query(Rank).all():
            legacy_icon = _LEGACY_ICONS.get(rank.name)
            if legacy_icon is not None and rank.icon == legacy_icon:
                rank.icon = new_icons[rank.name]
    db.commit()
    return inserted
