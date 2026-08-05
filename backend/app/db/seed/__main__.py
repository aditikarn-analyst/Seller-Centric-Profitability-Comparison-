"""CLI entry point: create tables (if needed) and seed the configured database.

    python -m app.db.seed
"""

from app.db.session import SessionLocal, engine
from app.models import Base
from app.db.seed.seeder import seed_all


def main() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        result = seed_all(session)
    finally:
        session.close()

    print("Seed complete:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print(
        "\n⚠️  Fee/RTO values are ILLUSTRATIVE placeholders (see app/db/seed/data.py). "
        "Replace with verified, source-cited rates before any research claim (O1/O6)."
    )


if __name__ == "__main__":
    main()
