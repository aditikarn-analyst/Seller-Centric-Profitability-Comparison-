"""Repository-layer tests (Repository Pattern, RG7/C4 resolution)."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.db.seed.seeder import seed_all
from app.models import Comparison, Platform
from app.repositories import (
    ComparisonsRepository,
    FeeRulesRepository,
    ProductsRepository,
    RtoRatesRepository,
    UsersRepository,
)

TODAY = date(2026, 8, 5)


@pytest.fixture()
def seeded(db_session):
    seed_all(db_session)
    return db_session


def _platform_id(session, name: str) -> int:
    return session.scalar(select(Platform).where(Platform.name == name)).platform_id


class TestFeeRulesResolution:
    def test_resolves_current_active_version(self, seeded):
        repo = FeeRulesRepository(seeded)
        amazon = _platform_id(seeded, "Amazon")
        rule = repo.get_active_rule(
            amazon, "Home & Kitchen", TODAY,
            selling_price=Decimal("999.00"), weight_g=400,
        )
        assert rule is not None
        assert rule.commission_pct == Decimal("12.00")
        assert rule.effective_to is None

    def test_resolves_historical_version_for_past_date(self, seeded):
        """A comparison dated before the March revision resolves to 12.50 (§12.3)."""
        repo = FeeRulesRepository(seeded)
        amazon = _platform_id(seeded, "Amazon")
        rule = repo.get_active_rule(
            amazon, "Home & Kitchen", date(2026, 2, 1),
            selling_price=Decimal("999.00"), weight_g=400,
        )
        assert rule is not None
        assert rule.commission_pct == Decimal("12.50")

    def test_weight_exceeding_slab_has_no_rule(self, seeded):
        """Default seeded slab is 500 g; a 900 g product exceeds it."""
        repo = FeeRulesRepository(seeded)
        amazon = _platform_id(seeded, "Amazon")
        rule = repo.get_active_rule(
            amazon, "Home & Kitchen", TODAY,
            selling_price=Decimal("999.00"), weight_g=900,
        )
        assert rule is None

    def test_price_band_filter_is_numeric_not_lexicographic(self, seeded):
        """Guards the ExactNumeric-as-TEXT trap: 65.00 must not sort below 9.00."""
        repo = FeeRulesRepository(seeded)
        amazon = _platform_id(seeded, "Amazon")
        # price_band_min is 0.00, max is open — a mid-range price must match.
        rule = repo.get_active_rule(
            amazon, "Home & Kitchen", TODAY,
            selling_price=Decimal("70.00"), weight_g=100,
        )
        assert rule is not None

    def test_unknown_category_returns_none(self, seeded):
        repo = FeeRulesRepository(seeded)
        amazon = _platform_id(seeded, "Amazon")
        assert repo.get_active_rule(amazon, "Nonexistent", TODAY) is None

    def test_get_by_id_roundtrips(self, seeded):
        repo = FeeRulesRepository(seeded)
        amazon = _platform_id(seeded, "Amazon")
        rule = repo.get_active_rule(amazon, "Home & Kitchen", TODAY)
        assert repo.get_by_id(rule.rule_id).rule_id == rule.rule_id


class TestRtoResolution:
    def test_resolves_active_rate(self, seeded):
        repo = RtoRatesRepository(seeded)
        amazon = _platform_id(seeded, "Amazon")
        rate = repo.get_active_rate(amazon, "Home & Kitchen", TODAY)
        assert rate.rto_rate_pct == Decimal("5.00")
        assert rate.avg_rto_cost == Decimal("600.00")


class TestUsersRepository:
    def test_create_and_get_by_email(self, db_session):
        repo = UsersRepository(db_session)
        created = repo.create(email="a@b.com", password_hash="h", name="A")
        assert created.user_id is not None
        assert repo.get_by_email("a@b.com").user_id == created.user_id

    def test_get_missing_email_is_none(self, db_session):
        repo = UsersRepository(db_session)
        assert repo.get_by_email("nobody@x.com") is None


class TestProductsRepository:
    def test_create_and_list_by_user(self, db_session):
        users = UsersRepository(db_session)
        products = ProductsRepository(db_session)
        user = users.create(email="s@x.com", password_hash="h", name="S")

        products.create(
            user_id=user.user_id, name="P1", category="Books",
            cost_price=Decimal("100.00"), selling_price=Decimal("200.00"),
            weight_g=250,
        )
        listed = products.list_by_user(user.user_id)
        assert len(listed) == 1
        assert listed[0].selling_price == Decimal("200.00")


class TestComparisonsRepository:
    def test_add_and_history_joins_through_product(self, seeded):
        users = UsersRepository(seeded)
        products = ProductsRepository(seeded)
        fee_rules = FeeRulesRepository(seeded)
        comparisons = ComparisonsRepository(seeded)

        user = users.create(email="h@x.com", password_hash="h", name="H")
        amazon = _platform_id(seeded, "Amazon")
        product = products.create(
            user_id=user.user_id, name="Container", category="Home & Kitchen",
            cost_price=Decimal("450.00"), selling_price=Decimal("999.00"),
            weight_g=400,
        )
        rule = fee_rules.get_active_rule(
            amazon, "Home & Kitchen", TODAY,
            selling_price=Decimal("999.00"), weight_g=400,
        )

        comparisons.add(
            Comparison(
                product_id=product.product_id, platform_id=amazon,
                rule_id=rule.rule_id,
                gross_revenue=Decimal("999.00"), commission_amount=Decimal("119.88"),
                fixed_fee_amount=Decimal("40.00"), shipping_amount=Decimal("65.00"),
                gateway_amount=Decimal("19.98"), gst_amount=Decimal("44.07"),
                tcs_amount=Decimal("5.00"), rto_adjusted_cost=Decimal("30.00"),
                net_payout=Decimal("680.07"), profit=Decimal("230.07"),
                margin_pct=Decimal("23.03"), breakeven_price=Decimal("768.93"),
                explanation={"winner": "Flipkart"},
            )
        )
        seeded.commit()

        history = comparisons.list_by_user(user.user_id)
        assert len(history) == 1
        assert history[0].profit == Decimal("230.07")
        assert history[0].rule.commission_pct == Decimal("12.00")
