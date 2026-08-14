"""Fee calculation engine (README §13).

Two layers:

* ``compute_platform_result`` — a pure function that turns a resolved fee rule,
  RTO rate, and product prices into a full itemised result. No database, no
  framework: unit-testable against the §13.5 worked example directly.
* ``ComparisonEngine`` — a thin orchestrator that resolves the active rules from
  the repositories for every active platform and computes a result for each. It
  produces the per-platform results; ranking and explanation are added in
  Phase 8.

Ordering of terms follows §13.2 exactly, and TCS is kept out of profit (§13.3).
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional, Protocol

from sqlalchemy import select

from app.core.constants import GST_RATE_PCT, TCS_RATE_PCT
from app.core.money import CENTS, ROUNDING, MoneyInput, money
from app.models import Platform
from app.repositories import FeeRulesRepository, RtoRatesRepository
from app.services.breakeven import solve_break_even
from app.services.platforms import get_fee_module
from app.services.platforms.base import FeeRuleLike, PlatformFeeModule
from app.services.rto_estimator import rto_adjusted_cost
from app.services.tax_calculator import gst_on_fees, tcs_withheld


class RtoLike(Protocol):
    rto_rate_pct: Decimal
    avg_rto_cost: Decimal


@dataclass(frozen=True)
class ProductInput:
    """The minimal product facts the engine needs to price a comparison."""

    category: str
    cost_price: Decimal
    selling_price: Decimal
    weight_g: int


@dataclass(frozen=True)
class PlatformResult:
    """A full itemised result for one platform (mirrors the §13.5 columns)."""

    platform_name: str
    gross_revenue: Decimal
    commission: Decimal
    fixed_fee: Decimal
    shipping: Decimal
    gateway: Decimal
    fee_base: Decimal
    gst: Decimal
    rto_cost: Decimal
    net_settlement: Decimal          # pre-TCS (§13.2)
    tcs: Decimal                     # withheld, credited back (§13.3)
    cash_at_settlement: Decimal
    profit: Decimal                  # EffectiveProfit — excludes TCS
    margin_pct: Decimal
    breakeven_price: Optional[Decimal]
    rule_id: Optional[int]
    platform_id: Optional[int] = None


def _margin(profit: Decimal, selling_price: Decimal) -> Decimal:
    """EffectiveProfit / SellingPrice * 100, to two places (§13.2)."""
    if selling_price == 0:
        return Decimal("0.00")
    return (profit / selling_price * Decimal(100)).quantize(CENTS, rounding=ROUNDING)


def compute_platform_result(
    *,
    platform_name: str,
    cost_price: MoneyInput,
    selling_price: MoneyInput,
    weight_g: int,
    fee_module: PlatformFeeModule,
    rule: FeeRuleLike,
    rto: RtoLike,
    breakeven_price: Optional[Decimal] = None,
    platform_id: Optional[int] = None,
    gst_rate_pct: MoneyInput = GST_RATE_PCT,
    tcs_rate_pct: MoneyInput = TCS_RATE_PCT,
) -> PlatformResult:
    """Compute the complete fee stack and profit for one platform (§13.2)."""
    selling = money(selling_price)
    cost = money(cost_price)

    fees = fee_module.compute(selling, weight_g, rule)
    fee_base = fees.fee_base
    gst = gst_on_fees(fee_base, gst_rate_pct)
    rto_cost = rto_adjusted_cost(rto.rto_rate_pct, rto.avg_rto_cost)

    net_settlement = selling - fee_base - gst - rto_cost         # pre-TCS
    tcs = tcs_withheld(selling, tcs_rate_pct)
    cash_at_settlement = net_settlement - tcs
    profit = net_settlement - cost                              # TCS excluded
    margin = _margin(profit, selling)

    return PlatformResult(
        platform_name=platform_name,
        gross_revenue=selling,
        commission=fees.commission,
        fixed_fee=fees.fixed_fee,
        shipping=fees.shipping,
        gateway=fees.gateway,
        fee_base=fee_base,
        gst=gst,
        rto_cost=rto_cost,
        net_settlement=net_settlement,
        tcs=tcs,
        cash_at_settlement=cash_at_settlement,
        profit=profit,
        margin_pct=margin,
        breakeven_price=breakeven_price,
        rule_id=getattr(rule, "rule_id", None),
        platform_id=platform_id,
    )


class ComparisonEngine:
    """Resolves rules and computes a result per active platform."""

    def __init__(self, session) -> None:
        self.session = session
        self.fee_rules = FeeRulesRepository(session)
        self.rto_rates = RtoRatesRepository(session)

    def compare(
        self, product: ProductInput, on_date: Optional[date] = None
    ) -> list[PlatformResult]:
        on_date = on_date or date.today()
        # Business rule: only active platforms that onboard third-party sellers
        # participate. Brand-owned D2C stores are excluded here even if they
        # somehow carried fee rows.
        active_platforms = self.session.scalars(
            select(Platform).where(
                Platform.is_active.is_(True),
                Platform.seller_supported.is_(True),
            )
        )

        results: list[PlatformResult] = []
        for platform in active_platforms:
            rule = self.fee_rules.get_active_rule(
                platform.platform_id, product.category, on_date,
                selling_price=product.selling_price, weight_g=product.weight_g,
            )
            rto = self.rto_rates.get_active_rate(
                platform.platform_id, product.category, on_date
            )
            # A platform that cannot price this product (no rule/rate) is skipped.
            if rule is None or rto is None:
                continue

            candidate_rules = self.fee_rules.list_active(
                platform.platform_id, product.category, on_date
            )
            breakeven = solve_break_even(
                cost_price=product.cost_price,
                rules=candidate_rules,
                weight_g=product.weight_g,
                rto_cost=rto_adjusted_cost(rto.rto_rate_pct, rto.avg_rto_cost),
            )

            results.append(
                compute_platform_result(
                    platform_name=platform.name,
                    cost_price=product.cost_price,
                    selling_price=product.selling_price,
                    weight_g=product.weight_g,
                    fee_module=get_fee_module(platform.name),
                    rule=rule,
                    rto=rto,
                    breakeven_price=breakeven,
                    platform_id=platform.platform_id,
                )
            )
        return results
