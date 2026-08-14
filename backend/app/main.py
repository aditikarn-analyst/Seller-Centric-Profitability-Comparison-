"""FastAPI application entry point.

Uses an application-factory (``create_app``) rather than a bare module-level
app so tests can build a fresh, isolated instance. At Phase 0 the app exposes
only a health check; feature routers are mounted in later phases (README §15).

Run locally from the ``backend/`` directory::

    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "Seller-centric multi-platform e-commerce profitability "
            "comparison system."
        ),
    )

    # Allow the frontend dev origin(s) to call the API from the browser.
    # Token is sent in the Authorization header (not a cookie), so credentials
    # are not required. Origins are configurable via CORS_ORIGINS.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        """Liveness probe — confirms the app booted and config loaded."""
        return {"status": "ok", "environment": settings.environment}

    app.include_router(api_router)
    return app


app = create_app()
