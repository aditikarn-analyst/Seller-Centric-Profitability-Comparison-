"""Deviation-report engine (README §18, O6).

Given expected profit values (from each platform's official calculator) for a
set of SKUs, run the engine and report the signed deviation per SKU/platform.
A systematic deviation is itself a reportable finding (§13.1) — the harness
records it rather than hiding it.
"""

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.seed.seeder import seed_all
from app.models import Base
from app.services.fee_engine import ComparisonEngine, ProductInput


@dataclass(frozen=True)
class ExpectedRow:
    category: str
    cost_price: Decimal
    selling_price: Decimal
    weight_g: int
    platform: str
    expected_profit: Decimal


@dataclass(frozen=True)
class DeviationRow:
    category: str
    selling_price: Decimal
    platform: str
    computed_profit: Optional[Decimal]
    expected_profit: Decimal
    deviation: Optional[Decimal]  # computed - expected; None if platform absent


@dataclass
class ValidationReport:
    rows: list[DeviationRow]
    tolerance: Decimal = Decimal("0.01")

    @property
    def _abs_devs(self) -> list[Decimal]:
        return [abs(r.deviation) for r in self.rows if r.deviation is not None]

    @property
    def max_abs_deviation(self) -> Decimal:
        return max(self._abs_devs) if self._abs_devs else Decimal("0.00")

    @property
    def mean_abs_deviation(self) -> Decimal:
        devs = self._abs_devs
        if not devs:
            return Decimal("0.00")
        return (sum(devs) / len(devs)).quantize(Decimal("0.0001"))

    @property
    def within_tolerance(self) -> int:
        return sum(1 for d in self._abs_devs if d <= self.tolerance)

    @property
    def total_compared(self) -> int:
        return len(self._abs_devs)


def build_in_memory_session() -> Session:
    """A self-contained, seeded in-memory DB so validation needs no server."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False},
        poolclass=StaticPool, future=True,
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_connection, _rec):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False, future=True)()
    seed_all(session)
    return session


def run_validation(
    expected_rows: list[ExpectedRow],
    session: Session,
    on_date: Optional[date] = None,
    tolerance: Decimal = Decimal("0.01"),
) -> ValidationReport:
    on_date = on_date or date.today()
    engine = ComparisonEngine(session)
    cache: dict[tuple, dict] = {}
    rows: list[DeviationRow] = []

    for e in expected_rows:
        key = (e.category, e.cost_price, e.selling_price, e.weight_g)
        if key not in cache:
            results = engine.compare(
                ProductInput(e.category, e.cost_price, e.selling_price, e.weight_g),
                on_date=on_date,
            )
            cache[key] = {r.platform_name: r for r in results}

        result = cache[key].get(e.platform)
        computed = result.profit if result else None
        deviation = (computed - e.expected_profit) if computed is not None else None
        rows.append(
            DeviationRow(
                category=e.category,
                selling_price=e.selling_price,
                platform=e.platform,
                computed_profit=computed,
                expected_profit=e.expected_profit,
                deviation=deviation,
            )
        )

    return ValidationReport(rows=rows, tolerance=tolerance)


def load_expected_csv(path: Path) -> list[ExpectedRow]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return [
            ExpectedRow(
                category=row["category"].strip(),
                cost_price=Decimal(row["cost_price"]),
                selling_price=Decimal(row["selling_price"]),
                weight_g=int(row["weight_g"]),
                platform=row["platform"].strip(),
                expected_profit=Decimal(row["expected_profit"]),
            )
            for row in reader
        ]
