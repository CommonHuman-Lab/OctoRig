# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import hashlib
import io
import json
import zipfile
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import bad_request, conflict, not_found
from app.models.marketplace import MarketplacePackage, PackageInstallation, PackageType
from app.services import audit_service

# ── Manifest schema (loose validation) ───────────────────────────────────────

_REQUIRED_MANIFEST_FIELDS = ("name", "slug", "version", "type")


def _parse_manifest(data: bytes) -> dict[str, Any]:
    try:
        manifest = json.loads(data)
    except ValueError as exc:
        raise bad_request(f"Invalid manifest.json: {exc}")
    missing = [f for f in _REQUIRED_MANIFEST_FIELDS if f not in manifest]
    if missing:
        raise bad_request(f"manifest.json missing required fields: {missing}")
    return manifest


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _verify_ed25519(zip_bytes: bytes, signature_hex: str, public_key_hex: str) -> bool:
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        pub.verify(bytes.fromhex(signature_hex), zip_bytes)
        return True
    except Exception:
        return False


# ── Install flow ──────────────────────────────────────────────────────────────

def install_package(
    db: Session,
    zip_bytes: bytes,
    installed_by_id: int,
) -> MarketplacePackage:
    from app.config import settings

    trusted_keys = settings.get_marketplace_trusted_keys()
    if not trusted_keys:
        raise bad_request(
            "Marketplace installation is disabled: no trusted keys are configured. "
            "Set MARKETPLACE_TRUSTED_KEYS in your environment."
        )

    checksum = _sha256(zip_bytes)

    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        raise bad_request("Uploaded file is not a valid ZIP archive")

    names = zf.namelist()
    if "manifest.json" not in names:
        raise bad_request("ZIP must contain manifest.json at root")

    manifest = _parse_manifest(zf.read("manifest.json"))

    # Mandatory Ed25519 signature verification against all configured trusted keys.
    if "signature.sig" not in names:
        raise bad_request("Package must include a signature.sig file signed with a trusted key")

    signature_hex = zf.read("signature.sig").decode().strip()
    is_verified = any(_verify_ed25519(zip_bytes, signature_hex, key) for key in trusted_keys)
    if not is_verified:
        raise bad_request("Package signature verification failed against all configured trusted keys")

    slug = manifest["slug"]
    existing = db.query(MarketplacePackage).filter(MarketplacePackage.slug == slug).first()
    if existing:
        raise conflict(f"Package '{slug}' is already installed")

    try:
        pkg_type = PackageType(manifest["type"])
    except ValueError:
        raise bad_request(f"Unknown package type: {manifest['type']!r}")

    pkg = MarketplacePackage(
        slug=slug,
        name=manifest["name"],
        version=manifest["version"],
        package_type=pkg_type,
        manifest=manifest,
        description=manifest.get("description"),
        author=manifest.get("author"),
        signature=signature_hex,
        checksum=checksum,
        is_verified=is_verified,
    )
    db.add(pkg)
    db.flush()

    if pkg_type == PackageType.CHALLENGE_PACK and "challenges" in manifest:
        _import_challenges(db, manifest["challenges"], pkg)

    installation = PackageInstallation(
        package_id=pkg.id,
        installed_by=installed_by_id,
    )
    db.add(installation)
    db.commit()
    db.refresh(pkg)

    audit_service.write_audit(
        db,
        action=audit_service.MARKETPLACE_INSTALLED,
        user_id=installed_by_id,
        detail={"slug": slug, "version": manifest["version"], "verified": is_verified},
    )
    return pkg


def _import_challenges(db: Session, challenges: list[dict], pkg: MarketplacePackage) -> None:
    from app.models.challenge import (
        Challenge,
        ChallengeDifficulty,
        ChallengeFlag,
        ChallengeHint,
        ChallengeType,
        FlagType,
    )
    for ch_dict in challenges:
        slug = ch_dict.get("slug") or f"{pkg.slug}-{ch_dict.get('id', '')}"
        if db.query(Challenge).filter(Challenge.slug == slug).first():
            continue

        ch = Challenge(
            slug=slug,
            title=ch_dict.get("title", "Untitled"),
            description=ch_dict.get("description", ""),
            challenge_type=ChallengeType(ch_dict.get("challenge_type", "flag")),
            difficulty=ChallengeDifficulty(ch_dict.get("difficulty", "medium")),
            category=ch_dict.get("category", pkg.manifest.get("category", "general")),
            tags=ch_dict.get("tags", []),
            skills=ch_dict.get("skills", []),
            points=ch_dict.get("points", 100),
            estimated_minutes=ch_dict.get("estimated_minutes"),
            content=ch_dict.get("content", {}),
            is_active=True,
            is_archived=False,
            version=1,
        )
        db.add(ch)
        db.flush()

        for flag_val in ch_dict.get("flags", []):
            db.add(ChallengeFlag(
                challenge_id=ch.id,
                flag_type=FlagType.STATIC,
                value=flag_val,
                case_sensitive=True,
            ))

        for i, hint_text in enumerate(ch_dict.get("hints", []), 1):
            db.add(ChallengeHint(
                challenge_id=ch.id,
                order_num=i,
                content=hint_text,
                cost=0,
            ))


# ── Uninstall ─────────────────────────────────────────────────────────────────

def uninstall_package(db: Session, package_id: int, user_id: int) -> None:
    pkg = db.get(MarketplacePackage, package_id)
    if pkg is None:
        raise not_found("Package")
    db.delete(pkg)
    db.commit()
    audit_service.write_audit(
        db,
        action=audit_service.MARKETPLACE_UNINSTALLED,
        user_id=user_id,
        detail={"slug": pkg.slug},
    )


# ── List ──────────────────────────────────────────────────────────────────────

def list_packages(db: Session) -> list[MarketplacePackage]:
    return db.query(MarketplacePackage).order_by(MarketplacePackage.created_at.desc()).all()
