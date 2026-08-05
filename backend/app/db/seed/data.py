"""Seed dataset — ILLUSTRATIVE placeholder rates.

============================================================================
 ⚠️  THE FEE AND RTO VALUES BELOW ARE ILLUSTRATIVE PLACEHOLDERS, NOT VERIFIED
     PLATFORM RATES. They are consistent with the worked example in README
     §13.5 and exist only to exercise the engine. Collecting the real,
     source-cited rate card (Objective O1) is team fieldwork against Amazon
     Seller Central and Flipkart Seller Hub, and MUST replace these values —
     including real ``source_url`` and ``date_accessed`` — before any research
     claim or validation run (O6). Every row's ``source_url`` is marked
     ILLUSTRATIVE precisely so an un-replaced value cannot masquerade as real.
============================================================================

The dataset is defined as a small category matrix and expanded into row dicts
at import time, keeping it DRY and easy to audit.
"""

from datetime import date
from decimal import Decimal

# --- Shared / statutory-ish defaults ---------------------------------------
DEFAULT_SLAB_G: int = 500                 # illustrative shipping weight slab
GST_PCT: Decimal = Decimal("18.00")       # §13.2
GATEWAY_PCT: Decimal = Decimal("2.00")    # illustrative payment-gateway rate
PRICE_BAND_MIN: Decimal = Decimal("0.00")
PRICE_BAND_MAX = None                     # open-ended band (illustrative)

CURRENT_FROM: date = date(2026, 3, 15)    # active rules effective date
ACCESSED: date = date(2026, 8, 5)

AMAZON_SRC = "ILLUSTRATIVE — verify at https://sellercentral.amazon.in/ (fee schedule)"
FLIPKART_SRC = "ILLUSTRATIVE — verify at https://seller.flipkart.com/ (rate card)"

PLATFORMS: list[str] = ["Amazon", "Flipkart"]

# category -> (az_comm, fk_comm, az_fixed, fk_fixed, az_ship, fk_ship)
CATEGORY_FEES: dict[str, tuple] = {
    "Home & Kitchen":            (Decimal("12.00"), Decimal("9.00"),  Decimal("40.00"), Decimal("35.00"), Decimal("65.00"), Decimal("58.00")),
    "Electronics Accessories":   (Decimal("15.00"), Decimal("13.00"), Decimal("45.00"), Decimal("40.00"), Decimal("70.00"), Decimal("62.00")),
    "Books":                     (Decimal("6.00"),  Decimal("5.00"),  Decimal("25.00"), Decimal("20.00"), Decimal("45.00"), Decimal("42.00")),
    "Clothing":                  (Decimal("18.00"), Decimal("16.00"), Decimal("50.00"), Decimal("45.00"), Decimal("75.00"), Decimal("68.00")),
    "Beauty & Personal Care":    (Decimal("14.00"), Decimal("12.00"), Decimal("40.00"), Decimal("38.00"), Decimal("60.00"), Decimal("55.00")),
    "Toys":                      (Decimal("13.00"), Decimal("11.00"), Decimal("42.00"), Decimal("38.00"), Decimal("68.00"), Decimal("60.00")),
    "Sports & Fitness":          (Decimal("12.00"), Decimal("10.00"), Decimal("45.00"), Decimal("40.00"), Decimal("80.00"), Decimal("72.00")),
    "Automotive Accessories":    (Decimal("11.00"), Decimal("9.00"),  Decimal("45.00"), Decimal("42.00"), Decimal("85.00"), Decimal("78.00")),
    "Grocery":                   (Decimal("8.00"),  Decimal("7.00"),  Decimal("30.00"), Decimal("28.00"), Decimal("55.00"), Decimal("50.00")),
}

# category -> (az_rto_pct, az_rto_cost, fk_rto_pct, fk_rto_cost)
# Chosen so Home & Kitchen reproduces §13.5: 5% x 600 = 30.00 (Amazon),
# 6% x 750 = 45.00 (Flipkart).
CATEGORY_RTO: dict[str, tuple] = {
    "Home & Kitchen":            (Decimal("5.00"), Decimal("600.00"), Decimal("6.00"), Decimal("750.00")),
    "Electronics Accessories":   (Decimal("4.00"), Decimal("700.00"), Decimal("5.00"), Decimal("720.00")),
    "Books":                     (Decimal("3.00"), Decimal("300.00"), Decimal("3.00"), Decimal("320.00")),
    "Clothing":                  (Decimal("9.00"), Decimal("500.00"), Decimal("10.00"), Decimal("520.00")),
    "Beauty & Personal Care":    (Decimal("6.00"), Decimal("450.00"), Decimal("7.00"), Decimal("470.00")),
    "Toys":                      (Decimal("5.00"), Decimal("520.00"), Decimal("6.00"), Decimal("540.00")),
    "Sports & Fitness":          (Decimal("5.00"), Decimal("650.00"), Decimal("6.00"), Decimal("680.00")),
    "Automotive Accessories":    (Decimal("4.00"), Decimal("720.00"), Decimal("5.00"), Decimal("740.00")),
    "Grocery":                   (Decimal("7.00"), Decimal("400.00"), Decimal("8.00"), Decimal("420.00")),
}


def _fee_row(platform, category, commission, fixed, shipping, source,
             effective_from=CURRENT_FROM, effective_to=None) -> dict:
    return {
        "platform": platform,
        "category": category,
        "price_band_min": PRICE_BAND_MIN,
        "price_band_max": PRICE_BAND_MAX,
        "commission_pct": commission,
        "fixed_fee": fixed,
        "shipping_slab_weight_g": DEFAULT_SLAB_G,
        "shipping_fee": shipping,
        "payment_gateway_pct": GATEWAY_PCT,
        "gst_pct": GST_PCT,
        "effective_from": effective_from,
        "effective_to": effective_to,
        "source_url": source,
        "date_accessed": ACCESSED,
    }


def _build_fee_rules() -> list[dict]:
    rows: list[dict] = []
    for category, (azc, fkc, azf, fkf, azs, fks) in CATEGORY_FEES.items():
        rows.append(_fee_row("Amazon", category, azc, azf, azs, AMAZON_SRC))
        rows.append(_fee_row("Flipkart", category, fkc, fkf, fks, FLIPKART_SRC))

    # Versioning demonstration (§12.3): a superseded historical Amazon
    # Home & Kitchen row. The active row above (12.00, effective_to=NULL)
    # supersedes it; this closed row is retained, never mutated.
    rows.append(
        _fee_row(
            "Amazon", "Home & Kitchen",
            commission=Decimal("12.50"), fixed=Decimal("40.00"), shipping=Decimal("65.00"),
            source=AMAZON_SRC,
            effective_from=date(2025, 4, 1),
            effective_to=date(2026, 3, 14),
        )
    )
    return rows


def _build_rto_rates() -> list[dict]:
    rows: list[dict] = []
    for category, (azp, azc, fkp, fkc) in CATEGORY_RTO.items():
        rows.append({
            "platform": "Amazon", "category": category,
            "rto_rate_pct": azp, "avg_rto_cost": azc,
            "effective_from": CURRENT_FROM, "source_url": AMAZON_SRC,
        })
        rows.append({
            "platform": "Flipkart", "category": category,
            "rto_rate_pct": fkp, "avg_rto_cost": fkc,
            "effective_from": CURRENT_FROM, "source_url": FLIPKART_SRC,
        })
    return rows


FEE_RULES: list[dict] = _build_fee_rules()
RTO_RATES: list[dict] = _build_rto_rates()
