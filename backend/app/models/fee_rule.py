"""FeeRule model (README §12) — a versioned, effective-dated fee schedule row.

This table is the concrete response to RG7/C4: a rate change is an INSERT with a
new ``effective_from``; the prior row is retained with a closed ``effective_to``.
No row is ever mutated, so historical comparisons stay reproducible (§12.3).
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    # Auditability (NFR4): every rate traces to a primary source.
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    date_accessed: Mapped[date] = mapped_column(Date, nullable=False)

    platform: Mapped["Platform"] = relationship(back_populates="fee_rules")
