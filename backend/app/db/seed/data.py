"""Seed dataset — derived entirely from ``platform_config``.

This module intentionally holds no data of its own anymore: platform specs, fee
profiles, and RTO profiles all live in ``platform_config`` and are expanded by
its builders. This keeps a single source of truth and removes the long tuples
the earlier version carried.

============================================================================
 ⚠️  FEE / RTO VALUES ARE ILLUSTRATIVE PLACEHOLDERS. Every source_url reads
     "ILLUSTRATIVE — Replace with official seller documentation." Replace with
     verified, source-cited rates before any research claim (O1/O6).
============================================================================
"""

from app.db.seed.platform_config import (
    PLATFORM_SPECS,
    PLATFORMS,
    build_fee_rules,
    build_rto_rates,
)

# Backward-compatible names consumed by the seeder.
FEE_RULES: list[dict] = build_fee_rules()
RTO_RATES: list[dict] = build_rto_rates()

__all__ = ["PLATFORM_SPECS", "PLATFORMS", "FEE_RULES", "RTO_RATES"]
