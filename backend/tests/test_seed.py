"""Seed-layer tests (README §12.3 versioning, O1 category coverage)."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.core.money import apply_rate
from app.db.seed.seeder import seed_all
from app.models import FeeRule, Platform, RtoRate


def _amazon(session) -> Platform:
    return session.scalar(select(Platform).where(Platform.name == "Amazon"))


class TestSeedPopulation:
    def test_counts_match_config(self, db_session):
        # Counts are derived from the platform config, not hardcoded, so adding
        # a platform updates the expectation automatically.
        from app.db.seed import data

        seed_all(db_session)
        assert db_session.query(Platform).count() == len(data.PLATFORM_SPECS)
        assert db_session.query(FeeRule).count() == len(data.FEE_RULES)
        assert db_session.query(RtoRate).count() == len(data.RTO_RATES)

    def test_at_least_nine_categories(self, db_session):
        """Objective O1: >= 9 product categories modelled."""
        seed_all(db_session)
        categories = {c for (c,) in db_session.query(FeeRule.category).distinct()}
        assert len(categories) >= 9


class TestIdempotency:
    def test_second_run_inserts_nothing(self, db_session):
        seed_all(db_session)
        fee_count = db_session.query(FeeRule).count()
        rto_count = db_session.query(RtoRate).count()

        result = seed_all(db_session)  # run again

        assert result["fee_rules_inserted"] == 0
        assert result["rto_rates_inserted"] == 0
        assert result["platforms_inserted"] == 0
        assert db_session.query(FeeRule).count() == fee_count
        assert db_session.query(RtoRate).count() == rto_count


class TestVersioning:
    def test_active_rule_is_open_ended_and_12pct(self, db_session):
        """The current Amazon Home & Kitchen rule has effective_to = NULL."""
        seed_all(db_session)
        amazon = _amazon(db_session)
        active = db_session.scalar(
            select(FeeRule).where(
                FeeRule.platform_id == amazon.platform_id,
                FeeRule.category == "Home & Kitchen",
                FeeRule.effective_to.is_(None),
            )
        )
        assert active is not None
        assert active.commission_pct == Decimal("12.00")

    def test_historical_row_retained_not_mutated(self, db_session):
        """§12.3: the superseded row survives with a closed effective_to."""
        seed_all(db_session)
        amazon = _amazon(db_session)
        historical = db_session.scalar(
            select(FeeRule).where(
                FeeRule.platform_id == amazon.platform_id,
                FeeRule.category == "Home & Kitchen",
                FeeRule.effective_to == date(2026, 3, 14),
            )
        )
        assert historical is not None
        assert historical.commission_pct == Decimal("12.50")
        assert historical.effective_from == date(2025, 4, 1)


class TestWorkedExampleAlignment:
    def test_rto_reproduces_section_13_5(self, db_session):
        """Seeded RTO inputs yield the §13.5 figures: Amazon 30.00, Flipkart 45.00."""
        seed_all(db_session)
        amazon = _amazon(db_session)
        flipkart = db_session.scalar(select(Platform).where(Platform.name == "Flipkart"))

        az_rto = db_session.scalar(
            select(RtoRate).where(
                RtoRate.platform_id == amazon.platform_id,
                RtoRate.category == "Home & Kitchen",
            )
        )
        fk_rto = db_session.scalar(
            select(RtoRate).where(
                RtoRate.platform_id == flipkart.platform_id,
                RtoRate.category == "Home & Kitchen",
            )
        )
        assert apply_rate(az_rto.avg_rto_cost, az_rto.rto_rate_pct) == Decimal("30.00")
        assert apply_rate(fk_rto.avg_rto_cost, fk_rto.rto_rate_pct) == Decimal("45.00")
