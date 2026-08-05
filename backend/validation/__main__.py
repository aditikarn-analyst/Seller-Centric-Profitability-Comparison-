"""CLI: run the deviation report.

    python -m validation                       # uses validation/expected_skus.csv
    python -m validation path/to/expected.csv
"""

import sys
from pathlib import Path

from validation.validator import (
    build_in_memory_session,
    load_expected_csv,
    run_validation,
)

_DEFAULT = Path(__file__).parent / "expected_skus.csv"


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else _DEFAULT
    expected = load_expected_csv(path)

    session = build_in_memory_session()
    try:
        report = run_validation(expected, session)
    finally:
        session.close()

    print(f"Deviation report — {len(report.rows)} rows from {path.name}\n")
    print(f"{'Category':<22}{'Price':>9}{'Platform':>12}{'Computed':>11}{'Expected':>11}{'Dev':>9}")
    for r in report.rows:
        computed = "n/a" if r.computed_profit is None else f"{r.computed_profit}"
        dev = "n/a" if r.deviation is None else f"{r.deviation}"
        print(f"{r.category:<22}{r.selling_price:>9}{r.platform:>12}{computed:>11}{r.expected_profit:>11}{dev:>9}")

    print(
        f"\nCompared: {report.total_compared} | "
        f"within ±{report.tolerance}: {report.within_tolerance} | "
        f"max |dev|: {report.max_abs_deviation} | "
        f"mean |dev|: {report.mean_abs_deviation}"
    )
    print(
        "\nNOTE (O6): expected_skus.csv currently holds the §13.5 worked example as a "
        "self-consistency check. Replace/extend with >=25 real SKUs whose expected "
        "values come from Amazon/Flipkart official calculators for the C6 contribution."
    )


if __name__ == "__main__":
    main()
