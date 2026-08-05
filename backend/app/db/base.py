"""Declarative base for all ORM models.

Every model inherits from ``Base`` so that ``Base.metadata`` collects all table
definitions in one place (used by ``create_all`` in tests and by Alembic
autogenerate in Phase 11).
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Common declarative base (SQLAlchemy 2.0 style)."""

    pass
