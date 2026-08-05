"""Database seeding package.

Run as a module to (re)seed the configured database::

    python -m app.db.seed
"""

from app.db.seed.seeder import seed_all

__all__ = ["seed_all"]
