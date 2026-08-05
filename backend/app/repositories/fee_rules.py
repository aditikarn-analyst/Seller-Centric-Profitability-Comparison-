"""FeeRulesRepository — resolves the fee rule in force for a given context.

Resolution is the heart of RG7/C4: given a platform, category, and date, return
the fee-rule *version* that was effective then, further narrowed by the
product's price band and weight slab.

Note on filtering strategy: date filtering runs in SQL (Date columns sort
correctly), but price-band and weight-slab filtering runs in Python on Decimal
objects. Monetary columns are stored as TEXT on SQLite (ExactNumeric, §Phase 2)
and would compare lexicographically — not numerically — inside a SQL WHERE.
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import select

from app.models import FeeRule
from app.repositories.base import BaseRepository


class FeeRulesRepository(BaseRepository):
    def _active_by_date(self, platform_id: int, category: str, on_date: date):
        """Rows effective on ``on_date`` (SQL-side date filter only)."""
        stmt = (
            select(FeeRule)
            .where(
                FeeRule.platform_id == platform_id,
                FeeRule.category == category,
                FeeRule.effective_from <= on_date,
                (FeeRule.effective_to.is_(None)) | (on_date < FeeRule.effective_to),
            )
            .order_by(FeeRule.effective_from.desc())
        )
        return list(self.session.scalars(stmt))

    def get_active_rule(
        self,
        platform_id: int,
        category: str,
        on_date: date,
        selling_price: Optional[Decimal] = None,
        weight_g: Optional[int] = None,
    ) -> Optional[FeeRule]:
        """Return the single applicable fee rule, or ``None`` if none matches.

        Among rows effective on ``on_date``, keep those whose price band
        contains ``selling_price`` and whose shipping slab accommodates
        ``weight_g``; prefer the most recent effective date, then the tightest
        (smallest) shipping slab.
        """
        candidates = self._active_by_date(platform_id, category, on_date)

        def matches(rule: FeeRule) -> bool:
            if selling_price is not None:
                if selling_price < rule.price_band_min:
                    return False
                if (
                    rule.price_band_max is not None
                    and selling_price >= rule.price_band_max
                ):
                    return False
            if weight_g is not None and rule.shipping_slab_weight_g < weight_g:
                return False
            return True

        matching = [r for r in candidates if matches(r)]
        if not matching:
            return None

        matching.sort(
            key=lambda r: (-r.effective_from.toordinal(), r.shipping_slab_weight_g)
        )
        return matching[0]

    def list_active(
        self, platform_id: int, category: str, on_date: date
    ) -> list[FeeRule]:
        """All rules effective on ``on_date`` (every price band and slab).

        The break-even solver (§13.4) needs every band the product could occupy,
        not just the one matching a specific selling price.
        """
        return self._active_by_date(platform_id, category, on_date)

    def get_by_id(self, rule_id: int) -> Optional[FeeRule]:
        """Fetch a specific rule version (reproducibility / audit, NFR5)."""
        return self.session.get(FeeRule, rule_id)
