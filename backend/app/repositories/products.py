"""ProductsRepository — seller SKUs."""

from decimal import Decimal
from typing import Optional

from sqlalchemy import select

from app.models import Product
from app.repositories.base import BaseRepository


class ProductsRepository(BaseRepository):
    def create(
        self,
        *,
        user_id: int,
        name: str,
        category: str,
        cost_price: Decimal,
        selling_price: Decimal,
        weight_g: int,
        length_cm: Optional[Decimal] = None,
        width_cm: Optional[Decimal] = None,
        height_cm: Optional[Decimal] = None,
    ) -> Product:
        """Add a product and flush (assigns product_id). Caller commits."""
        product = Product(
            user_id=user_id,
            name=name,
            category=category,
            cost_price=cost_price,
            selling_price=selling_price,
            weight_g=weight_g,
            length_cm=length_cm,
            width_cm=width_cm,
            height_cm=height_cm,
        )
        self.session.add(product)
        self.session.flush()
        return product

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.session.get(Product, product_id)

    def list_by_user(self, user_id: int) -> list[Product]:
        stmt = (
            select(Product)
            .where(Product.user_id == user_id)
            .order_by(Product.created_at.desc())
        )
        return list(self.session.scalars(stmt))
