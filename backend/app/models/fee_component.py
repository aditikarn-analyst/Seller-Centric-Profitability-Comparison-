"""FeeComponent model — normalized, per-component marketplace fee data.

Each row is ONE fee component (commission, fixed fee, shipping, payment, GST,
RTO, …) for a (platform, category, price band, fulfilment) context, carrying
its OWN provenance and confidence. This is the concrete answer to the
research-integrity requirement that "every fee component must have its own
provenance": within one marketplace, commission can be VERIFIED while shipping
is PARTIALLY_VERIFIED and payment is NOT_PUBLICLY_VERIFIABLE — represented as
three independent rows.

Value representation (never fabricated):
* PERCENT  -> ``value`` (unit PCT), e.g. 5% commission
* EXACT    -> ``value`` (unit INR), e.g. ₹30 fixed fee
* RANGE    -> ``value_min`` / ``value_max`` (unit INR or PCT); ``value_max`` may
             be NULL for an open-ended "starts at ₹X" range
* NOT_VERIFIABLE -> all values NULL; the component is known to exist but its
             amount is not publicly disclosed (distinct from "no fee")
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import ExactNumeric, Money


class FeeComponent(Base):
    __tablename__ = "fee_components"

    component_id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int] = mapped_column(
        ForeignKey("platforms.platform_id"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Applicability conditions (all optional; NULL = applies regardless).
    price_band_min: Mapped[Optional[Decimal]] = mapped_column(Money(), nullable=True)
    price_band_max: Mapped[Optional[Decimal]] = mapped_column(Money(), nullable=True)
    fulfillment_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # What this component is and how its value is expressed.
    component_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    value_kind: Mapped[str] = mapped_column(String(20), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)

    # Values (nullable — NULL is meaningful only alongside NOT_VERIFIABLE, or as
    # the open upper bound of a RANGE). 12,4 accommodates both INR and precise %.
    value: Mapped[Optional[Decimal]] = mapped_column(ExactNumeric(12, 4), nullable=True)
    value_min: Mapped[Optional[Decimal]] = mapped_column(ExactNumeric(12, 4), nullable=True)
    value_max: Mapped[Optional[Decimal]] = mapped_column(ExactNumeric(12, 4), nullable=True)

    # Per-component provenance & confidence.
    verification_status: Mapped[str] = mapped_column(String(30), nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    last_verified: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(600), nullable=True)

    # Versioning / reproducibility.
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    dataset_version: Mapped[str] = mapped_column(String(20), nullable=False)

    platform: Mapped["Platform"] = relationship()
