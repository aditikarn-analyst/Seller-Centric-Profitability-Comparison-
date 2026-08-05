"""Comparison routes (README §15, FR2–FR8).

POST /compare is the core endpoint: it validates the product, runs the engine
for every active platform, ranks and explains, and — for an authenticated
seller — persists the product and one comparison row per platform. Anonymous
visitors get the computation without persistence (§9).
"""

import io
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_optional_user
from app.models import Comparison, User
from app.repositories import ComparisonsRepository, ProductsRepository
from app.schemas.product import CompareRequest
from app.schemas.serializers import (
    serialize_comparison_response,
    serialize_recommendation,
    serialize_stored_comparison,
)
from app.services.fee_engine import ComparisonEngine, ProductInput
from app.services.recommendation_engine import recommend

router = APIRouter(tags=["compare"])


def _persist(db, user, payload, rec) -> None:
    """Save the product and one comparison row per platform (authenticated only)."""
    product = ProductsRepository(db).create(
        user_id=user.user_id,
        name=payload.name or f"{payload.category} @ {payload.selling_price}",
        category=payload.category,
        cost_price=payload.cost_price,
        selling_price=payload.selling_price,
        weight_g=payload.weight_g,
        length_cm=payload.length_cm,
        width_cm=payload.width_cm,
        height_cm=payload.height_cm,
    )
    explanation_json = serialize_recommendation(rec)
    rows = [
        Comparison(
            product_id=product.product_id,
            platform_id=r.platform_id,
            rule_id=r.rule_id,
            gross_revenue=r.gross_revenue,
            commission_amount=r.commission,
            fixed_fee_amount=r.fixed_fee,
            shipping_amount=r.shipping,
            gateway_amount=r.gateway,
            gst_amount=r.gst,
            tcs_amount=r.tcs,
            rto_adjusted_cost=r.rto_cost,
            net_payout=r.net_settlement,
            profit=r.profit,
            margin_pct=r.margin_pct,
            breakeven_price=r.breakeven_price,
            explanation=explanation_json,
        )
        for r in rec.ranking
    ]
    ComparisonsRepository(db).add_all(rows)
    db.commit()


@router.post("/compare")
def compare(
    payload: CompareRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> dict:
    results = ComparisonEngine(db).compare(
        ProductInput(
            category=payload.category,
            cost_price=payload.cost_price,
            selling_price=payload.selling_price,
            weight_g=payload.weight_g,
        ),
        on_date=date.today(),
    )
    if not results:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "No active platform can price this product "
                "(unknown category or weight beyond all shipping slabs)."
            ),
        )

    rec = recommend(results)
    if user is not None:
        _persist(db, user, payload, rec)

    product_view = {
        "name": payload.name,
        "category": payload.category,
        "cost_price": str(payload.cost_price),
        "selling_price": str(payload.selling_price),
        "weight_g": payload.weight_g,
    }
    return serialize_comparison_response(product_view, rec)


@router.get("/comparisons")
def history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = ComparisonsRepository(db).list_by_user(user.user_id)
    return [serialize_stored_comparison(c) for c in rows]


_BULK_REQUIRED_COLUMNS = {"category", "cost_price", "selling_price", "weight_g"}
_BULK_MAX_ROWS = 500  # comfortably above NFR2's >= 200 target


@router.post("/compare/bulk")
async def compare_bulk(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Run the engine across a CSV catalogue (FR10, NFR2).

    pandas is imported here only — the single-product path avoids the import
    cost (§10). Each row is validated and priced independently; a bad row is
    reported in ``errors`` without failing the whole upload.
    """
    import pandas as pd  # local import: bulk path only

    raw = await file.read()
    try:
        frame = pd.read_csv(io.BytesIO(raw))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse CSV")

    missing = _BULK_REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise HTTPException(
            status_code=422, detail=f"CSV missing columns: {sorted(missing)}"
        )
    if len(frame) > _BULK_MAX_ROWS:
        raise HTTPException(
            status_code=422, detail=f"Too many rows (max {_BULK_MAX_ROWS})"
        )

    engine = ComparisonEngine(db)
    results: list[dict] = []
    errors: list[dict] = []
    today = date.today()

    for idx, row in frame.iterrows():
        line = int(idx) + 2  # +2: header row + 1-based
        try:
            product = ProductInput(
                category=str(row["category"]).strip(),
                cost_price=Decimal(str(row["cost_price"])),
                selling_price=Decimal(str(row["selling_price"])),
                weight_g=int(row["weight_g"]),
            )
        except (InvalidOperation, ValueError, TypeError):
            errors.append({"line": line, "error": "Invalid numeric field"})
            continue

        platform_results = engine.compare(product, on_date=today)
        if not platform_results:
            errors.append({"line": line, "error": "No platform can price this row"})
            continue

        rec = recommend(platform_results)
        results.append(
            {
                "line": line,
                "category": product.category,
                "selling_price": str(product.selling_price),
                "winner": rec.winner,
                "margin_over_next": str(rec.margin_over_next),
                "winner_profit": str(rec.ranking[0].profit),
            }
        )

    return {
        "total_rows": int(len(frame)),
        "processed": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }
