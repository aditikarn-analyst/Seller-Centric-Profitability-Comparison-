"""Validation-harness tests (README §18, O6)."""

from datetime import date
from decimal import Decimal

from validation.validator import (
    ExpectedRow,
    build_in_memory_session,
    run_validation,
)

TODAY = date(2026, 8, 5)


def test_worked_example_has_zero_deviation():
    """Engine matches the §13.5 expected values exactly (self-consistency)."""
    session = build_in_memory_session()
    try:
        rows = [
            ExpectedRow("Home & Kitchen", Decimal("450.00"), Decimal("999.00"),
                        400, "Amazon", Decimal("230.07")),
            ExpectedRow("Home & Kitchen", Decimal("450.00"), Decimal("999.00"),
                        400, "Flipkart", Decimal("264.59")),
        ]
        report = run_validation(rows, session, on_date=TODAY)
        assert report.total_compared == 2
        assert report.within_tolerance == 2
        assert report.max_abs_deviation == Decimal("0.00")
    finally:
        session.close()


def test_deviation_is_reported_not_hidden():
    """A wrong expected value produces a signed, non-zero deviation."""
    session = build_in_memory_session()
    try:
        rows = [
            ExpectedRow("Home & Kitchen", Decimal("450.00"), Decimal("999.00"),
                        400, "Amazon", Decimal("200.00")),
        ]
        report = run_validation(rows, session, on_date=TODAY)
        assert report.rows[0].deviation == Decimal("30.07")  # 230.07 - 200.00
        assert report.within_tolerance == 0
    finally:
        session.close()
