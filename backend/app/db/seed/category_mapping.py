"""Internal ↔ marketplace category mapping (documented, not silently assumed).

The 9 internal categories are broad; each marketplace charges by its own,
finer sub-categories. Where a broad internal category maps to several
marketplace sub-categories with different rates, the fee is represented as a
RANGE or marked NOT_PUBLICLY_VERIFIABLE — never collapsed to one fabricated
value. This table records the representative mapping and its uncertainty so the
assumption is auditable (README / DATA_SOURCES.md).
"""

INTERNAL_CATEGORIES: tuple[str, ...] = (
    "Home & Kitchen",
    "Electronics Accessories",
    "Books",
    "Clothing",
    "Beauty & Personal Care",
    "Toys",
    "Sports & Fitness",
    "Automotive Accessories",
    "Grocery",
)

# internal category -> {marketplace: (representative marketplace category, confidence note)}
CATEGORY_MAP: dict[str, dict[str, tuple[str, str]]] = {
    "Home & Kitchen": {
        "Amazon": ("Home/Kitchen small appliances & storage", "Spans subcategories with different rates → RANGE"),
        "Flipkart": ("Home & Kitchen", "Umbrella; per-category rate login-gated ≥₹1000"),
        "Meesho": ("Home & Kitchen", "0% commission regardless of category"),
    },
    "Electronics Accessories": {
        "Amazon": ("Headphones/earphones & accessories", "Representative 18% >₹1000; varies by accessory"),
        "Flipkart": ("Electronics accessories", "Per-category rate login-gated ≥₹1000"),
        "Meesho": ("Accessories", "0% commission"),
    },
    "Clothing": {
        "Amazon": ("Apparel", "Wide spread (baby 7% … shorts 24%) → RANGE"),
        "Flipkart": ("Apparel/Fashion", "Fashion 0% announced 2026; details login-gated"),
        "Meesho": ("Apparel", "0% commission"),
    },
    "Grocery": {
        "Amazon": ("Grocery — dry", "Spices 8% / dried fruits 9% → RANGE"),
        "Flipkart": ("Grocery", "Login-gated ≥₹1000"),
        "Meesho": ("Grocery/FMCG", "0% commission"),
    },
    # Categories not captured from the official Amazon fee page this cycle are
    # marked NOT_PUBLICLY_VERIFIABLE for Amazon ≥₹1000 in the seed rather than guessed.
    "Books": {"Amazon": ("Books", "≥₹1000 rate not captured this cycle → NOT_PUBLICLY_VERIFIABLE"),
              "Flipkart": ("Books", "Login-gated"), "Meesho": ("Books", "0% commission")},
    "Beauty & Personal Care": {"Amazon": ("Beauty", "Not captured this cycle → NOT_PUBLICLY_VERIFIABLE"),
                                "Flipkart": ("Beauty", "Login-gated"), "Meesho": ("Beauty", "0% commission")},
    "Toys": {"Amazon": ("Toys", "Not captured this cycle → NOT_PUBLICLY_VERIFIABLE"),
             "Flipkart": ("Toys", "Login-gated"), "Meesho": ("Toys", "0% commission")},
    "Sports & Fitness": {"Amazon": ("Sports", "Not captured this cycle → NOT_PUBLICLY_VERIFIABLE"),
                          "Flipkart": ("Sports", "Login-gated"), "Meesho": ("Sports", "0% commission")},
    "Automotive Accessories": {"Amazon": ("Automotive", "Not captured this cycle → NOT_PUBLICLY_VERIFIABLE"),
                                "Flipkart": ("Automotive", "Login-gated"), "Meesho": ("Automotive", "0% commission")},
}
