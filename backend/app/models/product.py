"""Product model (README §12) — an SKU a seller wants to compare."""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import Dimension, Money


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    cost_price: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Money(), nullable=False)
    weight_g: Mapped[int] = mapped_column(nullable=False)
    length_cm: Mapped[Decimal] = mapped_column(Dimension(), nullable=True)
    width_cm: Mapped[Decimal] = mapped_column(Dimension(), nullable=True)
    height_cm: Mapped[Decimal] = mapped_column(Dimension(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="products")
    comparisons: Mapped[list["Comparison"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
