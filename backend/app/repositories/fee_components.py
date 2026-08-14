"""FeeComponentsRepository — resolves applicable fee components (Option A).

Returns every component that applies to a (platform, category, selling price,
fulfilment, date) context. Date filtering runs in SQL; price-band and
fulfilment narrowing run in Python on Decimals (monetary columns are TEXT on
SQLite and would compare lexicographically in SQL — same lesson as fee_rules).
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import select

from app.models import FeeComponent
from app.repositories.base import BaseRepository


class FeeComponentsRepository(BaseRepository):
    def list_applicable(
        self,
        platform_id: int,
        category: str,
        on_date: date,
        selling_price: Decimal,
        fulfillment_type: Optional[str] = None,
    ) -> list[FeeComponent]:
        stmt = (
            select(FeeComponent)
            .where(
                FeeComponent.platform_id == platform_id,
                FeeComponent.category == category,
                FeeComponent.effective_from <= on_date,
                (FeeComponent.effective_to.is_(None))
                | (on_date < FeeComponent.effective_to),
            )
            .order_by(FeeComponent.component_type, FeeComponent.effective_from.desc())
        )
        components = list(self.session.scalars(stmt))

        def applies(c: FeeComponent) -> bool:
            if c.price_band_min is not None and selling_price < c.price_band_min:
                return False
            if c.price_band_max is not None and selling_price >= c.price_band_max:
                return False
            if (
                c.fulfillment_type is not None
                and fulfillment_type is not None
                and c.fulfillment_type != fulfillment_type
            ):
                return False
            return True

        return [c for c in components if applies(c)]

    def categories_for_platform(self, platform_id: int) -> list[str]:
        stmt = (
            select(FeeComponent.category)
            .where(FeeComponent.platform_id == platform_id)
            .distinct()
        )
        return sorted(self.session.scalars(stmt))
