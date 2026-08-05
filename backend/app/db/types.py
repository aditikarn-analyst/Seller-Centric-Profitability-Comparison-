"""Custom SQLAlchemy column types.

``ExactNumeric`` is the storage-layer defense of NFR3/NFR5 (README §10, §13.1).

SQLite has no native fixed-point numeric type and will return Python ``float``
where ``NUMERIC`` was declared — silently reintroducing exactly the binary-float
error the money layer forbids. To prevent this:

* on **SQLite** the value is stored as canonical decimal **TEXT** and read back
  as an exact ``Decimal``;
* on **PostgreSQL** the value maps to a real ``NUMERIC(precision, scale)`` column
  (README §12 requires ``NUMERIC(12,2)`` for money);

so a stored comparison recomputes identically across both databases (NFR5).
"""

from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.types import TypeDecorator

from app.core.money import money


class ExactNumeric(TypeDecorator):
    """Dialect-aware exact decimal column.

    Values are quantized to ``scale`` decimal places on the way in, so what is
    persisted always matches the two-decimal money convention. Reuses the money
    layer for construction, so a ``float`` is rejected here too.
    """

    # Default rendering; overridden per-dialect in ``load_dialect_impl``.
    impl = Numeric
    cache_ok = True

    def __init__(self, precision: int = 12, scale: int = 2, **kwargs):
        self.precision = precision
        self.scale = scale
        self._quantum = Decimal(1).scaleb(-scale)  # scale=2 -> Decimal('0.01')
        super().__init__(precision=precision, scale=scale, **kwargs)

    def load_dialect_impl(self, dialect):
        # SQLite: store as TEXT to keep the value exact and float-free.
        if dialect.name == "sqlite":
            return dialect.type_descriptor(String(32))
        return dialect.type_descriptor(
            Numeric(self.precision, self.scale, asdecimal=True)
        )

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        quantized = money(value).quantize(self._quantum, rounding=ROUND_HALF_UP)
        # SQLite impl is String, so hand it a canonical string.
        if dialect.name == "sqlite":
            return str(quantized)
        return quantized

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        # From SQLite this is a str; from PostgreSQL already a Decimal.
        return money(value).quantize(self._quantum, rounding=ROUND_HALF_UP)


def Money() -> ExactNumeric:
    """Monetary column: ``NUMERIC(12, 2)`` semantics (README §12)."""
    return ExactNumeric(12, 2)


def Rate() -> ExactNumeric:
    """Percentage/rate column, e.g. ``commission_pct = 12.00``."""
    return ExactNumeric(5, 2)


def Dimension() -> ExactNumeric:
    """Physical dimension in cm."""
    return ExactNumeric(6, 2)
