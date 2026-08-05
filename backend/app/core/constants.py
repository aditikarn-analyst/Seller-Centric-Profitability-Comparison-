"""Statutory rate constants (README §13.2, §7.7).

These are legally-fixed rates, not marketplace fees, so they live in code as
documented constants rather than in the ``fee_rules`` table. Each is traceable
to its primary source and carries a team-action note where verification is
still outstanding.
"""

from decimal import Decimal

#: GST on platform fees — statutory 18% applied to the fee base (§13.2).
GST_RATE_PCT: Decimal = Decimal("18.00")

#: TCS under Section 52, CGST Act 2017 (§7.7 / RG7 / [R10]).
#:
#: RESOLVED 2026-08-05 (project decision) to 0.5% total — 0.25% CGST + 0.25%
#: SGST/UTGST for intra-state, 0.5% IGST for inter-state supplies — consistent
#: with Notification No. 15/2024-Central Tax dated 10 July 2024.
#:
#: TEAM ACTION (O6): confirm against the primary CBIC notification text before
#: the empirical validation run; some 2026 secondary sources still cite 1%.
TCS_RATE_PCT: Decimal = Decimal("0.50")
