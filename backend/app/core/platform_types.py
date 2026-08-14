"""Platform & product taxonomy — the typed vocabulary of the whole system.

Every categorical value the application reasons about is defined here as an
enum, so magic strings never appear in business logic. A mistyped category,
support level, verification status, or data source is caught at import/type-check
time rather than surfacing as a silent runtime bug.

Research rationale:
* Maintainability — one authoritative vocabulary; renames are mechanical and safe.
* Reproducibility — stored values map to a fixed, documented set of members.
* Extensibility — a new platform type / product category / data source is a
  one-line enum addition, with no scattered string literals to update.
"""

from enum import Enum


class PlatformCategory(str, Enum):
    """The business domain / model a platform operates in.

    Independent of seller eligibility: a platform's domain (e.g. ELECTRONICS)
    is separate from whether it onboards third-party sellers. See SellerSupport.
    """

    MARKETPLACE = "Marketplace"        # general multi-vendor
    FASHION = "Fashion"
    BEAUTY = "Beauty"
    ELECTRONICS = "Electronics"
    GROCERY = "Grocery"
    QUICK_COMMERCE = "Quick Commerce"
    PHARMACY = "Pharmacy"
    FURNITURE = "Furniture"
    B2B = "B2B"
    D2C = "D2C"                        # brand-owned single-brand store


class SellerSupport(str, Enum):
    """Degree to which a platform onboards third-party sellers.

    This — not the platform's domain — determines comparison eligibility. An
    own-retail chain (e.g. Croma) keeps its ELECTRONICS domain but is NONE here.
    """

    FULL = "FULL"           # open marketplace, self-serve onboarding
    PARTIAL = "PARTIAL"     # curated / brand-approval / hybrid onboarding
    LIMITED = "LIMITED"     # closed brand-supply (e.g. quick-commerce dark stores)
    NONE = "NONE"           # no third-party onboarding (own-retail / D2C)

    @property
    def participates(self) -> bool:
        """True if a platform at this level may appear in comparisons.

        Only NONE is excluded; FULL/PARTIAL/LIMITED all onboard sellers to some
        degree. Keeping the full level (rather than a bare boolean) preserves
        business information for future analytics.
        """
        return self is not SellerSupport.NONE


class ProductCategory(str, Enum):
    """Centralized product-category registry — the single source of truth.

    ``fee_rules.category`` stays a validated String column, but every value it
    may hold is defined here, and the catalog API exposes this registry so the
    frontend never hardcodes dropdown values.
    """

    ELECTRONICS = "Electronics"
    MOBILES = "Mobiles"
    LAPTOPS = "Laptops"
    ACCESSORIES = "Accessories"
    HOME_APPLIANCES = "Home Appliances"
    HOME_KITCHEN = "Home & Kitchen"
    GROCERY = "Grocery"
    FMCG = "FMCG"
    CLOTHING = "Clothing"
    FASHION = "Fashion"
    FOOTWEAR = "Footwear"
    BEAUTY = "Beauty"
    PERSONAL_CARE = "Personal Care"
    BOOKS = "Books"
    TOYS = "Toys"
    SPORTS = "Sports"
    AUTOMOTIVE = "Automotive"
    FURNITURE = "Furniture"
    JEWELLERY = "Jewellery"
    PET_SUPPLIES = "Pet Supplies"
    OFFICE_SUPPLIES = "Office Supplies"
    BABY_PRODUCTS = "Baby Products"
    HEALTH = "Health"
    PHARMACY = "Pharmacy"

    @classmethod
    def values(cls) -> tuple[str, ...]:
        return tuple(member.value for member in cls)


class VerificationStatus(str, Enum):
    """How well a fee value is backed by its cited source.

    Research-integrity requirement: a value is only VERIFIED when the source
    states it exactly. A published range (e.g. "2%–38%") is at most
    PARTIALLY_VERIFIED, never an invented exact figure marked VERIFIED.
    """

    VERIFIED = "VERIFIED"                        # source states this exact value
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"    # source gives a range/condition, not an exact figure
    ASSUMED = "ASSUMED"                          # a documented assumption was necessary
    NOT_PUBLICLY_VERIFIABLE = "NOT_PUBLICLY_VERIFIABLE"  # value not publicly disclosed


class SourceType(str, Enum):
    """Origin of a fee value's numbers."""

    OFFICIAL = "OFFICIAL"                # marketplace's own published fee page/doc
    SECONDARY = "SECONDARY"             # credible third-party, cited (not official)
    USER_ASSUMPTION = "USER_ASSUMPTION"  # supplied/assumed by the seller or admin
    ILLUSTRATIVE = "ILLUSTRATIVE"        # placeholder — not real platform data


class FulfillmentType(str, Enum):
    """Fulfilment model a fee rule applies to (advanced input).

    ``None`` on a rule means it applies regardless of fulfilment model.
    """

    SELF_SHIP = "SELF_SHIP"                  # seller ships (e.g. Easy Ship / self)
    PLATFORM_FULFILLED = "PLATFORM_FULFILLED"  # marketplace warehouse/fulfilment


class ComponentType(str, Enum):
    """One line of a marketplace's fee stack (normalized fee_components)."""

    COMMISSION = "COMMISSION"
    FIXED_FEE = "FIXED_FEE"
    SHIPPING = "SHIPPING"
    PAYMENT = "PAYMENT"
    GST = "GST"           # statutory tax, kept separate from marketplace fees
    RTO = "RTO"           # modelled return cost, not a marketplace-published fee
    OTHER = "OTHER"


class ValueKind(str, Enum):
    """How a component's numeric value is expressed.

    Distinguishes a known 0 (e.g. PERCENT 0 = "0% commission") from an unknown
    value (NOT_VERIFIABLE) — these must never be conflated (research integrity).
    """

    EXACT = "EXACT"                    # a single fixed amount (with unit)
    PERCENT = "PERCENT"                # an exact percentage of selling price
    RANGE = "RANGE"                    # a min/max band (value_min..value_max)
    NOT_VERIFIABLE = "NOT_VERIFIABLE"  # value not publicly disclosed / unknown


class Unit(str, Enum):
    """Unit for a component value."""

    PCT = "PCT"   # percentage of selling price
    INR = "INR"   # absolute rupees


#: Convenience tuple of product-category display values (derived, not duplicated).
PRODUCT_CATEGORIES: tuple[str, ...] = ProductCategory.values()
