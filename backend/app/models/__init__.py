"""ORM model package.

Importing every model here ensures they are all registered on
``Base.metadata`` before ``create_all`` / Alembic autogenerate runs, and that
string-based relationships resolve.
"""

from app.db.base import Base
from app.models.comparison import Comparison
from app.models.fee_component import FeeComponent
from app.models.fee_rule import FeeRule
from app.models.platform import Platform
from app.models.product import Product
from app.models.rto_rate import RtoRate
from app.models.user import User

__all__ = [
    "Base",
    "User",
    "Product",
    "Platform",
    "FeeRule",
    "FeeComponent",
    "RtoRate",
    "Comparison",
]
