"""Unit tests for the money layer (README §13.1 / NFR3).

Assertions are exact-value: money math has one correct answer, never an
approximate one.
"""

from decimal import Decimal, InvalidOperation

import pytest

from app.core.money import ZERO, apply_rate, money, round_money


# --------------------------------------------------------------------------- #
# money(): safe construction
# --------------------------------------------------------------------------- #
class TestMoney:
    def test_from_string_is_exact(self):
        assert money("999.00") == Decimal("999.00")

    def test_from_int(self):
        assert money(450) == Decimal("450")

    def test_from_decimal_passes_through(self):
        d = Decimal("12.34")
        assert money(d) is d

    def test_float_is_rejected(self):
        # The core NFR3 guarantee: a float can never enter a monetary value.
        with pytest.raises(TypeError):
            money(0.12)

    def test_bool_is_rejected(self):
        # bool is an int subclass; must not be silently treated as 0/1 money.
        with pytest.raises(TypeError):
            money(True)

    def test_invalid_string_raises(self):
        with pytest.raises(InvalidOperation):
            money("not-a-number")


# --------------------------------------------------------------------------- #
# round_money(): ROUND_HALF_UP, two places
# --------------------------------------------------------------------------- #
class TestRoundMoney:
    def test_rounds_to_two_places(self):
        assert round_money("44.0748") == Decimal("44.07")

    def test_half_up_not_bankers(self):
        # Banker's rounding would give 0.12; we require HALF_UP -> 0.13.
        assert round_money("0.125") == Decimal("0.13")

    def test_half_up_classic_float_trap(self):
        # 2.675 is the textbook float-rounding failure; with Decimal(str) it
        # is exact and rounds up.
        assert round_money("2.675") == Decimal("2.68")

    def test_rounds_down_below_half(self):
        assert round_money("36.5202") == Decimal("36.52")

    def test_already_two_places_unchanged(self):
        assert round_money("119.88") == Decimal("119.88")

    def test_zero(self):
        assert round_money(ZERO) == Decimal("0.00")


# --------------------------------------------------------------------------- #
# apply_rate(): percentage of a base, rounded per line
# --------------------------------------------------------------------------- #
class TestApplyRate:
    def test_worked_example_amazon_commission(self):
        # §13.5: 12% of 999.00 -> 119.88
        assert apply_rate("999.00", "12.00") == Decimal("119.88")

    def test_worked_example_flipkart_commission(self):
        # §13.5: 9% of 999.00 -> 89.91
        assert apply_rate("999.00", "9.00") == Decimal("89.91")

    def test_worked_example_gateway(self):
        # §13.5: 2% of 999.00 -> 19.98
        assert apply_rate("999.00", "2.00") == Decimal("19.98")

    def test_worked_example_gst_on_amazon_fee_base(self):
        # §13.5: 18% of fee base 244.86 -> 44.0748 -> 44.07
        assert apply_rate("244.86", "18.00") == Decimal("44.07")

    def test_worked_example_gst_on_flipkart_fee_base(self):
        # §13.5: 18% of fee base 202.89 -> 36.5202 -> 36.52
        assert apply_rate("202.89", "18.00") == Decimal("36.52")

    def test_zero_rate(self):
        assert apply_rate("999.00", "0") == Decimal("0.00")

    def test_result_is_rounded_per_line(self):
        # 33.33% of 100 = 33.33 (rounded), proving per-line rounding happens.
        assert apply_rate("100.00", "33.33") == Decimal("33.33")

    def test_float_base_rejected(self):
        with pytest.raises(TypeError):
            apply_rate(999.0, "12.00")

    def test_float_rate_rejected(self):
        with pytest.raises(TypeError):
            apply_rate("999.00", 12.0)
