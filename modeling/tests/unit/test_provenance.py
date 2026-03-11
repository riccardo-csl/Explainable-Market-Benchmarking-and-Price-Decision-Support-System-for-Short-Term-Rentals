from pathlib import Path

from data_foundation.provenance import build_raw_dataset_manifest, sha256_for_file
from data_foundation.source_registry import source_dataset_descriptors


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "source_dataset_samples"


def test_sha256_for_file_returns_stable_hash() -> None:
    target_file = FIXTURE_ROOT / "data" / "raw" / "airbnb" / "listing_snapshots.csv"

    first = sha256_for_file(target_file)
    second = sha256_for_file(target_file)

    assert first == second
    assert len(first) == 64


def test_build_raw_dataset_manifest_uses_canonical_path_and_metadata() -> None:
    descriptor = next(
        item for item in source_dataset_descriptors() if item.name == "airbnb_listing_snapshots"
    )

    manifest = build_raw_dataset_manifest(
        descriptor,
        FIXTURE_ROOT,
        import_date="2026-03-11",
    )

    assert manifest.canonical_path == "data/raw/airbnb/listing_snapshots.csv"
    assert manifest.original_filename == "airbnb.csv"
    assert manifest.source_category == "third_party_export"
    assert manifest.import_date == "2026-03-11"
    assert manifest.size_bytes > 0
