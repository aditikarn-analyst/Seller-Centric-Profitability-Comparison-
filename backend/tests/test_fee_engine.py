"""Fee engine + break-even tests (README §13.2–§13.5).

The engine's headline obligation: reproduce the §13.5 worked example exactly,
line for line, for both platforms.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.db.seed.seeder import seed_all
from app.services.breakeven import solve_break_even
from app.services.fee_engine import (
    ComparisonEngine,
    ProductInput,
    compute_platform_result,
)
from app.services.platforms import AmazonFeeModule, FlipkartFeeModule

TODAY = date(2026, 8, 5)

AMAZON_RULE = SimpleNamespace(
    rule_id=1, commission_pct=Decimal("12.00"), fixed_fee=Decimal("40.00"),
    shipping_fee=Decimal("65.00"), payment_gateway_pct=Decimal("2.00"),
    shipping_slab_weight_g=500, price_band_min=Decimal("0.00"), price_band_max=None,
)
FLIPKART_RULE = SimpleNamespace(
    rule_id=2, commission_pct=Decimal("9.00"), fixed_fee=Decimal("35.00"),
    shipping_fee=Decimal("58.00"), payment_gateway_pct=Decimal("2.00"),
    shipping_slab_weight_g=500, price_band_min=Decimal("0.00"), price_band_max=None,
)
AMAZON_RTO = SimpleNamespace(rto_rate_pct=Decimal("5.00"), avg_rto_cost=Decimal("600.00"))
FLIPKART_RTO = SimpleNamespace(rto_rate_pct=Decimal("6.00"), avg_rto_cost=Decimal("750.00"))


class TestWorkedExampleAmazon:
    def setup_method(self):
        self.r = compute_platform_result(
            platform_name="Amazon", cost_price=Decimal("450.00"),
            selling_price=Decimal("999.00"), weight_g=400,
            fee_module=AmazonFeeModule(), rule=AMAZON_RULE, rto=AMAZON_RTO,
        )

    def test_fee_base(self):
        assert self.r.fee_base == Decimal("244.86")

    def test_gst(self):
        assert self.r.gst == Decimal("44.07")

    def test_rto(self):
        assert self.r.rto_cost == Decimal("30.00")

    def test_net_settlement_pre_tcs(self):
        assert self.r.net_settlement == Decimal("680.07")

    def test_tcs_and_cash(self):
        assert self.r.tcs == Decimal("5.00")
        assert self.r.cash_at_settlement == Decimal("675.07")

    def test_profit_excludes_tcs(self):
        # §13.3: profit = net settlement - cost, TCS not subtracted.
        assert self.r.profit == Decimal("230.07")

    def test_margin(self):
        assert self.r.margin_pct == Decimal("23.03")


class TestWorkedExampleFlipkart:
    def setup_method(self):
        self.r = compute_platform_result(
            platform_name="Flipkart", cost_price=Decimal("450.00"),
            selling_price=Decimal("999.00"), weight_g=400,
            fee_module=FlipkartFeeModule(), rule=FLIPKART_RULE, rto=FLIPKART_RTO,
        )

    def test_full_row(self):
        assert self.r.fee_base == Decimal("202.89")
        assert self.r.gst == Decimal("36.52")
        assert self.r.rto_cost == Decimal("45.00")
        assert self.r.net_settlement == Decimal("714.59")
        assert self.r.cash_at_settlement == Decimal("709.59")
        assert self.r.profit == Decimal("264.59")
        assert self.r.margin_pct == Decimal("26.49")


class TestBreakEven:
    def test_amazon_breakeven_is_profitable_below_999(self):
        be = solve_break_even(
            cost_price=Decimal("450.00"), rules=[AMAZON_RULE],
            weight_g=400, rto_cost=Decimal("30.00"),
        )
        # Analytical: (1.18*105 + 30 + 450) / (1 - 1.18*0.14) = 723.41
        assert be == Decimal("723.41")

    def test_at_breakeven_profit_is_approximately_zero(self):
        be = solve_break_even(
            cost_price=Decimal("450.00"), rules=[AMAZON_RULE],
            weight_g=400, rto_cost=Decimal("30.00"),
        )
        r = compute_platform_result(
            platform_name="Amazon", cost_price=Decimal("450.00"),
            selling_price=be, weight_g=400,
            fee_module=AmazonFeeModule(), rule=AMAZON_RULE, rto=AMAZON_RTO,
        )
        assert abs(r.profit) < Decimal("1.00")  # within per-line rounding noise

    def test_weight_exceeding_slab_yields_no_solution(self):
        assert solve_break_even(
            cost_price=Decimal("450.00"), rules=[AMAZON_RULE],
            weight_g=900, rto_cost=Decimal("30.00"),
        ) is None

    def test_no_finite_breakeven_when_fees_exceed_growth(self):
        greedy = SimpleNamespace(
            commission_pct=Decimal("90.00"), payment_gateway_pct=Decimal("0.00"),
            fixed_fee=Decimal("0.00"), shipping_fee=Decimal("0.00"),
            shipping_slab_weight_g=1000, price_band_min=Decimal("0.00"),
            price_band_max=None,
        )
        assert solve_break_even(
            cost_price=Decimal("300.00"), rules=[greedy],
            weight_g=100, rto_cost=Decimal("0.00"),
        ) is None

    def test_piecewise_discards_inconsistent_band_solution(self):
        """§13.4: a band solution outside its own band must be discarded."""
        band_low = SimpleNamespace(  # [0, 500): high commission
            commission_pct=Decimal("20.00"), payment_gateway_pct=Decimal("0.00"),
            fixed_fee=Decimal("0.00"), shipping_fee=Decimal("0.00"),
            shipping_slab_weight_g=1000, price_band_min=Decimal("0.00"),
            price_band_max=Decimal("500.00"),
        )
        band_high = SimpleNamespace(  # [500, inf): low commission
            commission_pct=Decimal("5.00"), payment_gateway_pct=Decimal("0.00"),
            fixed_fee=Decimal("0.00"), shipping_fee=Decimal("0.00"),
            shipping_slab_weight_g=1000, price_band_min=Decimal("500.00"),
            price_band_max=None,
        )
        # band_low solves to 392.67 (in [0,500) -> valid).
        # band_high solves to 318.81 (NOT in [500, inf) -> discard).
        be = solve_break_even(
            cost_price=Decimal("300.00"), rules=[band_low, band_high],
            weight_g=100, rto_cost=Decimal("0.00"),
        )
        assert be == Decimal("392.67")


class TestComparisonEngineIntegration:
    def test_engine_reproduces_worked_example_from_seeded_db(self, db_session):
        seed_all(db_session)
        engine = ComparisonEngine(db_session)
        results = engine.compare(
            ProductInput(
                category="Home & Kitchen",
                cost_price=Decimal("450.00"),
                selling_price=Decimal("999.00"),
                weight_g=400,
            ),
            on_date=TODAY,
        )
        by_platform = {r.platform_name: r for r in results}
        assert by_platform["Amazon"].profit == Decimal("230.07")
        assert by_platform["Flipkart"].profit == Decimal("264.59")
        # rule_id populated from the resolved DB row (audit trail).
        assert by_platform["Amazon"].rule_id is not None
