from pathlib import Path

from data_foundation.inspector import inspect_dataset
from data_foundation.source_registry import source_dataset_descriptors


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "source_dataset_samples"


def test_csv_inspection_extracts_coverage_and_candidate_keys() -> None:
    spec = next(
        descriptor
        for descriptor in source_dataset_descriptors()
        if descriptor.name == "airbnb_listing_snapshots"
    )

    profile = inspect_dataset(spec, FIXTURE_ROOT)

    assert profile.row_count == 2
    assert profile.coverage["cities"] == ["Firenze"]
    assert profile.coverage["periods"] == ["Early Spring", "Early Summer"]
    assert profile.coverage["snapshot_dates"] == ["2024-03-15", "2024-06-15"]
    assert any(result.columns == ["Listings id", "Date of scraping"] and result.is_unique for result in profile.candidate_keys)


def test_geojson_inspection_extracts_geometry_information() -> None:
    spec = next(
        descriptor
        for descriptor in source_dataset_descriptors()
        if descriptor.name == "neighbourhood_boundaries"
    )

    profile = inspect_dataset(spec, FIXTURE_ROOT)

    assert profile.feature_count == 2
    assert profile.geometry_types == ["MultiPolygon"]
    field_names = {field.name for field in profile.fields}
    assert {"neighbourhood", "neighbourhood_group"} <= field_names
