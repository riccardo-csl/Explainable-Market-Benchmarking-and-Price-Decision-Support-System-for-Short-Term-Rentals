"""CLI runner for midterm EDA chart generation."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .eda_chart_generator import generate_midterm_eda_charts


def load_listing_snapshot(repo_root: Path) -> pd.DataFrame:
    """Load the canonical cleaned listing snapshot dataset."""

    listing_snapshot_path = repo_root / "data" / "processed" / "airbnb" / "csv" / "listing_snapshot.csv"
    if not listing_snapshot_path.exists():
        raise FileNotFoundError(
            "Expected cleaned listing snapshot dataset at "
            f"{listing_snapshot_path}. Run the cleaned dataset pipeline first."
        )
    return pd.read_csv(listing_snapshot_path)


def run_midterm_eda_chart_pipeline(
    repo_root: Path,
    output_root: Path | None = None,
    *,
    min_neighbourhood_rows: int = 200,
    top_n: int = 5,
    bottom_n: int = 5,
) -> list[Path]:
    """Generate the full EDA chart pack for the midterm slides."""

    resolved_repo_root = repo_root.resolve()
    resolved_output_root = resolved_repo_root if output_root is None else output_root.resolve()
    listing_snapshot = load_listing_snapshot(resolved_repo_root)
    return generate_midterm_eda_charts(
        listing_snapshot,
        resolved_output_root,
        min_neighbourhood_rows=min_neighbourhood_rows,
        top_n=top_n,
        bottom_n=bottom_n,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the full midterm EDA chart pack from the canonical cleaned dataset."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Path to the repository root that contains data/processed/airbnb/csv/listing_snapshot.csv.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Optional output root. Charts are written under modeling/reports/eda/midterm_charts/.",
    )
    parser.add_argument(
        "--min-neighbourhood-rows",
        type=int,
        default=200,
        help="Minimum number of listing snapshot rows required for the neighbourhood extremes chart.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top-priced neighbourhoods to keep in the extremes chart.",
    )
    parser.add_argument(
        "--bottom-n",
        type=int,
        default=5,
        help="Number of lower-priced neighbourhoods to keep in the extremes chart.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    written_paths = run_midterm_eda_chart_pipeline(
        repo_root=args.repo_root,
        output_root=args.output_root,
        min_neighbourhood_rows=args.min_neighbourhood_rows,
        top_n=args.top_n,
        bottom_n=args.bottom_n,
    )
    for path in written_paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
