"""Shared platform fee interface (README §11.2).

Every marketplace fee module exposes the *same* interface, so the comparison
orchestrator (Phase 7) prices all platforms in one loop and never branches on
platform identity. Adding a new marketplace is a new subclass plus new
``fee_rules`` rows — not a change to the orchestrator. This is the structural
response to RG1 and RG2.

The base class implements the common algorithm; each fee component is a small
overridable hook (template method), so a platform with a genuine quirk — say
weight-tiered shipping — overrides one hook without touching the rest.

Modules stay framework-free: they accept any object exposing the rule fields
(``FeeRuleLike``), so the ORM ``FeeRule`` satisfies them structurally without
the service layer importing SQLAlchemy.
"""

from abc import ABC
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol, runtime_checkable

from app.core.money import apply_rate, money


@runtime_checkable
class FeeRuleLike(Protocol):
    """Structural type for a resolved fee rule (ORM FeeRule satisfies it)."""

    commission_pct: Decimal
    fixed_fee: Decimal
    shipping_fee: Decimal
    payment_gateway_pct: Decimal
    shipping_slab_weight_g: int


@dataclass(frozen=True)
class FeeBreakdown:
    """The itemised, pre-tax fee stack for one platform."""

    commission: Decimal
    fixed_fee: Decimal
    shipping: Decimal
    gateway: Decimal

    @property
    def fee_base(self) -> Decimal:
        """FeeBase = Commission + FixedFee + Shipping + Gateway (§13.2)."""
        return self.commission + self.fixed_fee + self.shipping + self.gateway


class PlatformFeeModule(ABC):
    """Base class for all marketplace fee modules."""

    #: Must exactly match a ``platforms.name`` row.
    name: str = ""

    def compute(
        self, selling_price: Decimal, weight_g: int, rule: FeeRuleLike
    ) -> FeeBreakdown:
        """Compute the four fee lines from a resolved rule."""
        return FeeBreakdown(
            commission=self.compute_commission(selling_price, rule),
            fixed_fee=self.compute_fixed_fee(rule),
            shipping=self.compute_shipping(weight_g, rule),
            gateway=self.compute_gateway(selling_price, rule),
        )

    # --- Overridable hooks (default = data-driven from the rule) ------------
    def compute_commission(self, selling_price: Decimal, rule: FeeRuleLike) -> Decimal:
        return apply_rate(selling_price, rule.commission_pct)

    def compute_fixed_fee(self, rule: FeeRuleLike) -> Decimal:
        return money(rule.fixed_fee)

    def compute_shipping(self, weight_g: int, rule: FeeRuleLike) -> Decimal:
        return money(rule.shipping_fee)

    def compute_gateway(self, selling_price: Decimal, rule: FeeRuleLike) -> Decimal:
        return apply_rate(selling_price, rule.payment_gateway_pct)
