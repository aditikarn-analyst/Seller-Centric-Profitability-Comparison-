"""Repository layer.

Each repository owns all persistence queries for one aggregate, so upper layers
(services, routes) never build SQL directly. Repositories flush but do not
commit — the caller owns the transaction boundary (Unit of Work).
"""

from app.repositories.comparisons import ComparisonsRepository
from app.repositories.fee_rules import FeeRulesRepository
from app.repositories.products import ProductsRepository
from app.repositories.rto_rates import RtoRatesRepository
from app.repositories.users import UsersRepository

__all__ = [
    "FeeRulesRepository",
    "RtoRatesRepository",
    "UsersRepository",
    "ProductsRepository",
    "ComparisonsRepository",
]
