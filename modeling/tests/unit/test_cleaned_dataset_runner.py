from pathlib import Path

import pandas as pd
import yaml

from data_foundation.cleaned_dataset_runner import main, run_cleaned_dataset_pipeline


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "source_dataset_samples"


def test_cleaned_dataset_runner_writes_processed_outputs_and_manifests(tmp_path: Path) -> None:
    written_paths = run_cleaned_dataset_pipeline(
        FIXTURE_ROOT,
        tmp_path,
        generation_date="2026-03-11",
    )

    parquet_path = tmp_path / "data" / "processed" / "airbnb" / "parquet" / "listing_snapshot.parquet"
    csv_path = tmp_path / "data" / "processed" / "airbnb" / "csv" / "listing_snapshot.csv"
    manifest_path = tmp_path / "data" / "processed" / "airbnb" / "_manifests" / "listing_snapshot.yaml"

    assert parquet_path in written_paths
    assert csv_path in written_paths
    assert manifest_path in written_paths

    dataframe = pd.read_parquet(parquet_path)
    assert list(dataframe.columns)[0] == "listing_id"
    assert len(dataframe) == 2

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert manifest["dataset_name"] == "listing_snapshot"
    assert manifest["generation_date"] == "2026-03-11"
    assert manifest["row_count"] == 2


def test_cleaned_dataset_main_prints_written_paths(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "--repo-root",
            str(FIXTURE_ROOT),
            "--output-root",
            str(tmp_path),
            "--generation-date",
            "2026-03-11",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "data/processed/airbnb/parquet/listing_snapshot.parquet" in captured.out
