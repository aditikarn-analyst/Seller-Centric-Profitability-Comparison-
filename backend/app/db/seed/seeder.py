"""Idempotent database seeding.

Platform metadata is upserted from ``PLATFORM_SPECS`` (create, or update the
classification columns on re-seed). Fee and RTO rules are inserted with the same
before-existence check as before, so seeding stays safe to run repeatedly.
Idempotency keys:

* platform      -> ``name`` (metadata refreshed each run)
* fee_rule      -> (platform, category, price_band_min, effective_from)
* rto_rate      -> (platform, category, effective_from)
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.seed import data
from app.db.seed.fee_components_seed import FEE_COMPONENTS
from app.db.seed.platform_config import PlatformSpec
from app.models import FeeComponent, FeeRule, Platform, RtoRate


def _upsert_platform(session: Session, spec: PlatformSpec) -> tuple[Platform, bool]:
    """Create the platform, or refresh its metadata if it already exists."""
    platform = session.scalar(select(Platform).where(Platform.name == spec.name))
    created = platform is None
    if platform is None:
        platform = Platform(name=spec.name)
        session.add(platform)

    platform.slug = spec.slug
    platform.platform_category = spec.category.value
    platform.business_model = spec.business_model
    platform.website = spec.website
    platform.seller_supported = spec.seller_supported
    if created:
        platform.is_active = True

    session.flush()  # assign platform_id for downstream FKs
    return platform, created


def _platform_by_name(session: Session, name: str) -> Platform:
    platform = session.scalar(select(Platform).where(Platform.name == name))
    if platform is None:  # pragma: no cover - platforms are seeded first
        raise ValueError(f"Platform '{name}' not seeded before its rules")
    return platform


def seed_platforms(session: Session) -> int:
    inserted = 0
    for spec in data.PLATFORM_SPECS:
        _, created = _upsert_platform(session, spec)
        if created:
            inserted += 1
    return inserted


def seed_fee_rules(session: Session) -> int:
    inserted = 0
    for row in data.FEE_RULES:
        platform = _platform_by_name(session, row["platform"])
        exists = session.scalar(
            select(FeeRule).where(
                FeeRule.platform_id == platform.platform_id,
                FeeRule.category == row["category"],
                FeeRule.price_band_min == row["price_band_min"],
                FeeRule.effective_from == row["effective_from"],
            )
        )
        if exists is not None:
            continue
        payload = {k: v for k, v in row.items() if k != "platform"}
        session.add(FeeRule(platform_id=platform.platform_id, **payload))
        inserted += 1
    return inserted


def seed_rto_rates(session: Session) -> int:
    inserted = 0
    for row in data.RTO_RATES:
        platform = _platform_by_name(session, row["platform"])
        exists = session.scalar(
            select(RtoRate).where(
                RtoRate.platform_id == platform.platform_id,
                RtoRate.category == row["category"],
                RtoRate.effective_from == row["effective_from"],
            )
        )
        if exists is not None:
            continue
        payload = {k: v for k, v in row.items() if k != "platform"}
        session.add(RtoRate(platform_id=platform.platform_id, **payload))
        inserted += 1
    return inserted


def seed_fee_components(session: Session) -> int:
    """Seed the normalized, source-verified fee components (Option A).

    Idempotency key: (platform, category, component_type, price_band_min,
    effective_from).
    """
    inserted = 0
    for row in FEE_COMPONENTS:
        platform = _platform_by_name(session, row["platform"])
        exists = session.scalar(
            select(FeeComponent).where(
                FeeComponent.platform_id == platform.platform_id,
                FeeComponent.category == row["category"],
                FeeComponent.component_type == row["component_type"],
                FeeComponent.price_band_min == row["price_band_min"],
                FeeComponent.effective_from == row["effective_from"],
            )
        )
        if exists is not None:
            continue
        payload = {k: v for k, v in row.items() if k != "platform"}
        session.add(FeeComponent(platform_id=platform.platform_id, **payload))
        inserted += 1
    return inserted


def seed_all(session: Session) -> dict[str, int]:
    """Seed all reference data in dependency order and commit."""
    result = {
        "platforms_inserted": seed_platforms(session),
        "fee_rules_inserted": seed_fee_rules(session),
        "rto_rates_inserted": seed_rto_rates(session),
        "fee_components_inserted": seed_fee_components(session),
    }
    session.commit()
    return result
