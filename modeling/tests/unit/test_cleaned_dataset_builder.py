import json
from pathlib import Path

from data_foundation.cleaned_dataset_builder import build_cleaned_datasets
from data_foundation.raw_dataset_loader import load_raw_datasets
from data_foundation.source_registry import source_dataset_descriptors, target_dataset_contracts


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "source_dataset_samples"


def test_build_cleaned_datasets_matches_contract_columns_and_parses_coordinates() -> None:
    raw_datasets = load_raw_datasets(source_dataset_descriptors(), FIXTURE_ROOT)
    cleaned_datasets = build_cleaned_datasets(raw_datasets, target_dataset_contracts())

    listing_snapshot = cleaned_datasets["listing_snapshot"]
    assert "latitude" in listing_snapshot.columns
    assert "longitude" in listing_snapshot.columns
    assert float(listing_snapshot.loc[0, "latitude"]) == 43.77
    assert bool(listing_snapshot.loc[0, "is_superhost"]) is True

    neighbourhood_boundary = cleaned_datasets["neighbourhood_boundary"]
    assert neighbourhood_boundary["boundary_id"].tolist() == [
        "firenze_centro_storico_centro_storico_001",
        "firenze_duomo_centro_storico_001",
    ]
    geometry_payload = json.loads(neighbourhood_boundary.loc[0, "geometry"])
    assert geometry_payload["type"] == "MultiPolygon"
    assert neighbourhood_boundary["city_name"].tolist() == ["Firenze", "Firenze"]
