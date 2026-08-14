# Marketplace Fee Data — Sources & Provenance

**Dataset version:** `2026.08` · **Data collection date:** 2026-08-09 · **Last verified:** 2026-08-09

> This is a **manually source-verified** dataset, **not** a live marketplace fee feed.
> Marketplace fees change; verify current seller fee schedules before commercial
> decisions. Every production fee value below carries its own source and confidence.

## Confidence & source-type legend

| Verification status | Meaning |
|---|---|
| `VERIFIED` | The cited source states this **exact** value. |
| `PARTIALLY_VERIFIED` | The source gives a **range/condition** (or a general policy), not a single exact figure for this exact context. Stored as a range or with conditions — never a fabricated exact number. |
| `NOT_PUBLICLY_VERIFIABLE` | The fee exists but its value is **not publicly disclosed**. Stored as `NOT_VERIFIABLE` with no invented number. |
| `ASSUMED` | A documented modelling assumption (e.g. RTO). |

| Source type | Meaning |
|---|---|
| `OFFICIAL` | The marketplace's own published page, **or a statutory source** (GST). |
| `SECONDARY` | A credible third party, cited (never presented as official). |
| `USER_ASSUMPTION` | Supplied/assumed by the seller or maintainer. |
| `ILLUSTRATIVE` | Placeholder — **never** used for a research result. |

## Provenance table (production `fee_components`)

### Amazon India — source: [sell.amazon.in/fees-and-pricing](https://sell.amazon.in/fees-and-pricing) (OFFICIAL, fetched 2026-08-09)

| Component | Category / band | Value | Kind | Status | Notes |
|---|---|---|---|---|---|
| Commission | Home & Kitchen, Electronics Accessories, Clothing, Grocery · ≤ ₹1000 | 0% | PERCENT | **VERIFIED** | category-confirmed on the fee page |
| Commission | Books, Beauty, Toys, Sports, Automotive · ≤ ₹1000 | 0% | PERCENT | **PARTIALLY_VERIFIED** | inferred from general "1800+ categories" policy, not category-confirmed (audit I2) |
| Commission | Home & Kitchen · > ₹1000 | 4.5%–8% | RANGE | PARTIALLY_VERIFIED | small appliances 4.5–8%; refrigerators 5% |
| Commission | Clothing · > ₹1000 | 7%–24% | RANGE | PARTIALLY_VERIFIED | baby 7% … shorts 24% |
| Commission | Grocery · > ₹1000 | 8%–9% | RANGE | PARTIALLY_VERIFIED | spices 8% / dried fruits 9% |
| Commission | Electronics Accessories · > ₹1000 | — | NOT_VERIFIABLE | **NOT_PUBLICLY_VERIFIABLE** | 18% is *headphones* only; umbrella not generalized (audit I4) |
| Commission | Books, Beauty, Toys, Sports, Automotive · > ₹1000 | — | NOT_VERIFIABLE | NOT_PUBLICLY_VERIFIABLE | not captured from official page this cycle |
| Fixed/closing | all | ≥ ₹1 (open) | RANGE | PARTIALLY_VERIFIED | "starts at ₹1"; no published max |
| Shipping | all | ≥ ₹37 (open) | RANGE | PARTIALLY_VERIFIED | "starts at ₹37"; volume/distance-dependent |
| Payment | all | — | NOT_VERIFIABLE | **NOT_PUBLICLY_VERIFIABLE** | no separate fee stated; absence ≠ 0 (audit I5) |

### Meesho — source: [supplier.meesho.com/pricing](https://supplier.meesho.com/pricing) (SECONDARY)

| Component | Value | Kind | Status | Notes |
|---|---|---|---|---|
| Commission | 0% | PERCENT | **VERIFIED** (SECONDARY) | 0% since Aug 2022. Official page returned 403 to automated fetch; corroborated by secondary sources (audit I3) |
| Payment | 0% | PERCENT | VERIFIED (SECONDARY) | no PG/COD charge |
| Fixed fee | ₹25–30 | RANGE | PARTIALLY_VERIFIED | secondary guides |
| Shipping | ₹27–120 | RANGE | PARTIALLY_VERIFIED | weight/zone-dependent |

### Flipkart — source: [seller.flipkart.com](https://seller.flipkart.com) + guides (SECONDARY; rate card login-gated)

| Component | Band | Value | Kind | Status | Notes |
|---|---|---|---|---|---|
| Commission | < ₹1000 | 0% | PERCENT | PARTIALLY_VERIFIED | eligible sellers, from 14 Nov 2025 |
| Commission | ≥ ₹1000 | — | NOT_VERIFIABLE | **NOT_PUBLICLY_VERIFIABLE** | per-category rate behind Seller Hub login |
| Payment (collection) | all | ~2% | PERCENT | PARTIALLY_VERIFIED | ~2% of order value |
| Fixed fee | all | ₹8–35 | RANGE | PARTIALLY_VERIFIED | by price/tier |
| Shipping | all | ₹0 … (open) | RANGE | PARTIALLY_VERIFIED | free most <500g; weight/zone otherwise |

### GST (all marketplaces) — source: [CGST Act, 2017 / CBIC](https://cbic-gst.gov.in/) (OFFICIAL, statutory)

| Component | Value | Kind | Status | Notes |
|---|---|---|---|---|
| GST | 18% | PERCENT | VERIFIED | **Statutory** tax on the marketplace fee base — *calculated*, not a marketplace-specific fee (audit I1) |

## Separation of data kinds

- **Source-derived (production):** all `OFFICIAL`/`SECONDARY` rows above.
- **Calculated:** GST (18% of the marketplace fee base, statutory).
- **Assumptions:** RTO — **excluded by default**; a documented modelling assumption, never a marketplace fee, no RTO amounts seeded.
- **Could not be verified:** Amazon per-category commission > ₹1000 for Electronics Accessories/Books/Beauty/Toys/Sports/Automotive; Amazon payment fee; Flipkart per-category commission ≥ ₹1000. Stored as `NOT_VERIFIABLE` → these **exclude** the marketplace from the definitive winner ranking.

## Known limitations

1. Marketplace fees are revised frequently; re-verify each cycle and bump `FEE_DATASET_VERSION`.
2. Meesho's official pricing page blocks automated fetch (403) → commission value is SECONDARY-corroborated.
3. Flipkart's ≥ ₹1000 per-category commission is login-gated → not publicly verifiable.
4. Amazon fee page publishes closing/shipping as open-ended ("starts at ₹X") → a bounded worst-case profit is not computable from public data.
5. With current public data, **Meesho is frequently the only definitive candidate** — a data-availability outcome, transparently reported, not a bias.
