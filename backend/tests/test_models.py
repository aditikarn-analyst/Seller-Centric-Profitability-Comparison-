"""Persistence-layer tests (README §12, §10 SQLite traps, NFR3/NFR5)."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Comparison, FeeRule, Platform, Product, User


def _make_user(session, email="seller@example.com"):
    user = User(email=email, password_hash="x", name="Test Seller")
    session.add(user)
    session.commit()
    return user


class TestSchemaCreation:
    def test_all_tables_created(self, db_session):
        # If the fixture's create_all succeeded, a trivial query must work.
        assert db_session.query(User).count() == 0


class TestMoneyPrecision:
    def test_money_roundtrips_as_exact_decimal(self, db_session):
        """The §10 SQLite trap: NUMERIC must not come back as a float."""
        user = _make_user(db_session)
        product = Product(
            user_id=user.user_id,
            name="Kitchen container",
            category="Home & Kitchen",
            cost_price=Decimal("450.00"),
            selling_price=Decimal("999.99"),
            weight_g=400,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

        assert isinstance(product.selling_price, Decimal)
        assert not isinstance(product.selling_price, float)
        assert product.selling_price == Decimal("999.99")
        assert product.cost_price == Decimal("450.00")

    def test_string_input_accepted_and_quantized(self, db_session):
        user = _make_user(db_session)
        product = Product(
            user_id=user.user_id,
            name="X",
            category="Home & Kitchen",
            cost_price="450",          # str input
            selling_price="1000.5",    # quantized to 1000.50
            weight_g=100,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        assert product.selling_price == Decimal("1000.50")
        assert product.cost_price == Decimal("450.00")


class TestForeignKeyEnforcement:
    def test_orphan_product_rejected(self, db_session):
        """The §10 SQLite trap: FKs must actually be enforced."""
        product = Product(
            user_id=99999,  # no such user
            name="Orphan",
            category="Home & Kitchen",
            cost_price=Decimal("10.00"),
            selling_price=Decimal("20.00"),
            weight_g=100,
        )
        db_session.add(product)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestUniqueConstraints:
    def test_duplicate_email_rejected(self, db_session):
        _make_user(db_session, email="dup@example.com")
        with pytest.raises(IntegrityError):
            _make_user(db_session, email="dup@example.com")


class TestFeeRuleVersioning:
    def test_effective_to_null_means_active(self, db_session):
        """§12.3: the currently-active rule row has a NULL effective_to."""
        platform = Platform(name="Amazon", is_active=True)
        db_session.add(platform)
        db_session.commit()

        rule = FeeRule(
            platform_id=platform.platform_id,
            category="Home & Kitchen",
            price_band_min=Decimal("0.00"),
            price_band_max=None,
            commission_pct=Decimal("12.00"),
            fixed_fee=Decimal("40.00"),
            shipping_slab_weight_g=500,
            shipping_fee=Decimal("65.00"),
            payment_gateway_pct=Decimal("2.00"),
            gst_pct=Decimal("18.00"),
            effective_from=date(2026, 3, 15),
            effective_to=None,
            source_url="https://sellercentral.amazon.in/",
            date_accessed=date(2026, 8, 5),
        )
        db_session.add(rule)
        db_session.commit()
        db_session.refresh(rule)

        assert rule.effective_to is None
        assert rule.commission_pct == Decimal("12.00")
        assert rule.platform.name == "Amazon"


class TestComparisonPersistence:
    def test_comparison_stores_denormalised_lines_and_json(self, db_session):
        user = _make_user(db_session)
        platform = Platform(name="Flipkart", is_active=True)
        db_session.add(platform)
        db_session.commit()

        product = Product(
            user_id=user.user_id,
            name="Container",
            category="Home & Kitchen",
            cost_price=Decimal("450.00"),
            selling_price=Decimal("999.00"),
            weight_g=400,
        )
        db_session.add(product)
        db_session.commit()

        rule = FeeRule(
            platform_id=platform.platform_id,
            category="Home & Kitchen",
            price_band_min=Decimal("0.00"),
            price_band_max=None,
            commission_pct=Decimal("9.00"),
            fixed_fee=Decimal("35.00"),
            shipping_slab_weight_g=500,
            shipping_fee=Decimal("58.00"),
            payment_gateway_pct=Decimal("2.00"),
            gst_pct=Decimal("18.00"),
            effective_from=date(2026, 3, 15),
            source_url="https://seller.flipkart.com/",
            date_accessed=date(2026, 8, 5),
        )
        db_session.add(rule)
        db_session.commit()

        comparison = Comparison(
            product_id=product.product_id,
            platform_id=platform.platform_id,
            rule_id=rule.rule_id,
            gross_revenue=Decimal("999.00"),
            commission_amount=Decimal("89.91"),
            fixed_fee_amount=Decimal("35.00"),
            shipping_amount=Decimal("58.00"),
            gateway_amount=Decimal("19.98"),
            gst_amount=Decimal("36.52"),
            tcs_amount=Decimal("5.00"),
            rto_adjusted_cost=Decimal("45.00"),
            net_payout=Decimal("714.59"),
            profit=Decimal("264.59"),
            margin_pct=Decimal("26.49"),
            breakeven_price=Decimal("734.41"),
            explanation={"winner": "Flipkart", "delta": "34.52"},
        )
        db_session.add(comparison)
        db_session.commit()
        db_session.refresh(comparison)

        assert comparison.profit == Decimal("264.59")
        assert comparison.explanation["winner"] == "Flipkart"
        assert comparison.rule.commission_pct == Decimal("9.00")
