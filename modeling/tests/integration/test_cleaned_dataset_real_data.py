from pathlib import Path

import pandas as pd
import yaml

from data_foundation.cleaned_dataset_runner import run_cleaned_dataset_pipeline


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_real_data_generates_all_cleaned_outputs_and_manifests(tmp_path: Path) -> None:
    run_cleaned_dataset_pipeline(REPO_ROOT, tmp_path, generation_date="2026-03-11")

    parquet_root = tmp_path / "data" / "processed" / "airbnb" / "parquet"
    csv_root = tmp_path / "data" / "processed" / "airbnb" / "csv"
    manifest_root = tmp_path / "data" / "processed" / "airbnb" / "_manifests"

    expected_names = {
        "listing_snapshot",
        "city_period_summary",
        "neighbourhood_period_summary",
        "neighbourhood_reference",
        "neighbourhood_boundary",
    }
    for dataset_name in expected_names:
        assert (parquet_root / f"{dataset_name}.parquet").exists()
        assert (csv_root / f"{dataset_name}.csv").exists()
        assert (manifest_root / f"{dataset_name}.yaml").exists()

    listing_snapshot = pd.read_parquet(parquet_root / "listing_snapshot.parquet")
    assert len(listing_snapshot) == 282047

    city_period_summary = pd.read_parquet(parquet_root / "city_period_summary.parquet")
    assert len(city_period_summary) == 17

    neighbourhood_period_summary = pd.read_parquet(parquet_root / "neighbourhood_period_summary.parquet")
    assert len(neighbourhood_period_summary) == 655

    neighbourhood_boundary = pd.read_parquet(parquet_root / "neighbourhood_boundary.parquet")
    assert len(neighbourhood_boundary) == 710
    assert neighbourhood_boundary["city_name"].notna().all()

    manifest = yaml.safe_load((manifest_root / "neighbourhood_boundary.yaml").read_text(encoding="utf-8"))
    assert manifest["generation_date"] == "2026-03-11"
