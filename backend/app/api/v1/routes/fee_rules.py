"""Fee-rule routes (README §15, FR11).

GET lists the rules active today. POST inserts a new effective-dated rule
without redeployment — the versioning mechanism (RG7/C4). Admin-role gating is
planned (§9); for now both require an authenticated user.
"""

from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import FeeRule, Platform, User
from app.schemas.fee_rule import FeeRuleCreate

router = APIRouter(prefix="/fee-rules", tags=["fee-rules"])


def _serialize_rule(rule: FeeRule) -> dict:
    return {
        "rule_id": rule.rule_id,
        "platform_id": rule.platform_id,
        "category": rule.category,
        "commission_pct": str(rule.commission_pct),
        "fixed_fee": str(rule.fixed_fee),
        "shipping_fee": str(rule.shipping_fee),
        "payment_gateway_pct": str(rule.payment_gateway_pct),
        "gst_pct": str(rule.gst_pct),
        "effective_from": rule.effective_from.isoformat(),
        "effective_to": rule.effective_to.isoformat() if rule.effective_to else None,
        "source_url": rule.source_url,
    }


@router.get("")
def list_active_rules(
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    today = date.today()
    stmt = select(FeeRule).where(
        FeeRule.effective_from <= today,
        (FeeRule.effective_to.is_(None)) | (today < FeeRule.effective_to),
    )
    return [_serialize_rule(r) for r in db.scalars(stmt)]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_fee_rule(
    payload: FeeRuleCreate,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    # Versioning contract: an update is an INSERT (§12.3), never a mutation.
    platform = db.get(Platform, payload.platform_id)
    if platform is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Unknown platform_id")

    rule = FeeRule(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return _serialize_rule(rule)
