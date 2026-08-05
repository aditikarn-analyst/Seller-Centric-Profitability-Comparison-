"""RtoRatesRepository — resolves the category RTO rate in force on a date.

RTO rows carry only ``effective_from`` (no closing date), so the active row is
the one with the latest ``effective_from`` at or before ``on_date``.
"""

from datetime import date
from typing import Optional

from sqlalchemy import select

from app.models import RtoRate
from app.repositories.base import BaseRepository


class RtoRatesRepository(BaseRepository):
    def get_active_rate(
        self, platform_id: int, category: str, on_date: date
    ) -> Optional[RtoRate]:
        stmt = (
            select(RtoRate)
            .where(
                RtoRate.platform_id == platform_id,
                RtoRate.category == category,
                RtoRate.effective_from <= on_date,
            )
            .order_by(RtoRate.effective_from.desc())
        )
        return self.session.scalars(stmt).first()
