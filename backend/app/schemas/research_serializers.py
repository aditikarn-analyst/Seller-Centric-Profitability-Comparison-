"""Serializers for the component-based research comparison (Option A).

All monetary values are emitted as strings (NFR3). Provenance, confidence,
assumptions, limitations, and sources are surfaced per marketplace so the client
can display exactly what is verified and what is not.
"""

from decimal import Decimal
from typing import Optional

from app.core.money import round_money
from app.services.component_engine import ComparisonOutcome, PlatformComponentResult


def _money(v: Optional[Decimal]) -> Optional[str]:
    """Emit money as a string rounded to 2dp at the API boundary (NFR3)."""
    return str(round_money(v)) if v is not None else None


def _breakdown(r: PlatformComponentResult) -> list[dict]:
    return [
        {
            "component": c.component_type,
            "value_kind": c.value_kind,
            "amount_min": _money(c.amount_min),
            "amount_max": _money(c.amount_max),
            "verification_status": c.verification_status,
            "source_type": c.source_type,
            "source_name": c.source_name,
            "source_url": c.source_url,
            "last_verified": c.last_verified,
            "notes": c.notes,
        }
        for c in r.components
    ]


def _sources(r: PlatformComponentResult) -> list[dict]:
    seen: dict[tuple, dict] = {}
    for c in r.components:
        key = (c.source_name, c.source_url, c.source_type)
        if c.source_name and key not in seen:
            seen[key] = {"name": c.source_name, "url": c.source_url, "type": c.source_type}
    return list(seen.values())


def _limitations(r: PlatformComponentResult) -> list[str]:
    lim: list[str] = []
    for c in r.missing_components:
        lim.append(f"{c}: no fee data (missing, not treated as ₹0).")
    for c in r.unavailable_components:
        lim.append(f"{c}: not publicly verifiable.")
    if r.total_cost_max is None and not r.unavailable_components and not r.missing_components:
        lim.append("Upper cost bound is open (a fee has no published maximum); only best-case profit is bounded.")
    if r.note:
        lim.append(r.note)
    return lim


def serialize_platform_result(r: PlatformComponentResult) -> dict:
    return {
        "marketplace": r.platform_name,
        "status": r.status,
        "definitive_candidate": r.is_definitive_candidate,
        "ranking_eligible": r.is_definitive_candidate,
        "total_fee_min": _money(r.total_cost_min),
        "total_fee_max": _money(r.total_cost_max),
        "net_profit_min": _money(r.net_profit_min),
        "net_profit_max": _money(r.net_profit_max),
        "profit_margin_min": _money(r.margin_min_pct),
        "profit_margin_max": _money(r.margin_max_pct),
        "fee_breakdown": _breakdown(r),
        "verified_components": r.verified_components,
        "partial_components": r.partial_components,
        "unavailable_components": r.unavailable_components,
        "missing_components": r.missing_components,
        "assumptions": r.assumptions,
        "limitations": _limitations(r),
        "sources": _sources(r),
    }


def serialize_research_outcome(product_view: dict, outcome: ComparisonOutcome) -> dict:
    return {
        "product": product_view,
        "dataset_version": outcome.dataset_version,
        "disclaimer": outcome.disclaimer,
        "definitive_winner": outcome.definitive_winner,
        "definitive_candidates": outcome.definitive_candidates,
        "recommendation_note": outcome.recommendation_note,
        "excluded": outcome.excluded,
        "results": [serialize_platform_result(r) for r in outcome.results],
    }
