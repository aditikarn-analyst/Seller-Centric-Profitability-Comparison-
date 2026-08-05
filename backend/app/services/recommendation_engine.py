"""Recommendation module (README §13.5, RG8).

Ranks per-platform results by effective profit, names the winner and its margin
over the next-best platform, and attaches the signed explanation of the gap.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.services.explainer import ExplanationItem, explain
from app.services.fee_engine import PlatformResult


@dataclass(frozen=True)
class Recommendation:
    winner: str
    margin_over_next: Decimal
    ranking: list[PlatformResult]              # sorted by profit, descending
    explanation: list[ExplanationItem]
    deciding_factor: Optional[str]             # largest-magnitude contribution


def rank(results: list[PlatformResult]) -> list[PlatformResult]:
    """Sort by profit descending; ties broken by platform name for determinism."""
    return sorted(results, key=lambda r: (-r.profit, r.platform_name))


def recommend(results: list[PlatformResult]) -> Recommendation:
    """Rank results and explain the winning margin.

    Raises:
        ValueError: if there are no results to rank.
    """
    if not results:
        raise ValueError("Cannot recommend from an empty result set")

    ranking = rank(results)
    winner = ranking[0]

    if len(ranking) == 1:
        return Recommendation(
            winner=winner.platform_name,
            margin_over_next=Decimal("0.00"),
            ranking=ranking,
            explanation=[],
            deciding_factor=None,
        )

    runner_up = ranking[1]
    explanation = explain(winner, runner_up)
    return Recommendation(
        winner=winner.platform_name,
        margin_over_next=winner.profit - runner_up.profit,
        ranking=ranking,
        explanation=explanation,
        deciding_factor=explanation[0].factor if explanation else None,
    )
