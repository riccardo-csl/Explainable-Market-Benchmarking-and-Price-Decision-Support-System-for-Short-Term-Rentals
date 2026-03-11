"""Minimal validation for cleaned processed datasets."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from .contracts import TargetDatasetContract
from .source_registry import target_dataset_contracts

CANONICAL_CITIES = {"Firenze", "Milano", "Napoli", "Roma", "Venezia"}
CANONICAL_PERIODS = {"Early Spring", "Early Summer", "Early Autumn", "Early Winter"}
BOUNDARY_GEOMETRY_TYPES = {"Polygon", "MultiPolygon"}


@dataclass(frozen=True)
class ValidationFinding:
    dataset_name: str
    check_name: str
    severity: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DatasetValidationResult:
    dataset_name: str
    status: str
    row_count: int | None
    checks_run: list[str]
    findings: list[ValidationFinding] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["findings"] = [finding.to_dict() for finding in self.findings]
        return payload


@dataclass(frozen=True)
class ValidationReport:
    validation_date: str
    overall_status: str
    dataset_results: list[DatasetValidationResult]
    findings: list[ValidationFinding]

    def to_dict(self) -> dict[str, Any]:
        return {
            "validation_date": self.validation_date,
            "overall_status": self.overall_status,
            "dataset_results": [result.to_dict() for result in self.dataset_results],
            "findings": [finding.to_dict() for finding in self.findings],
        }


def validate_cleaned_datasets(
    output_root: Path,
    validation_date: str | None = None,
) -> ValidationReport:
    resolved_output_root = output_root.resolve()
    resolved_validation_date = validation_date or date.today().isoformat()
    contracts = target_dataset_contracts()

    dataset_results: list[DatasetValidationResult] = []
    all_findings: list[ValidationFinding] = []
    loaded_frames: dict[str, pd.DataFrame] = {}

    for contract in contracts:
        result, dataframe = _validate_single_dataset(contract, resolved_output_root)
        dataset_results.append(result)
        all_findings.extend(result.findings)
        if dataframe is not None:
            loaded_frames[contract.name] = dataframe

    cross_dataset_findings = _validate_cross_dataset_consistency(loaded_frames)
    all_findings.extend(cross_dataset_findings)

    result_map = {result.dataset_name: result for result in dataset_results}
    for finding in cross_dataset_findings:
        result = result_map.get(finding.dataset_name)
        if result is None:
            continue
        result.findings.append(finding)

    dataset_results = [
        DatasetValidationResult(
            dataset_name=result.dataset_name,
            status="failed" if result.findings else "passed",
            row_count=result.row_count,
            checks_run=result.checks_run,
            findings=result.findings,
        )
        for result in dataset_results
    ]

    overall_status = "failed" if all_findings else "passed"
    return ValidationReport(
        validation_date=resolved_validation_date,
        overall_status=overall_status,
        dataset_results=dataset_results,
        findings=all_findings,
    )


def render_validation_summary_markdown(report: ValidationReport) -> str:
    lines = [
        "# Cleaned Dataset Validation Summary",
        "",
        f"- Validation date: `{report.validation_date}`",
        f"- Overall status: `{report.overall_status}`",
        "",
        "## Dataset Status",
        "",
        "| Dataset | Status | Rows | Checks | Findings |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in report.dataset_results:
        lines.append(
            f"| {result.dataset_name} | {result.status} | {result.row_count or 0} | "
            f"{', '.join(result.checks_run)} | {len(result.findings)} |"
        )

    lines.append("")
    if not report.findings:
        lines.extend(
            [
                "## Findings",
                "",
                "No validation failures were detected.",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(["## Findings", ""])
    for result in report.dataset_results:
        if not result.findings:
            continue
        lines.extend([f"### {result.dataset_name}", ""])
        for finding in result.findings:
            lines.append(f"- `{finding.check_name}`: {finding.message}")
        lines.append("")
    return "\n".join(lines)


def _validate_single_dataset(
    contract: TargetDatasetContract,
    output_root: Path,
) -> tuple[DatasetValidationResult, pd.DataFrame | None]:
    parquet_path = output_root / "data" / "processed" / "airbnb" / "parquet" / f"{contract.name}.parquet"
    csv_path = output_root / "data" / "processed" / "airbnb" / "csv" / f"{contract.name}.csv"
    manifest_path = output_root / "data" / "processed" / "airbnb" / "_manifests" / f"{contract.name}.yaml"

    checks_run = [
        "dataset_files_exist",
        "manifest_exists",
        "contract_columns_match",
        "non_nullable_fields",
        "primary_key_uniqueness",
        "dataset_semantics",
    ]
    findings: list[ValidationFinding] = []

    missing_paths = [path for path in [parquet_path, csv_path, manifest_path] if not path.exists()]
    if missing_paths:
        findings.append(
            ValidationFinding(
                dataset_name=contract.name,
                check_name="dataset_files_exist",
                severity="error",
                message=f"Missing expected processed artifacts: {', '.join(str(path) for path in missing_paths)}",
            )
        )
        return DatasetValidationResult(contract.name, "failed", None, checks_run, findings), None

    dataframe = pd.read_parquet(parquet_path)
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    findings.extend(_validate_manifest(contract, dataframe, manifest))
    findings.extend(_validate_contract_columns(contract, dataframe))
    findings.extend(_validate_non_nullable_fields(contract, dataframe))
    findings.extend(_validate_primary_key_uniqueness(contract, dataframe))
    findings.extend(_validate_dataset_semantics(contract.name, dataframe))

    status = "failed" if findings else "passed"
    return DatasetValidationResult(contract.name, status, len(dataframe), checks_run, findings), dataframe


def _validate_manifest(
    contract: TargetDatasetContract,
    dataframe: pd.DataFrame,
    manifest: dict[str, Any],
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    if manifest.get("dataset_name") != contract.name:
        findings.append(
            ValidationFinding(
                contract.name,
                "manifest_dataset_name",
                "error",
                f"Manifest dataset_name is `{manifest.get('dataset_name')}` instead of `{contract.name}`.",
            )
        )
    if manifest.get("row_count") != len(dataframe):
        findings.append(
            ValidationFinding(
                contract.name,
                "manifest_row_count",
                "error",
                f"Manifest row_count is `{manifest.get('row_count')}` but dataset has `{len(dataframe)}` rows.",
            )
        )
    if manifest.get("columns") != list(dataframe.columns):
        findings.append(
            ValidationFinding(
                contract.name,
                "manifest_columns",
                "error",
                "Manifest column list does not match the actual dataset columns.",
            )
        )
    return findings


def _validate_contract_columns(
    contract: TargetDatasetContract,
    dataframe: pd.DataFrame,
) -> list[ValidationFinding]:
    expected_columns = [field.name for field in contract.fields]
    actual_columns = list(dataframe.columns)
    if actual_columns == expected_columns:
        return []

    findings: list[ValidationFinding] = []
    missing_columns = [column for column in expected_columns if column not in actual_columns]
    unexpected_columns = [column for column in actual_columns if column not in expected_columns]
    if missing_columns:
        findings.append(
            ValidationFinding(
                contract.name,
                "missing_contract_columns",
                "error",
                f"Missing required columns: {', '.join(missing_columns)}.",
            )
        )
    if unexpected_columns:
        findings.append(
            ValidationFinding(
                contract.name,
                "unexpected_columns",
                "error",
                f"Unexpected columns present: {', '.join(unexpected_columns)}.",
            )
        )
    if not missing_columns and not unexpected_columns and actual_columns != expected_columns:
        findings.append(
            ValidationFinding(
                contract.name,
                "column_order",
                "error",
                "Columns do not match the contract order.",
            )
        )
    return findings


def _validate_non_nullable_fields(
    contract: TargetDatasetContract,
    dataframe: pd.DataFrame,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    for field in contract.fields:
        if field.nullable or field.name not in dataframe.columns:
            continue
        null_count = int(dataframe[field.name].isna().sum())
        if null_count > 0:
            findings.append(
                ValidationFinding(
                    contract.name,
                    "non_nullable_fields",
                    "error",
                    f"Field `{field.name}` contains `{null_count}` null values but is non-nullable.",
                )
            )
    return findings


def _validate_primary_key_uniqueness(
    contract: TargetDatasetContract,
    dataframe: pd.DataFrame,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    missing_pk_columns = [column for column in contract.primary_key if column not in dataframe.columns]
    if missing_pk_columns:
        findings.append(
            ValidationFinding(
                contract.name,
                "primary_key_columns",
                "error",
                f"Primary key columns missing from dataset: {', '.join(missing_pk_columns)}.",
            )
        )
        return findings

    duplicate_count = int(dataframe.duplicated(contract.primary_key).sum())
    if duplicate_count > 0:
        findings.append(
            ValidationFinding(
                contract.name,
                "primary_key_uniqueness",
                "error",
                f"Primary key `{', '.join(contract.primary_key)}` contains `{duplicate_count}` duplicate rows.",
            )
        )
    return findings


def _validate_dataset_semantics(dataset_name: str, dataframe: pd.DataFrame) -> list[ValidationFinding]:
    if dataset_name == "listing_snapshot":
        return _validate_listing_snapshot_semantics(dataframe)
    if dataset_name in {"city_period_summary", "neighbourhood_period_summary"}:
        return _validate_grouped_semantics(dataset_name, dataframe)
    if dataset_name == "neighbourhood_boundary":
        return _validate_boundary_semantics(dataframe)
    return []


def _validate_listing_snapshot_semantics(dataframe: pd.DataFrame) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    required_columns = {
        "city_name",
        "period_label",
        "nightly_price",
        "latitude",
        "longitude",
        "rating_score",
    }
    if not required_columns.issubset(dataframe.columns):
        return findings

    invalid_cities = sorted(set(dataframe["city_name"].dropna()) - CANONICAL_CITIES)
    if invalid_cities:
        findings.append(
            ValidationFinding(
                "listing_snapshot",
                "canonical_city_labels",
                "error",
                f"Unexpected city labels found: {', '.join(invalid_cities)}.",
            )
        )

    invalid_periods = sorted(set(dataframe["period_label"].dropna()) - CANONICAL_PERIODS)
    if invalid_periods:
        findings.append(
            ValidationFinding(
                "listing_snapshot",
                "canonical_period_labels",
                "error",
                f"Unexpected period labels found: {', '.join(invalid_periods)}.",
            )
        )

    non_positive_price_count = int((dataframe["nightly_price"] <= 0).fillna(False).sum())
    if non_positive_price_count > 0:
        findings.append(
            ValidationFinding(
                "listing_snapshot",
                "positive_nightly_price",
                "error",
                f"`nightly_price` contains `{non_positive_price_count}` non-positive values.",
            )
        )

    latitude_invalid = (dataframe["latitude"] < -90) | (dataframe["latitude"] > 90)
    longitude_invalid = (dataframe["longitude"] < -180) | (dataframe["longitude"] > 180)
    invalid_coordinate_count = int((latitude_invalid | longitude_invalid).fillna(False).sum())
    if invalid_coordinate_count > 0:
        findings.append(
            ValidationFinding(
                "listing_snapshot",
                "coordinate_bounds",
                "error",
                f"`latitude` or `longitude` is out of bounds in `{invalid_coordinate_count}` rows.",
            )
        )

    invalid_rating_count = int(
        ((dataframe["rating_score"] < 0) | (dataframe["rating_score"] > 5)).fillna(False).sum()
    )
    if invalid_rating_count > 0:
        findings.append(
            ValidationFinding(
                "listing_snapshot",
                "rating_bounds",
                "error",
                f"`rating_score` is outside the expected range [0, 5] in `{invalid_rating_count}` rows.",
            )
        )
    return findings


def _validate_grouped_semantics(dataset_name: str, dataframe: pd.DataFrame) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    required_columns = {"city_name", "period_label"}
    if not required_columns.issubset(dataframe.columns):
        return findings

    invalid_cities = sorted(set(dataframe["city_name"].dropna()) - CANONICAL_CITIES)
    if invalid_cities:
        findings.append(
            ValidationFinding(
                dataset_name,
                "canonical_city_labels",
                "error",
                f"Unexpected city labels found: {', '.join(invalid_cities)}.",
            )
        )
    invalid_periods = sorted(set(dataframe["period_label"].dropna()) - CANONICAL_PERIODS)
    if invalid_periods:
        findings.append(
            ValidationFinding(
                dataset_name,
                "canonical_period_labels",
                "error",
                f"Unexpected period labels found: {', '.join(invalid_periods)}.",
            )
        )
    return findings


def _validate_boundary_semantics(dataframe: pd.DataFrame) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    required_columns = {"city_name", "geometry_type"}
    if not required_columns.issubset(dataframe.columns):
        return findings

    invalid_cities = sorted(set(dataframe["city_name"].dropna()) - CANONICAL_CITIES)
    if invalid_cities:
        findings.append(
            ValidationFinding(
                "neighbourhood_boundary",
                "canonical_city_labels",
                "error",
                f"Unexpected city labels found: {', '.join(invalid_cities)}.",
            )
        )
    invalid_geometry_types = sorted(set(dataframe["geometry_type"].dropna()) - BOUNDARY_GEOMETRY_TYPES)
    if invalid_geometry_types:
        findings.append(
            ValidationFinding(
                "neighbourhood_boundary",
                "geometry_type_values",
                "error",
                f"Unexpected geometry types found: {', '.join(invalid_geometry_types)}.",
            )
        )
    return findings


def _validate_cross_dataset_consistency(
    loaded_frames: dict[str, pd.DataFrame],
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    reference = loaded_frames.get("neighbourhood_reference")
    boundary = loaded_frames.get("neighbourhood_boundary")
    if (
        reference is not None
        and boundary is not None
        and "neighbourhood_name" in reference.columns
        and "neighbourhood_name" in boundary.columns
    ):
        reference_names = set(reference["neighbourhood_name"].dropna().unique())
        unmatched = sorted(set(boundary["neighbourhood_name"].dropna().unique()) - reference_names)
        if unmatched:
            findings.append(
                ValidationFinding(
                    "neighbourhood_boundary",
                    "boundary_reference_alignment",
                    "error",
                    f"Boundary neighbourhoods missing from reference vocabulary: {', '.join(unmatched[:10])}.",
                )
            )
    return findings
