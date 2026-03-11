from pathlib import Path

import pandas as pd

from data_foundation.cleaned_dataset_validation import (
    _validate_contract_columns,
    _validate_listing_snapshot_semantics,
    _validate_non_nullable_fields,
    _validate_primary_key_uniqueness,
)
from data_foundation.source_registry import target_dataset_contracts


def _contract_by_name(name: str):
    return next(contract for contract in target_dataset_contracts() if contract.name == name)


def test_contract_column_validation_detects_missing_required_columns() -> None:
    contract = _contract_by_name("listing_snapshot")
    dataframe = pd.DataFrame(columns=["listing_id", "snapshot_date"])

    findings = _validate_contract_columns(contract, dataframe)

    assert any(finding.check_name == "missing_contract_columns" for finding in findings)


def test_primary_key_uniqueness_validation_detects_duplicates() -> None:
    contract = _contract_by_name("listing_snapshot")
    dataframe = pd.DataFrame(
        [
            {"listing_id": 1, "snapshot_date": "2024-03-15"},
            {"listing_id": 1, "snapshot_date": "2024-03-15"},
        ]
    )

    findings = _validate_primary_key_uniqueness(contract, dataframe)

    assert len(findings) == 1
    assert findings[0].check_name == "primary_key_uniqueness"


def test_non_nullable_validation_detects_nulls() -> None:
    contract = _contract_by_name("listing_snapshot")
    dataframe = pd.DataFrame(
        [
            {
                "listing_id": 1,
                "snapshot_date": "2024-03-15",
                "city_name": None,
                "period_label": "Early Spring",
            }
        ]
    )

    findings = _validate_non_nullable_fields(contract, dataframe)

    assert any("city_name" in finding.message for finding in findings)


def test_listing_snapshot_semantics_detect_invalid_city_period_price_and_coordinates() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "city_name": "Torino",
                "period_label": "Spring",
                "nightly_price": 0,
                "latitude": 200.0,
                "longitude": 10.0,
                "rating_score": 6.0,
            }
        ]
    )

    findings = _validate_listing_snapshot_semantics(dataframe)
    check_names = {finding.check_name for finding in findings}

    assert "canonical_city_labels" in check_names
    assert "canonical_period_labels" in check_names
    assert "positive_nightly_price" in check_names
    assert "coordinate_bounds" in check_names
    assert "rating_bounds" in check_names
