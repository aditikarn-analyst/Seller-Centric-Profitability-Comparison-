"""FeeRule model (README §12) — a versioned, effective-dated fee schedule row.

This table is the concrete response to RG7/C4: a rate change is an INSERT with a
new ``effective_from``; the prior row is retained with a closed ``effective_to``.
No row is ever mutated, so historical comparisons stay reproducible (§12.3).
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.platform_types import SourceType, VerificationStatus
from app.db.base import Base
from app.db.types import Money, Rate


class FeeRule(Base):
    __tablename__ = "fee_rules"

    rule_id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int] = mapped_column(
        ForeignKey("platforms.platform_id"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    price_band_min: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    price_band_max: Mapped[Decimal] = mapped_column(Money(), nullable=True)

    commission_pct: Mapped[Decimal] = mapped_column(Rate(), nullable=False)
    fixed_fee: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    shipping_slab_weight_g: Mapped[int] = mapped_column(nullable=False)
    shipping_fee: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    payment_gateway_pct: Mapped[Decimal] = mapped_column(Rate(), nullable=False)
    gst_pct: Mapped[Decimal] = mapped_column(Rate(), nullable=False)

    # Versioning: effective_to is NULL for the currently-active row.
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    effective_to: Mapped[date] = mapped_column(Date, nullable=True)

    # Fulfilment model this rule applies to (None = any). FulfillmentType value.
    fulfillment_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Auditability / provenance (NFR4). Every rate traces to a cited source and
    # carries an explicit confidence level. Defaults deliberately label any row
    # that omits them as ILLUSTRATIVE / ASSUMED — so placeholder data can never
    # masquerade as verified.
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    source_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    source_type: Mapped[str] = mapped_column(
        String(20), default=SourceType.ILLUSTRATIVE.value, nullable=False
    )
    verification_status: Mapped[str] = mapped_column(
        String(30), default=VerificationStatus.ASSUMED.value, nullable=False
    )
    date_accessed: Mapped[date] = mapped_column(Date, nullable=False)
    last_verified: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    platform: Mapped["Platform"] = relationship(back_populates="fee_rules")
