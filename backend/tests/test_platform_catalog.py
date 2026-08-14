"""Tests for the multi-platform catalog refactor.

Covers platform classification metadata, the seller-supported business rule
(D2C never appears), and category-scoped participation.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.core.platform_types import PlatformCategory, SellerSupport
from app.db.seed.platform_config import PLATFORM_SPECS, PLATFORMS
from app.db.seed.seeder import seed_all
from app.models import FeeRule, Platform
from app.services.fee_engine import ComparisonEngine, ProductInput

TODAY = date(2026, 8, 5)

D2C_NAMES = {s.name for s in PLATFORM_SPECS if s.category is PlatformCategory.D2C}
SELLER_NAMES = {s.name for s in PLATFORM_SPECS if s.seller_supported}


def _compare(session, category, weight_g=400):
    engine = ComparisonEngine(session)
    results = engine.compare(
        ProductInput(category=category, cost_price=Decimal("450.00"),
                     selling_price=Decimal("999.00"), weight_g=weight_g),
        on_date=TODAY,
    )
    return {r.platform_name for r in results}


class TestConfigDerivation:
    def test_platforms_derived_from_specs(self):
        assert PLATFORMS == tuple(s.name for s in PLATFORM_SPECS)

    def test_ten_d2c_stores_present(self):
        assert len(D2C_NAMES) == 10

    def test_seller_support_participation_rule(self):
        assert SellerSupport.FULL.participates is True
        assert SellerSupport.PARTIAL.participates is True
        assert SellerSupport.LIMITED.participates is True
        assert SellerSupport.NONE.participates is False


class TestPlatformMetadata:
    def test_all_specs_seeded_with_metadata(self, db_session):
        seed_all(db_session)
        assert db_session.query(Platform).count() == len(PLATFORM_SPECS)
        amazon = db_session.scalar(select(Platform).where(Platform.name == "Amazon"))
        assert amazon.slug == "amazon-india"
        assert amazon.platform_category == "Marketplace"
        assert amazon.seller_supported is True
        assert amazon.website == "https://sellercentral.amazon.in"

    def test_d2c_marked_not_seller_supported_and_ruleless(self, db_session):
        seed_all(db_session)
        apple = db_session.scalar(
            select(Platform).where(Platform.name == "Apple Store India")
        )
        assert apple is not None                       # exists for extensibility
        assert apple.seller_supported is False
        rules = db_session.scalars(
            select(FeeRule).where(FeeRule.platform_id == apple.platform_id)
        ).all()
        assert rules == []                             # no seller fee rules


class TestSellerSupportedBusinessRule:
    def test_d2c_never_appears_in_comparison(self, db_session):
        seed_all(db_session)
        # Electronics category — many D2C brands sell electronics, but none may appear.
        participants = _compare(db_session, "Electronics")
        assert participants.isdisjoint(D2C_NAMES)

    def test_home_kitchen_preserves_amazon_and_flipkart(self, db_session):
        seed_all(db_session)
        participants = _compare(db_session, "Home & Kitchen")
        assert {"Amazon", "Flipkart"}.issubset(participants)
        assert participants.isdisjoint(D2C_NAMES)

    def test_category_scopes_participants(self, db_session):
        seed_all(db_session)
        # "Beauty" is served by beauty platforms only (Amazon uses a different
        # legacy category name), so Amazon must NOT appear here.
        participants = _compare(db_session, "Beauty")
        assert {"Nykaa", "Tira", "Purplle"}.issubset(participants)
        assert "Amazon" not in participants
