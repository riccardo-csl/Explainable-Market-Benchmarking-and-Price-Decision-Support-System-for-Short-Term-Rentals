from pathlib import Path

import yaml

from data_foundation.raw_data_catalog_runner import main, run_raw_data_catalog


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "source_dataset_samples"


def test_raw_data_catalog_runner_writes_manifests_and_docs(tmp_path: Path) -> None:
    written_paths = run_raw_data_catalog(
        FIXTURE_ROOT,
        tmp_path,
        import_date="2026-03-11",
    )

    manifest_path = tmp_path / "data" / "raw" / "_manifests" / "airbnb_listing_snapshots.yaml"
    registry_path = tmp_path / "shared" / "contracts" / "data" / "source_dataset_registry.yaml"

    assert manifest_path in written_paths
    assert registry_path in written_paths

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert manifest["canonical_path"] == "data/raw/airbnb/listing_snapshots.csv"
    assert manifest["import_date"] == "2026-03-11"
    assert manifest["sha256"]


def test_raw_data_catalog_main_prints_manifest_paths(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "--repo-root",
            str(FIXTURE_ROOT),
            "--output-root",
            str(tmp_path),
            "--import-date",
            "2026-03-11",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "data/raw/_manifests/airbnb_listing_snapshots.yaml" in captured.out
