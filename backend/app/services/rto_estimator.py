"""Return-to-origin (RTO) cost estimation (README §13.2).

RTO is a first-class term in the profit formula (RG4), not an optional toggle.
The figure is an *expected value*: the per-unit amortised cost of returns across
a product category, not the cost of a single return event.

    RTO_cost = RTO_rate x (ForwardShipping + ReverseShipping + HandlingCost)

Here ``avg_rto_cost`` already represents the bracketed sum (the full cost of one
return event), and ``rto_rate_pct`` is the category return probability. The
product, rounded per line, is the amount subtracted from net settlement.
"""

from decimal import Decimal

from app.core.money import MoneyInput, apply_rate


def rto_adjusted_cost(
    rto_rate_pct: MoneyInput, avg_rto_cost: MoneyInput
) -> Decimal:
    """Expected per-unit RTO cost for a category.

    Example (§13.5): 5% x 600.00 -> 30.00 (Amazon), 6% x 750.00 -> 45.00
    (Flipkart).
    """
    return apply_rate(avg_rto_cost, rto_rate_pct)
