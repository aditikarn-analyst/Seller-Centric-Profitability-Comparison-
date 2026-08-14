"""Component-based comparison engine (Option A adapter).

Assembles a marketplace's applicable fee components, resolves each to a rupee
contribution (a single value, a bounded range, or "unknown"), and derives an
honest profit result:

* COMPLETE   — every material fee is an exact single value → one net profit.
* PARTIAL    — material fees are bounded ranges → a net-profit RANGE (min/max).
* UNAVAILABLE— a material fee is NOT_PUBLICLY_VERIFIABLE or unbounded → net
               profit cannot be defensibly computed.

Ranking policy (approved): only marketplaces whose cost is fully upper-bounded
and free of NOT_VERIFIABLE material components are "definitive candidates" and
participate in the winner ranking; others are still returned with their partial
figures and the exact missing component named. Ranges are never collapsed to a
midpoint — the engine reports min/max profit instead.
"""

from dataclasses import dataclass, field, replace
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import select

from app.core.dataset_metadata import DATA_DISCLAIMER, FEE_DATASET_VERSION
from app.core.money import ZERO, apply_rate, money, round_money
from app.core.platform_types import ComponentType, Unit, ValueKind, VerificationStatus
from app.models import Platform
from app.repositories.fee_components import FeeComponentsRepository
from app.services.fee_engine import ProductInput

_MATERIAL = {
    ComponentType.COMMISSION.value,
    ComponentType.FIXED_FEE.value,
    ComponentType.SHIPPING.value,
    ComponentType.PAYMENT.value,
}
_DEFAULT_GST_PCT = Decimal("18.00")


@dataclass(frozen=True)
class ResolvedComponent:
    component_type: str
    value_kind: str
    amount_min: Optional[Decimal]      # INR contribution, lower bound
    amount_max: Optional[Decimal]      # INR contribution, upper bound (None = open/unknown)
    verification_status: str
    source_type: str
    source_name: Optional[str]
    source_url: Optional[str]
    last_verified: Optional[str]
    notes: Optional[str]


@dataclass
class PlatformComponentResult:
    platform_name: str
    status: str                        # COMPLETE | PARTIAL | UNAVAILABLE
    is_definitive_candidate: bool
    components: list[ResolvedComponent] = field(default_factory=list)
    verified_components: list[str] = field(default_factory=list)
    partial_components: list[str] = field(default_factory=list)
    unavailable_components: list[str] = field(default_factory=list)
    missing_components: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    total_cost_min: Optional[Decimal] = None
    total_cost_max: Optional[Decimal] = None
    net_profit_min: Optional[Decimal] = None   # worst case (max cost)
    net_profit_max: Optional[Decimal] = None   # best case (min cost)
    margin_min_pct: Optional[Decimal] = None
    margin_max_pct: Optional[Decimal] = None
    note: Optional[str] = None


@dataclass
class ComparisonOutcome:
    results: list[PlatformComponentResult]
    definitive_winner: Optional[str]
    definitive_candidates: list[str]
    excluded: list[dict]               # [{platform, reasons: [...]}, ...]
    recommendation_note: str
    dataset_version: str = FEE_DATASET_VERSION
    disclaimer: str = DATA_DISCLAIMER


def _margin(profit: Optional[Decimal], selling: Decimal) -> Optional[Decimal]:
    if profit is None or selling == 0:
        return None
    return (profit / selling * Decimal(100)).quantize(Decimal("0.01"))


