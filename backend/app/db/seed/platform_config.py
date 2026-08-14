"""Platform configuration — the declarative source for all seed data.

Everything the seeder needs is derived from ``PLATFORM_SPECS`` and the
per-category fee/RTO profiles below via helper builders, so there is no
duplicated per-platform marketplace logic and ``PLATFORMS`` is derived, never
hand-maintained. Adding a platform = append one ``PlatformSpec``. Adding a
category = extend the applicable list for a platform category.

============================================================================
 ⚠️  ALL FEE AND RTO VALUES ARE ILLUSTRATIVE PLACEHOLDERS, NOT VERIFIED RATES.
     Every generated row's source_url reads
     "ILLUSTRATIVE — Replace with official seller documentation."
     Replace with real, source-cited data before any research claim (O1/O6).
============================================================================
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional

from app.core.platform_types import PlatformCategory, SellerSupport

# --------------------------------------------------------------------------- #
# Shared constants
# --------------------------------------------------------------------------- #
SOURCE_URL = "ILLUSTRATIVE — Replace with official seller documentation."
CURRENT_FROM = date(2026, 3, 15)
ACCESSED = date(2026, 8, 6)
DEFAULT_GATEWAY_PCT = Decimal("2.00")
DEFAULT_GST_PCT = Decimal("18.00")
DEFAULT_SLAB_G = 500


# --------------------------------------------------------------------------- #
# Value objects
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class FeeProfile:
    commission_pct: Decimal
    fixed_fee: Decimal
    shipping_fee: Decimal
    payment_gateway_pct: Decimal = DEFAULT_GATEWAY_PCT
    gst_pct: Decimal = DEFAULT_GST_PCT
    shipping_slab_weight_g: int = DEFAULT_SLAB_G


@dataclass(frozen=True)
class RtoProfile:
    rto_rate_pct: Decimal
    avg_rto_cost: Decimal


@dataclass(frozen=True)
class CategoryProfile:
    """Default economics + applicable product categories for a platform type."""

    fee: FeeProfile
    rto: RtoProfile
    product_categories: tuple[str, ...]


@dataclass(frozen=True)
class PlatformSpec:
    name: str
    slug: str
    category: PlatformCategory
    seller_support: SellerSupport
    business_model: str
    website: str

    @property
    def seller_supported(self) -> bool:
        return self.seller_support.participates


# --------------------------------------------------------------------------- #
# Per-platform-category default profiles (illustrative)
#
# New-marketplace defaults are intentionally less competitive than the
# Amazon/Flipkart overrides below, so the §13.5 worked example (Flipkart wins
# over Amazon) is preserved even as more platforms participate.
# --------------------------------------------------------------------------- #
CATEGORY_PROFILES: dict[PlatformCategory, CategoryProfile] = {
    PlatformCategory.MARKETPLACE: CategoryProfile(
        fee=FeeProfile(Decimal("20.00"), Decimal("50.00"), Decimal("70.00")),
        rto=RtoProfile(Decimal("8.00"), Decimal("600.00")),
        product_categories=(
            "Home & Kitchen", "Electronics", "Mobiles", "Accessories",
            "Clothing", "Footwear", "Books", "Toys", "Sports", "Grocery",
        ),
    ),
    PlatformCategory.FASHION: CategoryProfile(
        fee=FeeProfile(Decimal("22.00"), Decimal("55.00"), Decimal("75.00")),
        rto=RtoProfile(Decimal("12.00"), Decimal("550.00")),
        product_categories=("Clothing", "Fashion", "Footwear", "Accessories", "Jewellery"),
    ),
    PlatformCategory.BEAUTY: CategoryProfile(
        fee=FeeProfile(Decimal("18.00"), Decimal("45.00"), Decimal("60.00")),
        rto=RtoProfile(Decimal("7.00"), Decimal("450.00")),
        product_categories=("Beauty", "Personal Care", "Health"),
    ),
    PlatformCategory.ELECTRONICS: CategoryProfile(
        fee=FeeProfile(Decimal("8.00"), Decimal("60.00"), Decimal("90.00")),
        rto=RtoProfile(Decimal("4.00"), Decimal("800.00")),
        product_categories=("Electronics", "Mobiles", "Laptops", "Accessories", "Home Appliances"),
    ),
    PlatformCategory.GROCERY: CategoryProfile(
        fee=FeeProfile(Decimal("12.00"), Decimal("30.00"), Decimal("55.00")),
        rto=RtoProfile(Decimal("6.00"), Decimal("400.00")),
        product_categories=("Grocery", "FMCG", "Baby Products", "Pet Supplies"),
    ),
    PlatformCategory.QUICK_COMMERCE: CategoryProfile(
        fee=FeeProfile(Decimal("25.00"), Decimal("40.00"), Decimal("50.00")),
        rto=RtoProfile(Decimal("5.00"), Decimal("350.00")),
        product_categories=("Grocery", "FMCG", "Personal Care"),
    ),
    PlatformCategory.PHARMACY: CategoryProfile(
        fee=FeeProfile(Decimal("15.00"), Decimal("35.00"), Decimal("50.00")),
        rto=RtoProfile(Decimal("5.00"), Decimal("300.00")),
        product_categories=("Pharmacy", "Health", "Personal Care"),
    ),
    PlatformCategory.FURNITURE: CategoryProfile(
        fee=FeeProfile(Decimal("18.00"), Decimal("80.00"), Decimal("150.00"), shipping_slab_weight_g=5000),
        rto=RtoProfile(Decimal("10.00"), Decimal("900.00")),
        product_categories=("Furniture", "Home & Kitchen", "Home Appliances"),
    ),
    PlatformCategory.B2B: CategoryProfile(
        fee=FeeProfile(Decimal("6.00"), Decimal("25.00"), Decimal("60.00")),
        rto=RtoProfile(Decimal("3.00"), Decimal("500.00")),
        product_categories=("Electronics", "Accessories", "Office Supplies", "FMCG", "Automotive"),
    ),
    # D2C has no seller fee rules (no third-party sellers).
    PlatformCategory.D2C: CategoryProfile(
        fee=FeeProfile(Decimal("0.00"), Decimal("0.00"), Decimal("0.00")),
        rto=RtoProfile(Decimal("0.00"), Decimal("0.00")),
        product_categories=(),
    ),
}


# --------------------------------------------------------------------------- #
# Amazon / Flipkart per-category overrides (preserve existing behaviour & §13.5)
# Names stay "Amazon"/"Flipkart" for backward compatibility; slug carries the
# full identity.
# --------------------------------------------------------------------------- #
def _mk(comm: str, fixed: str, ship: str) -> FeeProfile:
    return FeeProfile(Decimal(comm), Decimal(fixed), Decimal(ship))


def _rto(pct: str, cost: str) -> RtoProfile:
    return RtoProfile(Decimal(pct), Decimal(cost))


_AMAZON_FEES = {
    "Home & Kitchen": _mk("12.00", "40.00", "65.00"),
    "Electronics Accessories": _mk("15.00", "45.00", "70.00"),
    "Books": _mk("6.00", "25.00", "45.00"),
    "Clothing": _mk("18.00", "50.00", "75.00"),
    "Beauty & Personal Care": _mk("14.00", "40.00", "60.00"),
    "Toys": _mk("13.00", "42.00", "68.00"),
    "Sports & Fitness": _mk("12.00", "45.00", "80.00"),
    "Automotive Accessories": _mk("11.00", "45.00", "85.00"),
    "Grocery": _mk("8.00", "30.00", "55.00"),
}
_FLIPKART_FEES = {
    "Home & Kitchen": _mk("9.00", "35.00", "58.00"),
    "Electronics Accessories": _mk("13.00", "40.00", "62.00"),
    "Books": _mk("5.00", "20.00", "42.00"),
    "Clothing": _mk("16.00", "45.00", "68.00"),
    "Beauty & Personal Care": _mk("12.00", "38.00", "55.00"),
    "Toys": _mk("11.00", "38.00", "60.00"),
    "Sports & Fitness": _mk("10.00", "40.00", "72.00"),
    "Automotive Accessories": _mk("9.00", "42.00", "78.00"),
    "Grocery": _mk("7.00", "28.00", "50.00"),
}
_AMAZON_RTO = {
    "Home & Kitchen": _rto("5.00", "600.00"),
    "Electronics Accessories": _rto("4.00", "700.00"),
    "Books": _rto("3.00", "300.00"),
    "Clothing": _rto("9.00", "500.00"),
    "Beauty & Personal Care": _rto("6.00", "450.00"),
    "Toys": _rto("5.00", "520.00"),
    "Sports & Fitness": _rto("5.00", "650.00"),
    "Automotive Accessories": _rto("4.00", "720.00"),
    "Grocery": _rto("7.00", "400.00"),
}
_FLIPKART_RTO = {
    "Home & Kitchen": _rto("6.00", "750.00"),
    "Electronics Accessories": _rto("5.00", "720.00"),
    "Books": _rto("3.00", "320.00"),
    "Clothing": _rto("10.00", "520.00"),
    "Beauty & Personal Care": _rto("7.00", "470.00"),
    "Toys": _rto("6.00", "540.00"),
    "Sports & Fitness": _rto("6.00", "680.00"),
    "Automotive Accessories": _rto("5.00", "740.00"),
    "Grocery": _rto("8.00", "420.00"),
}

# slug -> {category: FeeProfile}
FEE_OVERRIDES: dict[str, dict[str, FeeProfile]] = {
    "amazon-india": _AMAZON_FEES,
    "flipkart": _FLIPKART_FEES,
}
RTO_OVERRIDES: dict[str, dict[str, RtoProfile]] = {
    "amazon-india": _AMAZON_RTO,
    "flipkart": _FLIPKART_RTO,
}

# Superseded historical fee rows (versioning demo, §12.3): slug -> list of
# (category, FeeProfile, effective_from, effective_to).
HISTORICAL_FEES: dict[str, list[tuple]] = {
    "amazon-india": [
        ("Home & Kitchen", _mk("12.50", "40.00", "65.00"), date(2025, 4, 1), date(2026, 3, 14)),
    ],
}


# --------------------------------------------------------------------------- #
# Platform specifications
# --------------------------------------------------------------------------- #
def _spec(name, slug, category, support, website) -> PlatformSpec:
    return PlatformSpec(
        name=name, slug=slug, category=category, seller_support=support,
        business_model=category.value, website=website,
    )


PLATFORM_SPECS: tuple[PlatformSpec, ...] = (
    # 1. General multi-vendor marketplaces
    _spec("Amazon", "amazon-india", PlatformCategory.MARKETPLACE, SellerSupport.FULL, "https://sellercentral.amazon.in"),
    _spec("Flipkart", "flipkart", PlatformCategory.MARKETPLACE, SellerSupport.FULL, "https://seller.flipkart.com"),
    _spec("Meesho", "meesho", PlatformCategory.MARKETPLACE, SellerSupport.FULL, "https://supplier.meesho.com"),
    _spec("JioMart Marketplace", "jiomart-marketplace", PlatformCategory.MARKETPLACE, SellerSupport.FULL, "https://seller.jiomart.com"),
    _spec("Tata CLiQ Marketplace", "tatacliq-marketplace", PlatformCategory.MARKETPLACE, SellerSupport.FULL, "https://www.tatacliq.com"),
    _spec("Snapdeal", "snapdeal", PlatformCategory.MARKETPLACE, SellerSupport.FULL, "https://seller.snapdeal.com"),
    _spec("ShopClues", "shopclues", PlatformCategory.MARKETPLACE, SellerSupport.FULL, "https://seller.shopclues.com"),
    # 2. Fashion marketplaces
    _spec("Myntra", "myntra", PlatformCategory.FASHION, SellerSupport.FULL, "https://partner.myntra.com"),
    _spec("AJIO", "ajio", PlatformCategory.FASHION, SellerSupport.FULL, "https://seller.ajio.com"),
    # 3. Beauty marketplaces
    _spec("Nykaa", "nykaa", PlatformCategory.BEAUTY, SellerSupport.FULL, "https://seller.nykaa.com"),
    _spec("Tira", "tira", PlatformCategory.BEAUTY, SellerSupport.FULL, "https://www.tirabeauty.com"),
    _spec("Purplle", "purplle", PlatformCategory.BEAUTY, SellerSupport.FULL, "https://sell.purplle.com"),
    # 4. Electronics marketplaces (partial seller support)
    _spec("Croma", "croma", PlatformCategory.ELECTRONICS, SellerSupport.PARTIAL, "https://www.croma.com"),
    _spec("Vijay Sales", "vijay-sales", PlatformCategory.ELECTRONICS, SellerSupport.PARTIAL, "https://www.vijaysales.com"),
    _spec("Reliance Digital", "reliance-digital", PlatformCategory.ELECTRONICS, SellerSupport.PARTIAL, "https://www.reliancedigital.in"),
    # 5. Grocery / FMCG marketplaces (partial)
    _spec("BigBasket", "bigbasket", PlatformCategory.GROCERY, SellerSupport.PARTIAL, "https://www.bigbasket.com"),
    _spec("JioMart Grocery", "jiomart-grocery", PlatformCategory.GROCERY, SellerSupport.PARTIAL, "https://www.jiomart.com"),
    # 6. Quick commerce (limited). BigBasket Now classified here (deduped).
    _spec("Blinkit", "blinkit", PlatformCategory.QUICK_COMMERCE, SellerSupport.LIMITED, "https://blinkit.com"),
    _spec("Zepto", "zepto", PlatformCategory.QUICK_COMMERCE, SellerSupport.LIMITED, "https://www.zeptonow.com"),
    _spec("Swiggy Instamart", "swiggy-instamart", PlatformCategory.QUICK_COMMERCE, SellerSupport.LIMITED, "https://www.swiggy.com/instamart"),
    _spec("BigBasket Now", "bigbasket-now", PlatformCategory.QUICK_COMMERCE, SellerSupport.LIMITED, "https://www.bigbasket.com"),
    # 7. Pharmacy (partial)
    _spec("Tata 1mg", "tata-1mg", PlatformCategory.PHARMACY, SellerSupport.PARTIAL, "https://www.1mg.com"),
    _spec("PharmEasy", "pharmeasy", PlatformCategory.PHARMACY, SellerSupport.PARTIAL, "https://pharmeasy.in"),
    _spec("Apollo 24|7", "apollo-247", PlatformCategory.PHARMACY, SellerSupport.PARTIAL, "https://www.apollo247.com"),
    # 8. Furniture & home
    _spec("Pepperfry", "pepperfry", PlatformCategory.FURNITURE, SellerSupport.FULL, "https://www.pepperfry.com"),
    _spec("Urban Ladder", "urban-ladder", PlatformCategory.FURNITURE, SellerSupport.FULL, "https://www.urbanladder.com"),
    # 9. B2B
    _spec("IndiaMART", "indiamart", PlatformCategory.B2B, SellerSupport.FULL, "https://seller.indiamart.com"),
    _spec("TradeIndia", "tradeindia", PlatformCategory.B2B, SellerSupport.FULL, "https://www.tradeindia.com"),
    _spec("Udaan", "udaan", PlatformCategory.B2B, SellerSupport.FULL, "https://udaan.com"),
    # 10. Brand-owned D2C (no third-party sellers — never compared)
    _spec("Apple Store India", "apple-store-india", PlatformCategory.D2C, SellerSupport.NONE, "https://www.apple.com/in"),
    _spec("Samsung Shop", "samsung-shop", PlatformCategory.D2C, SellerSupport.NONE, "https://www.samsung.com/in/shop"),
    _spec("Mi Store", "mi-store", PlatformCategory.D2C, SellerSupport.NONE, "https://www.mi.com/in"),
    _spec("OnePlus Store", "oneplus-store", PlatformCategory.D2C, SellerSupport.NONE, "https://www.oneplus.in"),
    _spec("Lenovo Store", "lenovo-store", PlatformCategory.D2C, SellerSupport.NONE, "https://www.lenovo.com/in"),
    _spec("Dell Store", "dell-store", PlatformCategory.D2C, SellerSupport.NONE, "https://www.dell.com/en-in"),
    _spec("HP Store", "hp-store", PlatformCategory.D2C, SellerSupport.NONE, "https://www.hp.com/in-en"),
    _spec("Nike India", "nike-india", PlatformCategory.D2C, SellerSupport.NONE, "https://www.nike.com/in"),
    _spec("Adidas India", "adidas-india", PlatformCategory.D2C, SellerSupport.NONE, "https://www.adidas.co.in"),
    _spec("Puma India", "puma-india", PlatformCategory.D2C, SellerSupport.NONE, "https://in.puma.com"),
)

#: Derived automatically — never hand-maintained.
PLATFORMS: tuple[str, ...] = tuple(spec.name for spec in PLATFORM_SPECS)


# --------------------------------------------------------------------------- #
# Row builders (DRY — one code path builds every platform's rows)
# --------------------------------------------------------------------------- #
def _fee_row(platform_name, category, profile, effective_from=CURRENT_FROM,
             effective_to=None) -> dict:
    return {
        "platform": platform_name,
        "category": category,
        "price_band_min": Decimal("0.00"),
        "price_band_max": None,
        "commission_pct": profile.commission_pct,
        "fixed_fee": profile.fixed_fee,
        "shipping_slab_weight_g": profile.shipping_slab_weight_g,
        "shipping_fee": profile.shipping_fee,
        "payment_gateway_pct": profile.payment_gateway_pct,
        "gst_pct": profile.gst_pct,
        "effective_from": effective_from,
        "effective_to": effective_to,
        "source_url": SOURCE_URL,
        "date_accessed": ACCESSED,
    }


def _rto_row(platform_name, category, profile) -> dict:
    return {
        "platform": platform_name,
        "category": category,
        "rto_rate_pct": profile.rto_rate_pct,
        "avg_rto_cost": profile.avg_rto_cost,
        "effective_from": CURRENT_FROM,
        "source_url": SOURCE_URL,
    }


def build_fee_rules() -> list[dict]:
    rows: list[dict] = []
    for spec in PLATFORM_SPECS:
        if not spec.seller_supported:
            continue  # D2C: metadata only, no seller fee rules
        if spec.slug in FEE_OVERRIDES:
            for category, profile in FEE_OVERRIDES[spec.slug].items():
                rows.append(_fee_row(spec.name, category, profile))
            for category, profile, eff_from, eff_to in HISTORICAL_FEES.get(spec.slug, []):
                rows.append(_fee_row(spec.name, category, profile, eff_from, eff_to))
        else:
            profile = CATEGORY_PROFILES[spec.category]
            for category in profile.product_categories:
                rows.append(_fee_row(spec.name, category, profile.fee))
    return rows


def build_rto_rates() -> list[dict]:
    rows: list[dict] = []
    for spec in PLATFORM_SPECS:
        if not spec.seller_supported:
            continue
        if spec.slug in RTO_OVERRIDES:
            for category, profile in RTO_OVERRIDES[spec.slug].items():
                rows.append(_rto_row(spec.name, category, profile))
        else:
            profile = CATEGORY_PROFILES[spec.category]
            for category in profile.product_categories:
                rows.append(_rto_row(spec.name, category, profile.rto))
    return rows
