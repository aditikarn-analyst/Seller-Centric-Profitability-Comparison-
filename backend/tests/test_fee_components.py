"""Tests for the normalized fee-component system (Option A).

These assert the *mechanism* — component-level provenance, range handling,
partial/definitive classification, and ranking exclusion — not a predetermined
winner. Whatever wins must emerge from the seeded, source-verified data.
"""

from datetime import date
from decimal import Decimal

import pytest

from app.core.platform_types import ValueKind, VerificationStatus
from app.db.seed.seeder import seed_all
from app.services.component_engine import ComponentComparisonEngine
from app.services.fee_engine import ProductInput

TODAY = date(2026, 8, 9)


@pytest.fixture()
def engine(db_session):
    seed_all(db_session)
    return ComponentComparisonEngine(db_session)


def _run(engine, category="Home & Kitchen", selling="999.00", cost="450.00", weight=400):
    return engine.compare(
        ProductInput(category=category, cost_price=Decimal(cost),
                     selling_price=Decimal(selling), weight_g=weight),
        on_date=TODAY,
    )


def _result(outcome, name):
    return next(r for r in outcome.results if r.platform_name == name)


class TestMeeshoRangeCalculation:
    def test_meesho_is_definitive_with_profit_range(self, engine):
        m = _result(_run(engine), "Meesho")
        assert m.is_definitive_candidate is True
        assert m.status == "PARTIAL"                     # range-based, not fabricated exact
        # base_min 52 (+18% GST) → cost_min 61.36 ; base_max 150 (+18%) → cost_max 177.00
        assert m.total_cost_min == Decimal("61.36")
        assert m.total_cost_max == Decimal("177.00")
        assert m.net_profit_max == Decimal("487.64")     # best case (min cost)
        assert m.net_profit_min == Decimal("372.00")     # worst case (max cost)
        assert m.net_profit_min != m.net_profit_max       # range preserved, no midpoint

    def test_meesho_zero_commission_is_percent_not_unknown(self, engine):
        m = _result(_run(engine), "Meesho")
        commission = next(c for c in m.components if c.component_type == "COMMISSION")
        assert commission.value_kind == ValueKind.PERCENT.value      # 0% is a known value
        assert commission.verification_status == VerificationStatus.VERIFIED.value
        assert commission.amount_min == Decimal("0.00")


class TestAmazonPartialHandling:
    def test_amazon_excluded_payment_not_verifiable(self, engine):
        a = _result(_run(engine), "Amazon")
        assert a.is_definitive_candidate is False
        assert a.status == "UNAVAILABLE"
        assert "PAYMENT" in a.unavailable_components
        assert a.net_profit_min is None                  # cannot bound worst case

    def test_amazon_component_level_provenance(self, engine):
        a = _result(_run(engine), "Amazon")
        # Same marketplace, different confidence per component (the whole point).
        assert "COMMISSION" in a.verified_components      # 0% under ₹1000 (official)
        assert "PAYMENT" in a.unavailable_components      # not disclosed


class TestFlipkartHandling:
    def test_flipkart_low_price_open_shipping_excluded(self, engine):
        f = _result(_run(engine, selling="999.00"), "Flipkart")
        assert f.is_definitive_candidate is False         # shipping upper bound open
        assert f.total_cost_max is None

    def test_flipkart_high_price_commission_not_verifiable(self, engine):
        f = _result(_run(engine, selling="2000.00"), "Flipkart")
        assert "COMMISSION" in f.unavailable_components    # ≥₹1000 login-gated
        assert f.status == "UNAVAILABLE"


class TestRankingPolicy:
    def test_only_definitive_candidates_ranked(self, engine):
        outcome = _run(engine)
        # With today's public data, Meesho is the only fully-verifiable candidate.
        assert outcome.definitive_candidates == ["Meesho"]
        assert outcome.definitive_winner == "Meesho"
        assert "only marketplace" in outcome.recommendation_note
        excluded_names = {e["platform"] for e in outcome.excluded}
        assert {"Amazon", "Flipkart"}.issubset(excluded_names)

    def test_excluded_reasons_name_the_missing_component(self, engine):
        outcome = _run(engine)
        amazon_excl = next(e for e in outcome.excluded if e["platform"] == "Amazon")
        assert any("PAYMENT" in r for r in amazon_excl["reasons"])


class TestProvenanceAndMetadata:
    def test_every_component_carries_provenance(self, engine):
        for r in _run(engine).results:
            for c in r.components:
                assert c.verification_status
                assert c.source_type
                # source_url present for all real marketplace components
                assert c.source_url is not None

    def test_dataset_version_exposed(self, engine):
        outcome = _run(engine)
        assert outcome.dataset_version == "2026.08"
        assert "does not represent a live" in outcome.disclaimer


