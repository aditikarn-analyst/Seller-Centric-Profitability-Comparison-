"""Empirical validation harness (README §18, O6 / C6).

Compares engine output against expected values taken from each platform's own
fee calculator, over a set of real SKUs, and reports the deviation. This is the
empirical claim that distinguishes a research artefact from a software demo (C6).
"""

from app.core.money import money  # noqa: F401  (ensures package imports cleanly)
