"""Monetary arithmetic — the single source of correctness for all money math.

README §13.1 (NFR3) prohibits binary floating point in *any* monetary path.
Every fee, tax, RTO, and engine computation must construct and round money
through this module rather than using raw ``float`` arithmetic.

Two rules this module enforces:

1. **No float ever enters a monetary value.** ``float`` inputs are rejected at
   the boundary, because ``Decimal(0.12)`` inherits the binary-float artefact
   (``0.12000000000000000...``). Callers must pass ``str``, ``int``, or
   ``Decimal``.
2. **Per-line rounding, HALF_UP.** Each fee line is rounded to two decimal
   places at the point of computation (not at the end), because marketplaces
   round per line on settlement statements. ``ROUND_HALF_UP`` is used
   throughout — never Python's default banker's rounding.

Typical use::

    from app.core.money import money, apply_rate, ZERO

    commission = apply_rate(selling_price, rule.commission_pct)  # 12.00 -> 12%
    fee_base = commission + fixed_fee + shipping + gateway       # exact Decimal
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Union

# A value that may legally be turned into money. Note: ``float`` is deliberately
# excluded so that passing one is a static and runtime error, not silent
# corruption.
MoneyInput = Union[str, int, Decimal]

#: Quantum for two-decimal-place (paise) rounding.
CENTS = Decimal("0.01")

#: The rounding mode mandated by README §13.1.
ROUNDING = ROUND_HALF_UP

#: Convenience zero, already at money scale.
ZERO = Decimal("0.00")

#: Percentage divisor — rates such as ``commission_pct = 12.00`` are per-hundred.
_HUNDRED = Decimal("100")


def money(value: MoneyInput) -> Decimal:
    """Construct an exact ``Decimal`` money value from a safe input.

    Accepts ``str``, ``int``, or ``Decimal`` and returns the value **unrounded**
    (rounding is a separate, explicit step so intermediate precision is never
    silently lost). Rejects ``float`` — and ``bool``, which is a subclass of
    ``int`` — to prevent binary-float contamination (NFR3).

    Raises:
        TypeError: if ``value`` is a ``float`` or ``bool``.
        decimal.InvalidOperation: if a ``str`` is not a valid number.
    """
    if isinstance(value, bool):
        raise TypeError("bool is not a valid monetary value")
    if isinstance(value, float):
        raise TypeError(
            "float is prohibited in monetary paths (NFR3); "
            "pass a str, int, or Decimal instead"
        )
    if isinstance(value, Decimal):
        return value
    # int and str both construct an exact Decimal.
    return Decimal(value)


def round_money(value: MoneyInput) -> Decimal:
    """Quantize a value to two decimal places using ROUND_HALF_UP.

    This is the canonical rounding step applied per fee line (§13.1).
    """
    return money(value).quantize(CENTS, rounding=ROUNDING)


def apply_rate(base: MoneyInput, rate_pct: MoneyInput) -> Decimal:
    """Return ``base * rate_pct%`` rounded to paise, HALF_UP.

    ``rate_pct`` is expressed as a percentage number, matching the
    ``fee_rules`` schema (e.g. ``commission_pct = 12.00`` means 12%). The
    result is rounded immediately, because the amount becomes its own line on
    the settlement statement.

    Example::

        apply_rate("999.00", "12.00")  # -> Decimal('119.88')
    """
    raw = money(base) * money(rate_pct) / _HUNDRED
    return round_money(raw)
