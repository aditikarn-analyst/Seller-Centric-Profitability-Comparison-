"""Recommendation + explainer tests (README §13.5, RG8)."""

from datetime import date
from decimal import Decimal

from app.db.seed.seeder import seed_all
from app.services.explainer import explain
from app.services.fee_engine import ComparisonEngine, PlatformResult, ProductInput
from app.services.recommendation_engine import rank, recommend

TODAY = date(2026, 8, 5)


def _result(name, profit, **components) -> PlatformResult:
    base = dict(
        commission=Decimal("0"), fixed_fee=Decimal("0"), shipping=Decimal("0"),
        gateway=Decimal("0"), gst=Decimal("0"), rto_cost=Decimal("0"),
    )
    base.update(components)
    return PlatformResult(
        platform_name=name, gross_revenue=Decimal("999.00"),
        fee_base=Decimal("0"), net_settlement=Decimal("0"), tcs=Decimal("5.00"),
        cash_at_settlement=Decimal("0"), profit=profit, margin_pct=Decimal("0"),
        breakeven_price=None, rule_id=None, **base,
    )


# §13.5 worked-example results.
AMAZON = _result(
    "Amazon", Decimal("230.07"),
    commission=Decimal("119.88"), fixed_fee=Decimal("40.00"),
    shipping=Decimal("65.00"), gateway=Decimal("19.98"),
    gst=Decimal("44.07"), rto_cost=Decimal("30.00"),
)
FLIPKART = _result(
    "Flipkart", Decimal("264.59"),
    commission=Decimal("89.91"), fixed_fee=Decimal("35.00"),
    shipping=Decimal("58.00"), gateway=Decimal("19.98"),
    gst=Decimal("36.52"), rto_cost=Decimal("45.00"),
)


class TestRanking:
    def test_winner_is_highest_profit(self):
        rec = recommend([AMAZON, FLIPKART])
        assert rec.winner == "Flipkart"
        assert rec.ranking[0].platform_name == "Flipkart"
        assert rec.ranking[1].platform_name == "Amazon"

    def test_margin_over_next(self):
        rec = recommend([AMAZON, FLIPKART])
        assert rec.margin_over_next == Decimal("34.52")

    def test_deterministic_tie_break_by_name(self):
        a = _result("Bravo", Decimal("100.00"))
        b = _result("Alpha", Decimal("100.00"))
        assert [r.platform_name for r in rank([a, b])] == ["Alpha", "Bravo"]


class TestExplanationDecomposition:
    def test_signed_contributions_match_section_13_5(self):
        items = {i.factor: i.delta for i in explain(FLIPKART, AMAZON)}
        assert items["commission"] == Decimal("29.97")
        assert items["shipping"] == Decimal("7.00")
        assert items["fixed_fee"] == Decimal("5.00")
        assert items["gst"] == Decimal("7.55")
        assert items["rto"] == Decimal("-15.00")     # offset
        assert "gateway" not in items                 # zero delta excluded

    def test_deltas_sum_exactly_to_profit_gap(self):
        items = explain(FLIPKART, AMAZON)
        total = sum((i.delta for i in items), Decimal("0"))
        assert total == FLIPKART.profit - AMAZON.profit == Decimal("34.52")

    def test_deciding_factor_is_largest_magnitude(self):
        rec = recommend([AMAZON, FLIPKART])
        assert rec.deciding_factor == "commission"


class TestEdgeCases:
    def test_single_platform_has_zero_margin_and_no_explanation(self):
        rec = recommend([AMAZON])
        assert rec.winner == "Amazon"
        assert rec.margin_over_next == Decimal("0.00")
        assert rec.explanation == []
        assert rec.deciding_factor is None

    def test_empty_results_raises(self):
        import pytest

        with pytest.raises(ValueError):
            recommend([])


class TestIntegration:
    def test_full_pipeline_from_seeded_db(self, db_session):
        seed_all(db_session)
        results = ComparisonEngine(db_session).compare(
            ProductInput(
                category="Home & Kitchen", cost_price=Decimal("450.00"),
                selling_price=Decimal("999.00"), weight_g=400,
            ),
            on_date=TODAY,
        )
        rec = recommend(results)
        assert rec.winner == "Flipkart"
        assert rec.margin_over_next == Decimal("34.52")
        assert rec.deciding_factor == "commission"
        total = sum((i.delta for i in rec.explanation), Decimal("0"))
        assert total == Decimal("34.52")
