"""Database engine and session management.

Provides the engine, a session factory, and the ``get_db`` dependency used by
FastAPI routes (Phase 9). The SQLite foreign-key pragma is enabled on every
connection so referential integrity is actually enforced in development
(README §10 trap).
"""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

_is_sqlite = settings.database_url.startswith("sqlite")

# check_same_thread=False is required for SQLite under a threaded server.
_connect_args = {"check_same_thread": False} if _is_sqlite else {}

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    echo=False,
    future=True,
)


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """Enforce foreign keys on SQLite (off by default — README §10)."""
    # Only SQLite DBAPI connections understand this pragma.
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and guarantee it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
