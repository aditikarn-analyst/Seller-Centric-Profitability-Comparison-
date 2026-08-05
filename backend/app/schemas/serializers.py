"""Response serializers (README §15).

All monetary values are emitted as JSON strings, never floats, preserving the
NFR3 exact-decimal guarantee across the wire (FastAPI's default encoder would
otherwise turn Decimal into float).
"""

from decimal import Decimal
from typing import Optional

from app.models import Comparison, Product, User
from app.services.fee_engine import PlatformResult
from app.services.recommendation_engine import Recommendation


def _money(value: Optional[Decimal]) -> Optional[str]:
    return str(value) if value is not None else None


def serialize_user(user: User) -> dict:
    return {
        "user_id": user.user_id,
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def serialize_product(product: Product) -> dict:
    return {
        "product_id": product.product_id,
        "name": product.name,
        "category": product.category,
        "cost_price": _money(product.cost_price),
        "selling_price": _money(product.selling_price),
        "weight_g": product.weight_g,
    }


def serialize_breakdown(r: PlatformResult) -> dict:
    return {
        "gross_revenue": _money(r.gross_revenue),
        "commission": _money(r.commission),
        "fixed_fee": _money(r.fixed_fee),
        "shipping": _money(r.shipping),
        "gateway": _money(r.gateway),
        "fee_base": _money(r.fee_base),
        "gst_on_fees": _money(r.gst),
        "rto_adjusted_cost": _money(r.rto_cost),
        "net_settlement": _money(r.net_settlement),
        "tcs_withheld": _money(r.tcs),
        "cash_at_settlement": _money(r.cash_at_settlement),
        "effective_profit": _money(r.profit),
        "margin_pct": _money(r.margin_pct),
        "breakeven_price": _money(r.breakeven_price),
    }


def serialize_result(r: PlatformResult, rank: int) -> dict:
    return {
        "platform": r.platform_name,
        "rank": rank,
        "breakdown": serialize_breakdown(r),
        "rule_id": r.rule_id,
    }


def serialize_recommendation(rec: Recommendation) -> dict:
    return {
        "winner": rec.winner,
        "margin_over_next": _money(rec.margin_over_next),
        "deciding_factor": rec.deciding_factor,
        "explanation": [item.as_dict() for item in rec.explanation],
    }


def serialize_comparison_response(product: dict, rec: Recommendation) -> dict:
    return {
        "product": product,
        "results": [
            serialize_result(r, rank=i + 1) for i, r in enumerate(rec.ranking)
        ],
        "recommendation": serialize_recommendation(rec),
    }


def serialize_stored_comparison(c: Comparison) -> dict:
    """Serialize a persisted comparison row for history (§15 GET /comparisons)."""
    return {
        "comparison_id": c.comparison_id,
        "product_id": c.product_id,
        "platform_id": c.platform_id,
        "rule_id": c.rule_id,
        "gross_revenue": _money(c.gross_revenue),
        "effective_profit": _money(c.profit),
        "margin_pct": _money(c.margin_pct),
        "breakeven_price": _money(c.breakeven_price),
        "explanation": c.explanation,
        "computed_at": c.computed_at.isoformat() if c.computed_at else None,
    }
