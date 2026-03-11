from pathlib import Path

import yaml

from data_foundation.raw_data_catalog_runner import run_raw_data_catalog


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_real_datasets_generate_expected_registry(tmp_path: Path) -> None:
    run_raw_data_catalog(REPO_ROOT, tmp_path, import_date="2026-03-11")

    registry_path = tmp_path / "shared" / "contracts" / "data" / "source_dataset_registry.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    datasets = {item["name"]: item for item in registry["source_datasets"]}

    assert len(datasets) == 5
    assert all(
        item["relative_path"].startswith("data/raw/airbnb/")
        for item in datasets.values()
    )

    listings = datasets["airbnb_listing_snapshots"]["observed_profile"]
    assert listings["row_count"] > 200000
    assert listings["coverage"]["cities"] == ["Firenze", "Milano", "Napoli", "Roma", "Venezia"]
    assert listings["coverage"]["periods"] == ["Early Autumn", "Early Spring", "Early Summer", "Early Winter"]
    assert listings["coverage"]["snapshot_dates"] == ["2024-03-15", "2024-06-15", "2024-09-15", "2024-12-15"]
    assert any(
        key_result["columns"] == ["Listings id", "Date of scraping"] and key_result["is_unique"]
        for key_result in listings["candidate_keys"]
    )

    city_summary = datasets["city_period_summary"]["observed_profile"]
    assert city_summary["row_count"] == 17
    assert any(
        key_result["columns"] == ["place", "period"] and key_result["is_unique"]
        for key_result in city_summary["candidate_keys"]
    )

    boundaries = datasets["neighbourhood_boundaries"]["observed_profile"]
    assert boundaries["feature_count"] == 710
    assert boundaries["geometry_types"] == ["MultiPolygon"]

    manifest_path = tmp_path / "data" / "raw" / "_manifests" / "airbnb_listing_snapshots.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert manifest["canonical_path"] == "data/raw/airbnb/listing_snapshots.csv"
    assert manifest["import_date"] == "2026-03-11"
