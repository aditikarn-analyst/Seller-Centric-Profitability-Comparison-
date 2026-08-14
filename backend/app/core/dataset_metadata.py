"""Fee-dataset version metadata (README Step 13 — research reproducibility).

This is a *manually source-verified* dataset, NOT a real-time marketplace feed.
The version and dates below identify exactly which snapshot of fee data a
comparison was computed against, so a result is reproducible and auditable.
"""

from datetime import date

#: Human-readable dataset version (YYYY.MM of the collection cycle).
FEE_DATASET_VERSION: str = "2026.08"

#: When this dataset's values were collected from their sources.
DATA_COLLECTION_DATE: date = date(2026, 8, 9)

#: When this dataset's values were last verified against their sources.
LAST_VERIFICATION_DATE: date = date(2026, 8, 9)

#: Standing disclaimer surfaced in the API/UI/README. Marketplace fees change;
#: this is manually verified data, never a live feed.
DATA_DISCLAIMER: str = (
    "Marketplace fees are subject to change. This system uses manually "
    "source-verified fee data and does not represent a live marketplace fee "
    "feed. Verify current seller fee schedules before commercial decisions."
)


def dataset_metadata() -> dict[str, str]:
    """Serializable dataset-provenance block (for the API / UI)."""
    return {
        "fee_dataset_version": FEE_DATASET_VERSION,
        "data_collection_date": DATA_COLLECTION_DATE.isoformat(),
        "last_verification_date": LAST_VERIFICATION_DATE.isoformat(),
        "disclaimer": DATA_DISCLAIMER,
    }
