# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SiteSettings(Base):
    __tablename__ = "site_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)

    # Platform
    registration_open: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    maintenance_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    maintenance_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_flag_attempts: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Scoring
    dynamic_scoring_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dynamic_decay_factor: Mapped[float] = mapped_column(Float, nullable=False, default=0.9)
    dynamic_min_floor_pct: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    scoreboard_frozen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    first_blood_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Features
    python_editor_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    hide_lab_ports: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Branding
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_theme: Mapped[str | None] = mapped_column(String(32), nullable=True)
    default_locale: Mapped[str | None] = mapped_column(String(8), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