def decide_winner(definitive: list["PlatformComponentResult"]) -> tuple[Optional[str], str]:
    """Conservative, documented ranking policy (pure — unit-testable).

    * 0 candidates → no definitive winner.
    * 1 candidate  → it is the recommendation.
    * >1 candidate → rank by worst-case (minimum) net profit; a winner is
      established only if the top candidate's worst-case profit ≥ the runner-up's
      best-case profit (ranges do not overlap). Otherwise, NO winner is forced.
    """
    if not definitive:
        return None, ("No marketplace has sufficient publicly verified fee data for a "
                      "definitive recommendation for this product; partial results shown.")
    ranked = sorted(
        definitive,
        key=lambda r: (r.net_profit_min if r.net_profit_min is not None else r.net_profit_max),
        reverse=True,
    )
    if len(ranked) == 1:
        w = ranked[0].platform_name
        return w, (f"Recommended based on available verified fee data: {w} is the only marketplace "
                   f"with sufficient verified data for a definitive result for these inputs; "
                   f"others are partial (see limitations).")
    top, second = ranked[0], ranked[1]
    top_min = top.net_profit_min if top.net_profit_min is not None else top.net_profit_max
    second_max = second.net_profit_max if second.net_profit_max is not None else second.net_profit_min
    if top_min is not None and second_max is not None and top_min >= second_max:
        return top.platform_name, (
            f"Recommended based on available verified fee data: {top.platform_name} gives the "
            f"highest conservative (worst-case) net profit for these inputs among {len(ranked)} "
            f"definitive candidates.")
    return None, ("Definitive winner cannot be established from the available fee ranges: the top "
                  "candidates' profit ranges overlap, so no marketplace is conservatively best.")


