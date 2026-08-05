"""Product routes (README §15, FR1)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.repositories import ProductsRepository
from app.schemas.product import ProductCreate
from app.schemas.serializers import serialize_product

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    product = ProductsRepository(db).create(
        user_id=user.user_id,
        name=payload.name,
        category=payload.category,
        cost_price=payload.cost_price,
        selling_price=payload.selling_price,
        weight_g=payload.weight_g,
        length_cm=payload.length_cm,
        width_cm=payload.width_cm,
        height_cm=payload.height_cm,
    )
    db.commit()
    return serialize_product(product)


@router.get("")
def list_products(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    products = ProductsRepository(db).list_by_user(user.user_id)
    return [serialize_product(p) for p in products]
