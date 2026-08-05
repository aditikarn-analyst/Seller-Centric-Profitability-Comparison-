"""Explanation module (README §13.5, RG8).

Produces a signed, line-item decomposition of the profit gap between the winning
platform and a baseline (normally the runner-up). Each cost line contributes
``baseline_cost - winner_cost``: positive when the winner pays less on that line
(an advantage), negative when it pays more (an offset).

Because selling price and cost price are identical across platforms, these
signed contributions sum *exactly* to the profit gap — no residual, no
approximation. This exact decomposition, not the recommendation itself, is the
deliverable that addresses RG8.
"""

from dataclasses import dataclass
from decimal import Decimal

from app.services.fee_engine import PlatformResult

# (label, attribute) for each cost line that can differ between platforms.
_COST_FACTORS: list[tuple[str, str]] = [
    ("commission", "commission"),
    ("fixed_fee", "fixed_fee"),
    ("shipping", "shipping"),
    ("gateway", "gateway"),
    ("gst", "gst"),
    ("rto", "rto_cost"),
]


@dataclass(frozen=True)
class ExplanationItem:
    """One cost line's signed contribution to the winner's advantage."""

    factor: str
    delta: Decimal  # baseline_cost - winner_cost (positive = winner advantage)

    def as_dict(self) -> dict[str, str]:
        # Money as string, preserving the NFR3 exact-decimal guarantee on the wire.
        return {"factor": self.factor, "delta": str(self.delta)}


def explain(winner: PlatformResult, baseline: PlatformResult) -> list[ExplanationItem]:
    """Decompose the winner-vs-baseline profit gap into signed cost-line deltas.

    Returns non-zero contributions, ordered by magnitude (deciding factor first).
    The sum of the deltas equals ``winner.profit - baseline.profit``.
    """
    items = [
        ExplanationItem(
            factor=label,
            delta=getattr(baseline, attr) - getattr(winner, attr),
        )
        for label, attr in _COST_FACTORS
    ]
    non_zero = [item for item in items if item.delta != 0]
    non_zero.sort(key=lambda i: (-abs(i.delta), i.factor))
    return non_zero
