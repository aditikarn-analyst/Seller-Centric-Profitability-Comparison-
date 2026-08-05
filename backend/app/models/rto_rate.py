"""RtoRate model (README §12) — category-level return-to-origin cost inputs."""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import Money, Rate


class RtoRate(Base):
    __tablename__ = "rto_rates"

    rto_id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int] = mapped_column(
        ForeignKey("platforms.platform_id"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    rto_rate_pct: Mapped[Decimal] = mapped_column(Rate(), nullable=False)
    avg_rto_cost: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)

    platform: Mapped["Platform"] = relationship(back_populates="rto_rates")
