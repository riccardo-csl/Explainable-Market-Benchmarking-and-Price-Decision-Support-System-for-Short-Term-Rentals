from pathlib import Path

import yaml

from data_foundation.dataset_inventory_runner import main, run_dataset_inventory


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "source_dataset_samples"


def test_dataset_inventory_runner_writes_registry_contracts_and_docs(tmp_path: Path) -> None:
    written_paths = run_dataset_inventory(FIXTURE_ROOT, tmp_path)

    registry_path = tmp_path / "shared" / "contracts" / "data" / "source_dataset_registry.yaml"
    contract_path = tmp_path / "shared" / "contracts" / "data" / "target_cleaned_datasets" / "listing_snapshot.yaml"
    inventory_path = tmp_path / "docs" / "data" / "source_dataset_inventory.md"
    contracts_doc_path = tmp_path / "docs" / "data" / "cleaned_data_contracts.md"

    assert registry_path in written_paths
    assert contract_path in written_paths
    assert inventory_path in written_paths
    assert contracts_doc_path in written_paths

    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    assert len(registry["source_datasets"]) == 5
    assert all(
        dataset["relative_path"].startswith("data/raw/airbnb/")
        for dataset in registry["source_datasets"]
    )

    listing_contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    assert listing_contract["name"] == "listing_snapshot"
    assert listing_contract["primary_key"] == ["listing_id", "snapshot_date"]

    inventory_doc = inventory_path.read_text(encoding="utf-8")
    assert "Source Dataset Inventory" in inventory_doc
    assert "airbnb_listing_snapshots" in inventory_doc
    assert "Dataset Relationships" in inventory_doc

    contracts_doc = contracts_doc_path.read_text(encoding="utf-8")
    assert "Cleaned Data Contracts" in contracts_doc
    assert "neighbourhood_boundary" in contracts_doc


def test_dataset_inventory_main_prints_written_paths(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "--repo-root",
            str(FIXTURE_ROOT),
            "--output-root",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "source_dataset_registry.yaml" in captured.out
