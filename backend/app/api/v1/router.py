"""API v1 router — aggregates all route groups under /api/v1."""

from fastapi import APIRouter

from app.api.v1.routes import auth, compare, fee_rules, products

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(compare.router)
api_router.include_router(fee_rules.router)