class TestFinancialReconciliation:
    """Issue 1: the fee breakdown must reconcile exactly with the totals and
    profit. GST is 18% of the fee base, not of the selling price."""

    MATERIAL = {"COMMISSION", "FIXED_FEE", "SHIPPING", "PAYMENT"}

    def test_gst_line_is_on_fee_base_not_selling_price(self, engine):
        m = _result(_run(engine), "Meesho")
        gst = next(c for c in m.components if c.component_type == "GST")
        # base_min = 0+25+27 = 52 → GST 9.36 ; base_max = 0+30+120 = 150 → 27.00
        assert gst.amount_min == Decimal("9.36")
        assert gst.amount_max == Decimal("27.00")
        # and NOT 18% of ₹999 (179.82) — the old bug
        assert gst.amount_min != Decimal("179.82")

    def test_breakdown_sums_to_total_fee(self, engine):
        for r in _run(engine).results:
            if r.total_cost_min is not None:
                smin = sum((c.amount_min for c in r.components if c.amount_min is not None), Decimal("0"))
                assert smin == r.total_cost_min, r.platform_name
            if r.total_cost_max is not None:
                smax = sum((c.amount_max for c in r.components if c.amount_max is not None), Decimal("0"))
                assert smax == r.total_cost_max, r.platform_name

    def test_profit_reconciles_with_total_fee(self, engine):
        cost, selling = Decimal("450.00"), Decimal("999.00")
        for r in _run(engine).results:
            if r.net_profit_max is not None and r.total_cost_min is not None:
                assert r.net_profit_max == selling - cost - r.total_cost_min
            if r.net_profit_min is not None and r.total_cost_max is not None:
                assert r.net_profit_min == selling - cost - r.total_cost_max

    def test_range_reconciliation_min_and_max(self, engine):
        m = _result(_run(engine), "Meesho")
        # worst case uses max cost, best case uses min cost
        assert m.net_profit_min == Decimal("999.00") - Decimal("450.00") - m.total_cost_max
        assert m.net_profit_max == Decimal("999.00") - Decimal("450.00") - m.total_cost_min

    def test_api_money_values_are_two_dp(self, engine):
        from app.schemas.research_serializers import serialize_platform_result
        for r in _run(engine).results:
            d = serialize_platform_result(r)
            for key in ("total_fee_min", "total_fee_max", "net_profit_min", "net_profit_max"):
                v = d[key]
                if v is not None:
                    assert v == str(Decimal(v).quantize(Decimal("0.01"))), (key, v)


class TestMissingComponentGuard:
    """I6: a missing component row must never be treated as ₹0."""

    def test_missing_material_component_is_not_zero(self, db_session):
        from app.models import FeeComponent, Platform
        seed_all(db_session)
        meesho = db_session.query(Platform).filter_by(name="Meesho").one()
        # Remove Meesho SHIPPING rows for the category → component is now MISSING.
        db_session.query(FeeComponent).filter(
            FeeComponent.platform_id == meesho.platform_id,
            FeeComponent.category == "Home & Kitchen",
            FeeComponent.component_type == "SHIPPING",
        ).delete()
        db_session.commit()

        m = _result(_run(ComponentComparisonEngine(db_session)), "Meesho")
        assert "SHIPPING" in m.missing_components
        assert m.status == "UNAVAILABLE"
        assert m.is_definitive_candidate is False   # cannot pretend shipping = 0


class TestLegacyIsolation:
    """I7: the component engine must not depend on legacy fee_rules."""

    def test_result_unchanged_when_fee_rules_deleted(self, db_session):
        from app.models import FeeRule
        seed_all(db_session)
        eng = ComponentComparisonEngine(db_session)
        before = _result(_run(eng), "Meesho")

        db_session.query(FeeRule).delete()          # wipe legacy data entirely
        db_session.commit()

        after = _result(_run(ComponentComparisonEngine(db_session)), "Meesho")
        assert after.net_profit_min == before.net_profit_min
        assert after.net_profit_max == before.net_profit_max
        assert after.total_cost_min == before.total_cost_min


class TestConservativeRankingPolicy:
    """Pure ranking policy: no forced winner when profit ranges overlap."""

    @staticmethod
    def _mk(name, pmin, pmax):
        from app.services.component_engine import PlatformComponentResult
        return PlatformComponentResult(
            platform_name=name, status="PARTIAL", is_definitive_candidate=True,
            net_profit_min=Decimal(pmin), net_profit_max=Decimal(pmax),
        )

    def test_no_winner_when_ranges_overlap(self):
        from app.services.component_engine import decide_winner
        a = self._mk("A", "100", "150")
        b = self._mk("B", "120", "140")
        winner, note = decide_winner([a, b])
        assert winner is None
        assert "cannot be established" in note

    def test_winner_when_ranges_disjoint(self):
        from app.services.component_engine import decide_winner
        a = self._mk("A", "200", "220")
        b = self._mk("B", "100", "150")
        winner, _ = decide_winner([a, b])
        assert winner == "A"        # A's worst case (200) beats B's best case (150)

    def test_single_candidate_is_winner(self):
        from app.services.component_engine import decide_winner
        winner, note = decide_winner([self._mk("A", "100", "120")])
        assert winner == "A"
        assert "only marketplace" in note

    def test_no_candidates_no_winner(self):
        from app.services.component_engine import decide_winner
        winner, _ = decide_winner([])
        assert winner is None
