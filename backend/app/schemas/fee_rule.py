"""Fee-rule insert schema (README §15, FR11).

Admin inserts a new effective-dated rule without redeployment. Admin-role
gating is planned (§9); for now the endpoint requires an authenticated user.
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class FeeRuleCreate(BaseModel):
    platform_id: int
    category: str = Field(min_length=1, max_length=100)
    price_band_min: Decimal = Field(ge=0)
    price_band_max: Optional[Decimal] = Field(default=None, gt=0)
    commission_pct: Decimal = Field(ge=0)
    fixed_fee: Decimal = Field(ge=0)
    shipping_slab_weight_g: int = Field(gt=0)
    shipping_fee: Decimal = Field(ge=0)
    payment_gateway_pct: Decimal = Field(ge=0)
    gst_pct: Decimal = Field(ge=0)
    effective_from: date
    effective_to: Optional[date] = None
    source_url: str = Field(min_length=1, max_length=500)
    date_accessed: date
