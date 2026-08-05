"""Comparison model (README §12) — a persisted, auditable per-platform result.

Fee components are stored denormalised (each line, not only the total) so the
explanation is reconstructible without recomputation (§12.2). ``rule_id`` records
which fee-rule *version* produced the result, making every stored comparison
independently auditable.
"""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import Money, Rate


class Comparison(Base):
    __tablename__ = "comparisons"

    comparison_id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id"), nullable=False, index=True
    )
    platform_id: Mapped[int] = mapped_column(
        ForeignKey("platforms.platform_id"), nullable=False, index=True
    )
    rule_id: Mapped[int] = mapped_column(
        ForeignKey("fee_rules.rule_id"), nullable=False, index=True
    )

    gross_revenue: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    commission_amount: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    fixed_fee_amount: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    shipping_amount: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    gateway_amount: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    gst_amount: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    tcs_amount: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    rto_adjusted_cost: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    net_payout: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    profit: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    margin_pct: Mapped[Decimal] = mapped_column(Rate(), nullable=False)
    breakeven_price: Mapped[Decimal] = mapped_column(Money(), nullable=True)

    explanation: Mapped[dict] = mapped_column(JSON, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    product: Mapped["Product"] = relationship(back_populates="comparisons")
    platform: Mapped["Platform"] = relationship()
    rule: Mapped["FeeRule"] = relationship()
