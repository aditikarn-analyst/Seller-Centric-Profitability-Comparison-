"""GST and TCS computation (README §13.2, §13.3).

Two statutory terms enter the profit calculation very differently:

* **GST on fees** is a real cost: 18% levied on the platform fee base, money the
  seller does not get back. It reduces net settlement.
* **TCS under Section 52** is *not* a cost. It is withheld by the marketplace at
  settlement but credited to the seller's GST electronic cash ledger, where it
  offsets output-GST liability or is refundable. It is therefore a cash-flow
  event only. The engine (Phase 7) must exclude it from EffectiveProfit and
  report it solely against CashAtSettlement. Tools that subtract TCS from profit
  overstate the cost of selling (§13.3).

Both functions round per line (HALF_UP) via the money layer.
"""

from decimal import Decimal

from app.core.constants import GST_RATE_PCT, TCS_RATE_PCT
from app.core.money import MoneyInput, apply_rate


def gst_on_fees(fee_base: MoneyInput, gst_rate_pct: MoneyInput = GST_RATE_PCT) -> Decimal:
    """GST charged on the platform fee base (a real cost).

    Example (§13.5): 18% of 244.86 -> 44.07.
    """
    return apply_rate(fee_base, gst_rate_pct)


def tcs_withheld(
    net_taxable_supply: MoneyInput, tcs_rate_pct: MoneyInput = TCS_RATE_PCT
) -> Decimal:
    """TCS withheld at settlement (a cash-flow event, not a cost — §13.3).

    ``net_taxable_supply`` is the selling price in the current model. With the
    resolved 0.5% rate, 0.5% of 999.00 -> 5.00, matching §13.5.
    """
    return apply_rate(net_taxable_supply, tcs_rate_pct)
