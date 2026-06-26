# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_types import EnumCol as SQLEnum
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class PackageType(str, enum.Enum):
    LAB_PACK = "lab_pack"
    CHALLENGE_PACK = "challenge_pack"
    EXERCISE = "exercise"


class MarketplacePackage(Base):
    __tablename__ = "marketplace_packages"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    package_type: Mapped[PackageType] = mapped_column(SQLEnum(PackageType), nullable=False)
    manifest: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String(128), nullable=True)
    signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    installations: Mapped[list["PackageInstallation"]] = relationship(
        back_populates="package", cascade="all, delete-orphan"
    )


class PackageInstallation(Base):
    __tablename__ = "package_installations"

    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[int] = mapped_column(
        ForeignKey("marketplace_packages.id"), nullable=False, index=True
    )
    installed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    installed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    package: Mapped["MarketplacePackage"] = relationship(back_populates="installations")
    installer: Mapped["User"] = relationship()
