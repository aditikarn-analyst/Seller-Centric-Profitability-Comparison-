"""Platform model (README §12) — a marketplace, e.g. Amazon, Flipkart."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Platform(Base):
    __tablename__ = "platforms"

    platform_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    fee_rules: Mapped[list["FeeRule"]] = relationship(back_populates="platform")
    rto_rates: Mapped[list["RtoRate"]] = relationship(back_populates="platform")
