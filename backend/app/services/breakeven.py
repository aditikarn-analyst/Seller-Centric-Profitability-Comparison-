"""Break-even price solver (README §13.4).

EffectiveProfit(P) is *piecewise*-linear, not linear: commission (and shipping)
can change at price-band boundaries, so each band has its own slope. The naive
single-equation solve gives wrong answers at boundaries — this module solves per
band and keeps only band-consistent solutions.

Within one band, with:
    k = (commission_pct + payment_gateway_pct) / 100
    F = fixed_fee + shipping_fee
    g = 1 + GST_rate/100                          (GST factor, e.g. 1.18)
    RTO = expected RTO cost (independent of P)

    EffectiveProfit(P) = P*(1 - g*k) - g*F - RTO - CostPrice = 0
=>  P*           = (g*F + RTO + CostPrice) / (1 - g*k)

Algorithm (§13.4):
    1. For every candidate band whose shipping slab accommodates the weight,
    2. solve the linear equation analytically,
    3. discard a solution that falls outside its own band (inconsistent),
    4. return the lowest consistent solution (None if none exists).
"""

from decimal import Decimal
from typing import Optional

from app.core.constants import GST_RATE_PCT
from app.core.money import MoneyInput, money, round_money
from app.services.platforms.base import FeeRuleLike

_ONE = Decimal(1)
_HUNDRED = Decimal(100)


def solve_break_even(
    *,
    cost_price: MoneyInput,
    rules: list[FeeRuleLike],
    weight_g: int,
    rto_cost: MoneyInput,
    gst_rate_pct: MoneyInput = GST_RATE_PCT,
) -> Optional[Decimal]:
    """Return the lowest band-consistent break-even price, or None.

    ``rules`` are the candidate fee rules (typically all price bands active on
    the comparison date). ``rto_cost`` is the expected RTO cost, which does not
    vary with price.
    """
    cost = money(cost_price)
    rto = money(rto_cost)
    gst_factor = _ONE + money(gst_rate_pct) / _HUNDRED

    solutions: list[Decimal] = []
    for rule in rules:
        # A band's shipping slab is the maximum weight it covers.
        if rule.shipping_slab_weight_g < weight_g:
            continue

        k = (money(rule.commission_pct) + money(rule.payment_gateway_pct)) / _HUNDRED
        fixed_plus_shipping = money(rule.fixed_fee) + money(rule.shipping_fee)
        denominator = _ONE - gst_factor * k
        if denominator <= 0:
            # Fees consume revenue as fast as it grows: no finite break-even.
            continue

        price = (gst_factor * fixed_plus_shipping + rto + cost) / denominator

        band_min = money(rule.price_band_min)
        band_max = rule.price_band_max
        if price < band_min:
            continue
        if band_max is not None and price >= money(band_max):
            continue

        solutions.append(price)

    if not solutions:
        return None
    return round_money(min(solutions))
