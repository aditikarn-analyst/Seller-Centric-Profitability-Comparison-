"""Tax and RTO module tests (README §13.2, §13.3, §13.5)."""

from decimal import Decimal

import pytest

from app.core.constants import TCS_RATE_PCT
from app.services.rto_estimator import rto_adjusted_cost
from app.services.tax_calculator import gst_on_fees, tcs_withheld


class TestGst:
    def test_amazon_fee_base(self):
        # §13.5: 18% of 244.86 -> 44.0748 -> 44.07
        assert gst_on_fees(Decimal("244.86")) == Decimal("44.07")

    def test_flipkart_fee_base(self):
        # §13.5: 18% of 202.89 -> 36.5202 -> 36.52
        assert gst_on_fees(Decimal("202.89")) == Decimal("36.52")

    def test_zero_fee_base(self):
        assert gst_on_fees(Decimal("0.00")) == Decimal("0.00")

    def test_float_rejected(self):
        with pytest.raises(TypeError):
            gst_on_fees(244.86)


class TestTcs:
    def test_resolved_rate_is_half_percent(self):
        assert TCS_RATE_PCT == Decimal("0.50")

    def test_worked_example_value(self):
        # §13.5: 0.5% of 999.00 -> 4.995 -> 5.00 (ROUND_HALF_UP)
        assert tcs_withheld(Decimal("999.00")) == Decimal("5.00")

    def test_override_rate(self):
        # If the team later confirms 1%, the override must yield 9.99.
        assert tcs_withheld(Decimal("999.00"), Decimal("1.00")) == Decimal("9.99")

    def test_float_rejected(self):
        with pytest.raises(TypeError):
            tcs_withheld(999.0)


class TestRto:
    def test_amazon_home_kitchen(self):
        # §13.5: 5% x 600.00 -> 30.00
        assert rto_adjusted_cost(Decimal("5.00"), Decimal("600.00")) == Decimal("30.00")

    def test_flipkart_home_kitchen(self):
        # §13.5: 6% x 750.00 -> 45.00
        assert rto_adjusted_cost(Decimal("6.00"), Decimal("750.00")) == Decimal("45.00")

    def test_zero_rate_means_zero_cost(self):
        assert rto_adjusted_cost(Decimal("0.00"), Decimal("600.00")) == Decimal("0.00")

    def test_float_rejected(self):
        with pytest.raises(TypeError):
            rto_adjusted_cost(5.0, 600.0)
