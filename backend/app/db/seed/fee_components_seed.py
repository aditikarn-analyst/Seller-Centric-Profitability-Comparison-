"""Source-verified fee-component seed (Option A dataset).

Every row records its OWN provenance and confidence. Nothing here is fabricated:
percentages are exact only where an official page states them; ranges are stored
as ranges; components that are not publicly disclosed are stored as
NOT_VERIFIABLE (never a guessed number). See DATA_SOURCES.md for the full table.

Dataset: manually source-verified, NOT a live feed (dataset_version 2026.08).

Audit corrections applied (Phase 2 audit I1–I5):
* I1 — GST cites the CGST statute, not marketplace pages.
* I2 — Amazon 0%-≤₹1000 is VERIFIED only for the 4 categories confirmed on the
       official page; the other 5 are PARTIALLY_VERIFIED (general policy only).
* I3 — Meesho 0% commission/payment kept VERIFIED + SECONDARY, with a note that
       the official page could not be fetched.
* I4 — Amazon "Electronics Accessories" >₹1000 is NOT generalized from the
       headphones 18% rate; it is NOT_PUBLICLY_VERIFIABLE with a note.
* I5 — Amazon payment stays NOT_PUBLICLY_VERIFIABLE.
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from app.core.dataset_metadata import FEE_DATASET_VERSION, LAST_VERIFICATION_DATE
from app.core.platform_types import (
    ComponentType,
    SourceType,
    Unit,
    ValueKind,
    VerificationStatus,
)
from app.db.seed.category_mapping import INTERNAL_CATEGORIES

EFFECTIVE_FROM = date(2026, 3, 15)
VER = FEE_DATASET_VERSION
_LV = LAST_VERIFICATION_DATE

AMAZON_SRC = ("Amazon India — Fees & Pricing", "https://sell.amazon.in/fees-and-pricing")
MEESHO_SRC = ("Meesho Supplier Pricing (0% commission) + seller guides", "https://supplier.meesho.com/pricing")
FLIPKART_SRC = ("Flipkart seller fee guides (secondary); rate card login-gated", "https://seller.flipkart.com")
# I1: GST is a statutory tax, not a marketplace fee — cite the CGST statute.
CGST_SRC = ("CGST Act, 2017 — 18% GST on marketplace services (CBIC)", "https://cbic-gst.gov.in/")

# I2: categories whose ≤₹1000 0% referral was category-confirmed on the official page.
_AMAZON_UNDER1000_CONFIRMED = {"Home & Kitchen", "Electronics Accessories", "Clothing", "Grocery"}


def _c(platform, category, ctype, kind, *, value=None, vmin=None, vmax=None, unit=None,
       status, stype, source, notes=None, band_min=Decimal("0.00"), band_max=None,
       fulfillment=None) -> dict:
    return {
        "platform": platform,
        "category": category,
        "price_band_min": band_min,
        "price_band_max": band_max,
        "fulfillment_type": fulfillment,
        "component_type": ctype.value,
        "value_kind": kind.value,
        "unit": unit.value if unit else None,
        "value": Decimal(str(value)) if value is not None else None,
        "value_min": Decimal(str(vmin)) if vmin is not None else None,
        "value_max": Decimal(str(vmax)) if vmax is not None else None,
        "verification_status": status.value,
        "source_type": stype.value,
        "source_name": source[0],
        "source_url": source[1],
        "last_verified": _LV,
        "notes": notes,
        "effective_from": EFFECTIVE_FROM,
        "effective_to": None,
        "dataset_version": VER,
    }


# Amazon ≥₹1000 referral by internal category.
#   ("RANGE", min, max, note)        -> bounded percent range, PARTIALLY_VERIFIED
#   ("NOTV", None, None, note)       -> not publicly verifiable (custom note)
#   None                             -> not captured this cycle -> NOT_PUBLICLY_VERIFIABLE (generic note)
_AMAZON_ABOVE_1000: dict[str, Optional[tuple]] = {
    "Home & Kitchen": ("RANGE", 4.5, 8.0, "Small appliances 4.5% (₹1k–5k)–8% (>₹5k); refrigerators 5%"),
    # I4: 18% is the headphones subcategory only — do NOT generalize to the umbrella.
    "Electronics Accessories": ("NOTV", None, None,
                                 "Headphones subcategory is 18% (>₹1000), but the umbrella 'Electronics "
                                 "Accessories' spans varying rates; not uniformly verifiable — not generalized."),
    "Clothing": ("RANGE", 7.0, 24.0, "Apparel spread: baby 7% … shorts 24% (>₹1000)"),
    "Grocery": ("RANGE", 8.0, 9.0, "Spices 8% / dried fruits 9% (>₹1000)"),
    "Books": None,
    "Beauty & Personal Care": None,
    "Toys": None,
    "Sports & Fitness": None,
    "Automotive Accessories": None,
}


def _amazon_rows() -> list[dict]:
    rows: list[dict] = []
    for cat in INTERNAL_CATEGORIES:
        # I2: 0% ≤ ₹1000 — VERIFIED only for the 4 confirmed categories.
        under_status = (
            VerificationStatus.VERIFIED if cat in _AMAZON_UNDER1000_CONFIRMED
            else VerificationStatus.PARTIALLY_VERIFIED
        )
        under_note = (
            "0% referral fee on items ≤ ₹1000 (official, category-confirmed)."
            if cat in _AMAZON_UNDER1000_CONFIRMED
            else "0% referral ≤ ₹1000 inferred from Amazon's general '1800+ categories' policy; "
                 "category-specific confirmation not captured this cycle."
        )
        rows.append(_c("Amazon", cat, ComponentType.COMMISSION, ValueKind.PERCENT,
                       value=0, unit=Unit.PCT, band_min=Decimal("0.00"), band_max=Decimal("1000.00"),
                       status=under_status, stype=SourceType.OFFICIAL, source=AMAZON_SRC, notes=under_note))

        above = _AMAZON_ABOVE_1000[cat]
        if above is None or above[0] == "NOTV":
            note = (above[3] if above else
                    "Per-subcategory referral ≥ ₹1000 not captured from official page this cycle.")
            rows.append(_c("Amazon", cat, ComponentType.COMMISSION, ValueKind.NOT_VERIFIABLE,
                           band_min=Decimal("1000.00"), status=VerificationStatus.NOT_PUBLICLY_VERIFIABLE,
                           stype=SourceType.OFFICIAL, source=AMAZON_SRC, notes=note))
        else:  # RANGE
            rows.append(_c("Amazon", cat, ComponentType.COMMISSION, ValueKind.RANGE,
                           vmin=above[1], vmax=above[2], unit=Unit.PCT, band_min=Decimal("1000.00"),
                           status=VerificationStatus.PARTIALLY_VERIFIED, stype=SourceType.OFFICIAL,
                           source=AMAZON_SRC, notes=above[3]))

        rows.append(_c("Amazon", cat, ComponentType.FIXED_FEE, ValueKind.RANGE, vmin=1, vmax=None,
                       unit=Unit.INR, status=VerificationStatus.PARTIALLY_VERIFIED, stype=SourceType.OFFICIAL,
                       source=AMAZON_SRC, notes="Closing fee starts at ₹1; varies by price range & fulfilment."))
        rows.append(_c("Amazon", cat, ComponentType.SHIPPING, ValueKind.RANGE, vmin=37, vmax=None,
                       unit=Unit.INR, status=VerificationStatus.PARTIALLY_VERIFIED, stype=SourceType.OFFICIAL,
                       source=AMAZON_SRC, notes="Weight handling starts at ₹37; varies by volume & distance."))
        # I5: payment fee not disclosed → NOT_PUBLICLY_VERIFIABLE (absence ≠ zero).
        rows.append(_c("Amazon", cat, ComponentType.PAYMENT, ValueKind.NOT_VERIFIABLE,
                       status=VerificationStatus.NOT_PUBLICLY_VERIFIABLE, stype=SourceType.OFFICIAL,
                       source=AMAZON_SRC, notes="No separate payment/collection fee stated; absence does not prove 0."))
        rows.append(_c("Amazon", cat, ComponentType.GST, ValueKind.PERCENT, value=18, unit=Unit.PCT,
                       status=VerificationStatus.VERIFIED, stype=SourceType.OFFICIAL, source=CGST_SRC,
                       notes="Statutory 18% GST on marketplace fees (CGST Act); calculated, not a marketplace fee."))
    return rows


def _meesho_rows() -> list[dict]:
    rows: list[dict] = []
    meesho_note = ("0% commission across all categories since Aug 2022. Official Meesho pricing page could not "
                   "be directly fetched during automated verification; value corroborated through secondary sources.")
    for cat in INTERNAL_CATEGORIES:
        rows.append(_c("Meesho", cat, ComponentType.COMMISSION, ValueKind.PERCENT, value=0, unit=Unit.PCT,
                       status=VerificationStatus.VERIFIED, stype=SourceType.SECONDARY, source=MEESHO_SRC,
                       notes=meesho_note))
        rows.append(_c("Meesho", cat, ComponentType.PAYMENT, ValueKind.PERCENT, value=0, unit=Unit.PCT,
                       status=VerificationStatus.VERIFIED, stype=SourceType.SECONDARY, source=MEESHO_SRC,
                       notes="No payment gateway / COD charge to supplier. " + meesho_note))
        rows.append(_c("Meesho", cat, ComponentType.FIXED_FEE, ValueKind.RANGE, vmin=25, vmax=30, unit=Unit.INR,
                       status=VerificationStatus.PARTIALLY_VERIFIED, stype=SourceType.SECONDARY, source=MEESHO_SRC,
                       notes="Fixed platform fee ₹25–30 (secondary); exact per order."))
        rows.append(_c("Meesho", cat, ComponentType.SHIPPING, ValueKind.RANGE, vmin=27, vmax=120, unit=Unit.INR,
                       status=VerificationStatus.PARTIALLY_VERIFIED, stype=SourceType.SECONDARY, source=MEESHO_SRC,
                       notes="Logistics ₹27–120 by weight/zone (secondary)."))
        rows.append(_c("Meesho", cat, ComponentType.GST, ValueKind.PERCENT, value=18, unit=Unit.PCT,
                       status=VerificationStatus.VERIFIED, stype=SourceType.OFFICIAL, source=CGST_SRC,
                       notes="Statutory 18% GST on marketplace fees (CGST Act); calculated, not a marketplace fee."))
    return rows


def _flipkart_rows() -> list[dict]:
    rows: list[dict] = []
    for cat in INTERNAL_CATEGORIES:
        rows.append(_c("Flipkart", cat, ComponentType.COMMISSION, ValueKind.PERCENT, value=0, unit=Unit.PCT,
                       band_min=Decimal("0.00"), band_max=Decimal("1000.00"),
                       status=VerificationStatus.PARTIALLY_VERIFIED, stype=SourceType.SECONDARY, source=FLIPKART_SRC,
                       notes="0% commission on items < ₹1000 for eligible sellers (from 14 Nov 2025); eligibility applies."))
        rows.append(_c("Flipkart", cat, ComponentType.COMMISSION, ValueKind.NOT_VERIFIABLE,
                       band_min=Decimal("1000.00"), status=VerificationStatus.NOT_PUBLICLY_VERIFIABLE,
                       stype=SourceType.SECONDARY, source=FLIPKART_SRC,
                       notes="Per-category commission ≥ ₹1000 is behind Flipkart Seller Hub login; not publicly verifiable."))
        rows.append(_c("Flipkart", cat, ComponentType.PAYMENT, ValueKind.PERCENT, value=2, unit=Unit.PCT,
                       status=VerificationStatus.PARTIALLY_VERIFIED, stype=SourceType.SECONDARY, source=FLIPKART_SRC,
                       notes="Collection fee ~2% of order value (secondary)."))
        rows.append(_c("Flipkart", cat, ComponentType.FIXED_FEE, ValueKind.RANGE, vmin=8, vmax=35, unit=Unit.INR,
                       status=VerificationStatus.PARTIALLY_VERIFIED, stype=SourceType.SECONDARY, source=FLIPKART_SRC,
                       notes="Fixed/closing fee ₹8–35 by price/seller tier (secondary)."))
        rows.append(_c("Flipkart", cat, ComponentType.SHIPPING, ValueKind.RANGE, vmin=0, vmax=None, unit=Unit.INR,
                       status=VerificationStatus.PARTIALLY_VERIFIED, stype=SourceType.SECONDARY, source=FLIPKART_SRC,
                       notes="Free for most items < 500g (from 14 Nov 2025); weight/zone-dependent otherwise."))
        rows.append(_c("Flipkart", cat, ComponentType.GST, ValueKind.PERCENT, value=18, unit=Unit.PCT,
                       status=VerificationStatus.VERIFIED, stype=SourceType.OFFICIAL, source=CGST_SRC,
                       notes="Statutory 18% GST on marketplace fees (CGST Act); calculated, not a marketplace fee."))
    return rows


def build_fee_components() -> list[dict]:
    return _amazon_rows() + _meesho_rows() + _flipkart_rows()


FEE_COMPONENTS: list[dict] = build_fee_components()
