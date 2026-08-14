"""Platform model (README §12, extended).

A platform now carries its business classification (``platform_category``,
``business_model``), a stable ``slug``, its seller portal ``website``, and
whether it onboards third-party sellers (``seller_supported``). Comparison logic
filters on ``seller_supported`` rather than on any hardcoded platform name, so
brand-owned D2C stores exist as data but never appear in comparisons.

New columns are nullable / defaulted so historical rows and ad-hoc construction
remain valid (backward compatibility).
"""

from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Platform(Base):
    __tablename__ = "platforms"

    platform_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    slug: Mapped[Optional[str]] = mapped_column(
        String(120), unique=True, nullable=True, index=True
    )
    platform_category: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True
    )
    business_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Whether third-party sellers are supported; only True platforms are
    # eligible for profitability comparison (business rule).
    seller_supported: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    fee_rules: Mapped[list["FeeRule"]] = relationship(back_populates="platform")
    rto_rates: Mapped[list["RtoRate"]] = relationship(back_populates="platform")