class ComponentComparisonEngine:
    def __init__(self, session) -> None:
        self.session = session
        self.repo = FeeComponentsRepository(session)

    def _resolve(self, component, selling: Decimal) -> ResolvedComponent:
        kind = component.value_kind
        amin: Optional[Decimal]
        amax: Optional[Decimal]
        if kind == ValueKind.NOT_VERIFIABLE.value:
            amin, amax = None, None
        elif kind == ValueKind.PERCENT.value:
            amt = apply_rate(selling, component.value)
            amin, amax = amt, amt
        elif kind == ValueKind.EXACT.value:
            amt = round_money(component.value)
            amin, amax = amt, amt
        else:  # RANGE
            if component.unit == Unit.PCT.value:
                amin = apply_rate(selling, component.value_min) if component.value_min is not None else ZERO
                amax = apply_rate(selling, component.value_max) if component.value_max is not None else None
            else:
                amin = round_money(component.value_min) if component.value_min is not None else ZERO
                amax = round_money(component.value_max) if component.value_max is not None else None
        return ResolvedComponent(
            component_type=component.component_type,
            value_kind=kind,
            amount_min=amin,
            amount_max=amax,
            verification_status=component.verification_status,
            source_type=component.source_type,
            source_name=component.source_name,
            source_url=component.source_url,
            last_verified=component.last_verified.isoformat() if component.last_verified else None,
            notes=component.notes,
        )

    def _price_platform(self, platform_name, components, product) -> PlatformComponentResult:
        selling = money(product.selling_price)
        cost = money(product.cost_price)
        resolved = [self._resolve(c, selling) for c in components]

        # One component per type applies after band filtering; keep the first.
        by_type: dict[str, ResolvedComponent] = {}
        for r in resolved:
            by_type.setdefault(r.component_type, r)

        result = PlatformComponentResult(
            platform_name=platform_name, status="UNAVAILABLE",
            is_definitive_candidate=False, components=resolved,
        )

        # I6: a required material component that has NO row is *missing* — this is
        # distinct from an explicit 0 and must never be treated as fee = 0.
        missing_material = [
            ct for ct in (ComponentType.COMMISSION.value, ComponentType.FIXED_FEE.value,
                          ComponentType.SHIPPING.value, ComponentType.PAYMENT.value)
            if ct not in by_type
        ]
        result.missing_components = missing_material

        base_min = ZERO
        base_max: Optional[Decimal] = ZERO
        material_unverifiable: list[str] = []

        for ctype, r in by_type.items():
            if r.verification_status == VerificationStatus.VERIFIED.value:
                result.verified_components.append(ctype)
            elif r.verification_status == VerificationStatus.PARTIALLY_VERIFIED.value:
                result.partial_components.append(ctype)
            elif r.verification_status == VerificationStatus.NOT_PUBLICLY_VERIFIABLE.value:
                result.unavailable_components.append(ctype)
            elif r.verification_status == VerificationStatus.ASSUMED.value:
                result.assumptions.append(ctype)

            if ctype not in _MATERIAL:
                continue  # GST handled separately; RTO not a marketplace fee
            if r.amount_min is None:  # NOT_VERIFIABLE material
                material_unverifiable.append(ctype)
                base_max = None
                continue
            base_min += r.amount_min
            if base_max is not None:
                base_max = None if r.amount_max is None else base_max + r.amount_max

        # GST is statutory (18% on the marketplace fee BASE — NOT the selling
        # price). The seeded GST component resolves to 18% of selling price for
        # provenance display; we recompute it here from the same base the total
        # uses and overwrite that line so the fee breakdown reconciles EXACTLY
        # with total_fee (Issue 1). Its provenance (VERIFIED / CGST) is preserved.
        gst_pct = _DEFAULT_GST_PCT
        gst_min = apply_rate(base_min, gst_pct)
        gst_max = None if base_max is None else apply_rate(base_max, gst_pct)
        cost_min = base_min + gst_min
        cost_max = None if base_max is None else base_max + gst_max
        result.total_cost_min = cost_min
        result.total_cost_max = cost_max
        result.components = [
            replace(rc, amount_min=gst_min, amount_max=gst_max)
            if rc.component_type == ComponentType.GST.value
            else rc
            for rc in result.components
        ]

        result.is_definitive_candidate = (
            (not material_unverifiable) and (not missing_material) and (cost_max is not None)
        )

        if missing_material:
            # Missing rows: cannot even bound the known cost defensibly.
            result.status = "UNAVAILABLE"
            result.note = (
                "Missing required fee component(s): "
                f"{', '.join(missing_material)} (no data row — treated as MISSING, not ₹0)."
            )
            result.assumptions.append("RTO excluded (modelling assumption, not a marketplace-published fee).")
            return result

        if material_unverifiable:
            result.status = "UNAVAILABLE"
            result.net_profit_max = selling - cost - cost_min  # excludes unknown → optimistic
            result.margin_max_pct = _margin(result.net_profit_max, selling)
            result.note = (
                "Net profit cannot be defensibly computed: "
                f"{', '.join(material_unverifiable)} not publicly verifiable. "
                "Figure shown excludes the unverifiable component(s)."
            )
        elif cost_max is None:
            result.status = "PARTIAL"
            result.net_profit_max = selling - cost - cost_min  # best case only
            result.margin_max_pct = _margin(result.net_profit_max, selling)
            result.note = "Upper cost bound is open (shipping/fee has no published maximum); only best-case profit shown."
        else:
            result.net_profit_max = selling - cost - cost_min   # min cost → max profit
            result.net_profit_min = selling - cost - cost_max    # max cost → min profit
            result.margin_max_pct = _margin(result.net_profit_max, selling)
            result.margin_min_pct = _margin(result.net_profit_min, selling)
            result.status = "COMPLETE" if cost_min == cost_max else "PARTIAL"
            if result.status == "PARTIAL":
                result.note = "Range-based: profit reported as a min–max band (some fees are published ranges)."

        result.assumptions.append("RTO excluded (modelling assumption, not a marketplace-published fee).")
        return result

    def compare(
        self,
        product: ProductInput,
        fulfillment_type: Optional[str] = None,
        on_date: Optional[date] = None,
    ) -> ComparisonOutcome:
        on_date = on_date or date.today()
        platforms = self.session.scalars(
            select(Platform).where(
                Platform.is_active.is_(True), Platform.seller_supported.is_(True)
            )
        )

        results: list[PlatformComponentResult] = []
        for platform in platforms:
            comps = self.repo.list_applicable(
                platform.platform_id, product.category, on_date,
                money(product.selling_price), fulfillment_type,
            )
            if not comps:
                continue  # platform has no component data for this category
            results.append(self._price_platform(platform.name, comps, product))

        definitive = [r for r in results if r.is_definitive_candidate]
        definitive.sort(key=lambda r: (r.net_profit_min if r.net_profit_min is not None else r.net_profit_max), reverse=True)

        excluded = [
            {
                "platform": r.platform_name,
                "reasons": (
                    [f"{c} not publicly verifiable" for c in r.unavailable_components]
                    or ["cost not fully upper-bounded (open shipping/fee range)"]
                ),
            }
            for r in results
            if not r.is_definitive_candidate
        ]

        winner, note = decide_winner(definitive)

        return ComparisonOutcome(
            results=results,
            definitive_winner=winner,
            definitive_candidates=[r.platform_name for r in definitive],
            excluded=excluded,
            recommendation_note=note,
        )
