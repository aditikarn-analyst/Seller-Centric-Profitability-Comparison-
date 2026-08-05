"""Idempotent database seeding.

Each seed function checks for an existing row before inserting, so running the
seed repeatedly is safe and never creates duplicates. Idempotency keys:

* platform      -> ``name``
* fee_rule      -> (platform, category, price_band_min, effective_from)
* rto_rate      -> (platform, category, effective_from)
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.seed import data
from app.models import FeeRule, Platform, RtoRate


def _get_or_create_platform(session: Session, name: str) -> Platform:
    platform = session.scalar(select(Platform).where(Platform.name == name))
    if platform is None:
        platform = Platform(name=name, is_active=True)
        session.add(platform)
        session.flush()  # assign platform_id for downstream FKs
    return platform


def seed_platforms(session: Session) -> int:
    inserted = 0
    for name in data.PLATFORMS:
        before = session.scalar(select(Platform).where(Platform.name == name))
        _get_or_create_platform(session, name)
        if before is None:
            inserted += 1
    return inserted


def seed_fee_rules(session: Session) -> int:
    inserted = 0
    for row in data.FEE_RULES:
        platform = _get_or_create_platform(session, row["platform"])
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
        platform = _get_or_create_platform(session, row["platform"])
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


def seed_all(session: Session) -> dict[str, int]:
    """Seed all reference data in dependency order and commit."""
    result = {
        "platforms_inserted": seed_platforms(session),
        "fee_rules_inserted": seed_fee_rules(session),
        "rto_rates_inserted": seed_rto_rates(session),
    }
    session.commit()
    return result
