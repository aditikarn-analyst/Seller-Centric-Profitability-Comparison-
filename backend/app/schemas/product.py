"""Product / comparison request schemas (README §15).

Pydantic rejects malformed input at the boundary (§10): a non-positive price or
weight, or a missing category, never reaches the engine. Monetary fields are
typed Decimal so pydantic-core parses them losslessly from the JSON literal.
"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    cost_price: Decimal = Field(gt=0)
    selling_price: Decimal = Field(gt=0)
    weight_g: int = Field(gt=0)
    length_cm: Optional[Decimal] = Field(default=None, gt=0)
    width_cm: Optional[Decimal] = Field(default=None, gt=0)
    height_cm: Optional[Decimal] = Field(default=None, gt=0)
    # Advanced input (optional): "SELF_SHIP" | "PLATFORM_FULFILLED". None = any.
    fulfillment_type: Optional[str] = Field(default=None, max_length=30)


class ProductCreate(CompareRequest):
    """Same shape as a comparison request; name is required for a saved product."""

    name: str = Field(min_length=1, max_length=255)
