"""ComparisonsRepository — persisted, auditable comparison results.

A comparison links to its user indirectly through the product (see the §12
schema note surfaced in Phase 2: the comparisons table has no user_id column),
so history-by-user joins through ``products``.
"""

from typing import Optional

from sqlalchemy import select

from app.models import Comparison, Product
from app.repositories.base import BaseRepository


class ComparisonsRepository(BaseRepository):
    def add(self, comparison: Comparison) -> Comparison:
        """Stage one comparison row and flush. Caller commits the batch."""
        self.session.add(comparison)
        self.session.flush()
        return comparison

    def add_all(self, comparisons: list[Comparison]) -> list[Comparison]:
        self.session.add_all(comparisons)
        self.session.flush()
        return comparisons

    def get_by_id(self, comparison_id: int) -> Optional[Comparison]:
        return self.session.get(Comparison, comparison_id)

    def list_by_user(self, user_id: int) -> list[Comparison]:
        stmt = (
            select(Comparison)
            .join(Product, Comparison.product_id == Product.product_id)
            .where(Product.user_id == user_id)
            .order_by(Comparison.computed_at.desc())
        )
        return list(self.session.scalars(stmt))

    def list_by_product(self, product_id: int) -> list[Comparison]:
        stmt = (
            select(Comparison)
            .where(Comparison.product_id == product_id)
            .order_by(Comparison.computed_at.desc())
        )
        return list(self.session.scalars(stmt))
