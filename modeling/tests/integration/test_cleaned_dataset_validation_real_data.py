from pathlib import Path

import pandas as pd
import yaml

from data_foundation.cleaned_dataset_runner import run_cleaned_dataset_pipeline
from data_foundation.cleaned_dataset_validation_runner import run_cleaned_dataset_validation


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "source_dataset_samples"


def test_real_cleaned_datasets_pass_minimal_validation(tmp_path: Path) -> None:
    run_cleaned_dataset_pipeline(REPO_ROOT, tmp_path, generation_date="2026-03-11")

    written_paths, overall_status = run_cleaned_dataset_validation(
        REPO_ROOT,
        tmp_path,
        validation_date="2026-03-11",
    )

    assert overall_status == "passed"
    assert tmp_path / "data" / "processed" / "airbnb" / "_quality" / "validation_report.yaml" in written_paths

    report = yaml.safe_load(
        (tmp_path / "data" / "processed" / "airbnb" / "_quality" / "validation_report.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert report["overall_status"] == "passed"
    assert not report["findings"]


def test_validation_fails_when_primary_key_is_duplicated(tmp_path: Path) -> None:
    run_cleaned_dataset_pipeline(FIXTURE_ROOT, tmp_path, generation_date="2026-03-11")

    parquet_path = tmp_path / "data" / "processed" / "airbnb" / "parquet" / "listing_snapshot.parquet"
    csv_path = tmp_path / "data" / "processed" / "airbnb" / "csv" / "listing_snapshot.csv"
    manifest_path = tmp_path / "data" / "processed" / "airbnb" / "_manifests" / "listing_snapshot.yaml"

    dataframe = pd.read_parquet(parquet_path)
    dataframe = pd.concat([dataframe, dataframe.iloc[[0]]], ignore_index=True)
    dataframe.to_parquet(parquet_path, index=False)
    dataframe.to_csv(csv_path, index=False)

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["row_count"] = len(dataframe)
    manifest["columns"] = list(dataframe.columns)
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")

    _, overall_status = run_cleaned_dataset_validation(
        FIXTURE_ROOT,
        tmp_path,
        validation_date="2026-03-11",
    )

    report = yaml.safe_load(
        (tmp_path / "data" / "processed" / "airbnb" / "_quality" / "validation_report.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert overall_status == "failed"
    assert any(finding["check_name"] == "primary_key_uniqueness" for finding in report["findings"])


def test_validation_fails_when_required_column_is_missing(tmp_path: Path) -> None:
    run_cleaned_dataset_pipeline(FIXTURE_ROOT, tmp_path, generation_date="2026-03-11")

    parquet_path = tmp_path / "data" / "processed" / "airbnb" / "parquet" / "listing_snapshot.parquet"
    csv_path = tmp_path / "data" / "processed" / "airbnb" / "csv" / "listing_snapshot.csv"
    manifest_path = tmp_path / "data" / "processed" / "airbnb" / "_manifests" / "listing_snapshot.yaml"

    dataframe = pd.read_parquet(parquet_path).drop(columns=["city_name"])
    dataframe.to_parquet(parquet_path, index=False)
    dataframe.to_csv(csv_path, index=False)

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["row_count"] = len(dataframe)
    manifest["columns"] = list(dataframe.columns)
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")

    _, overall_status = run_cleaned_dataset_validation(
        FIXTURE_ROOT,
        tmp_path,
        validation_date="2026-03-11",
    )

    report = yaml.safe_load(
        (tmp_path / "data" / "processed" / "airbnb" / "_quality" / "validation_report.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert overall_status == "failed"
    assert any(finding["check_name"] == "missing_contract_columns" for finding in report["findings"])
