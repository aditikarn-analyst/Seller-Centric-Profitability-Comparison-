"""Platform fee module tests (README §11.2 interchangeability, §13.5)."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.db.seed.seeder import seed_all
from app.models import Platform
from app.repositories import FeeRulesRepository
from app.services.platforms import (
    AmazonFeeModule,
    FlipkartFeeModule,
    PlatformFeeModule,
    get_fee_module,
    registered_platforms,
)
from app.services.platforms.base import FeeBreakdown

# §13.5 illustrative rules as duck-typed objects (no DB needed).
AMAZON_RULE = SimpleNamespace(
    commission_pct=Decimal("12.00"), fixed_fee=Decimal("40.00"),
    shipping_fee=Decimal("65.00"), payment_gateway_pct=Decimal("2.00"),
    shipping_slab_weight_g=500,
)
FLIPKART_RULE = SimpleNamespace(
    commission_pct=Decimal("9.00"), fixed_fee=Decimal("35.00"),
    shipping_fee=Decimal("58.00"), payment_gateway_pct=Decimal("2.00"),
    shipping_slab_weight_g=500,
)


class TestFeeComputation:
    def test_amazon_matches_worked_example(self):
        fb = AmazonFeeModule().compute(Decimal("999.00"), 400, AMAZON_RULE)
        assert fb.commission == Decimal("119.88")
        assert fb.fixed_fee == Decimal("40.00")
        assert fb.shipping == Decimal("65.00")
        assert fb.gateway == Decimal("19.98")
        assert fb.fee_base == Decimal("244.86")

    def test_flipkart_matches_worked_example(self):
        fb = FlipkartFeeModule().compute(Decimal("999.00"), 400, FLIPKART_RULE)
        assert fb.commission == Decimal("89.91")
        assert fb.fixed_fee == Decimal("35.00")
        assert fb.shipping == Decimal("58.00")
        assert fb.gateway == Decimal("19.98")
        assert fb.fee_base == Decimal("202.89")


class TestInterchangeability:
    def test_both_modules_share_the_interface(self):
        for module in (AmazonFeeModule(), FlipkartFeeModule()):
            assert isinstance(module, PlatformFeeModule)
            fb = module.compute(Decimal("999.00"), 400, AMAZON_RULE)
            assert isinstance(fb, FeeBreakdown)

    def test_registry_lookup(self):
        assert get_fee_module("Amazon").name == "Amazon"
        assert get_fee_module("Flipkart").name == "Flipkart"
        assert registered_platforms() == ["Amazon", "Flipkart"]

    def test_unregistered_platform_raises(self):
        with pytest.raises(KeyError):
            get_fee_module("Meesho")


class TestWithSeededRule:
    def test_fee_base_from_real_resolved_rule(self, db_session):
        seed_all(db_session)
        amazon = db_session.query(Platform).filter_by(name="Amazon").one()
        rule = FeeRulesRepository(db_session).get_active_rule(
            amazon.platform_id, "Home & Kitchen", date(2026, 8, 5),
            selling_price=Decimal("999.00"), weight_g=400,
        )
        fb = get_fee_module("Amazon").compute(Decimal("999.00"), 400, rule)
        assert fb.fee_base == Decimal("244.86")
