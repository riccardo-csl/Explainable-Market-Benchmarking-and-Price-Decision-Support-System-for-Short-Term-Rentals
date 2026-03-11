"""Inspection utilities for source datasets."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable

from .contracts import CandidateKeyResult, FieldProfile, ObservedDatasetProfile, SourceDatasetDescriptor

UNIQUE_SAMPLE_LIMIT = 20


def _infer_primitive_type(value: str) -> str:
    text = value.strip()
    if not text:
        return "empty"

    try:
        int(text)
    except ValueError:
        pass
    else:
        return "integer"

    try:
        float(text)
    except ValueError:
        pass
    else:
        return "float"

    try:
        date.fromisoformat(text)
    except ValueError:
        return "string"
    return "date"


def _collapse_types(types: set[str]) -> str:
    resolved = {item for item in types if item != "empty"}
    if not resolved:
        return "string"
    if resolved == {"integer"}:
        return "integer"
    if resolved <= {"integer", "float"}:
        return "float"
    if resolved == {"date"}:
        return "date"
    return "string"


@dataclass
class _FieldAccumulator:
    values_seen: set[str] = field(default_factory=set)
    sample_values: list[str] = field(default_factory=list)
    types_seen: set[str] = field(default_factory=set)
    non_empty_count: int = 0
    null_count: int = 0
    unique_values_truncated: bool = False

    def consume(self, raw_value: str | None) -> None:
        text = "" if raw_value is None else str(raw_value).strip()
        if not text:
            self.null_count += 1
            self.types_seen.add("empty")
            return

        self.non_empty_count += 1
        self.types_seen.add(_infer_primitive_type(text))
        if text not in self.values_seen:
            if len(self.values_seen) < UNIQUE_SAMPLE_LIMIT:
                self.values_seen.add(text)
                self.sample_values.append(text)
            else:
                self.unique_values_truncated = True

    def to_profile(self, field_name: str, categorical_hints: Iterable[str]) -> FieldProfile:
        inferred_type = _collapse_types(self.types_seen)
        likely_categorical = field_name in categorical_hints or (
            inferred_type == "string" and not self.unique_values_truncated and len(self.values_seen) <= 20
        )
        return FieldProfile(
            name=field_name,
            inferred_type=inferred_type,
            nullable=self.null_count > 0,
            non_empty_count=self.non_empty_count,
            null_count=self.null_count,
            sample_values=self.sample_values[:5],
            likely_categorical=likely_categorical,
            unique_values_observed=len(self.values_seen),
            unique_values_truncated=self.unique_values_truncated,
        )


def inspect_dataset(spec: SourceDatasetDescriptor, repo_root: Path) -> ObservedDatasetProfile:
    if spec.file_format == "csv":
        return _inspect_csv_dataset(spec, repo_root)
    if spec.file_format == "geojson":
        return _inspect_geojson_dataset(spec, repo_root)
    raise ValueError(f"Unsupported dataset format: {spec.file_format}")


def _inspect_csv_dataset(spec: SourceDatasetDescriptor, repo_root: Path) -> ObservedDatasetProfile:
    path = spec.absolute_path(repo_root)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} does not contain a header row.")

        accumulators = {field_name: _FieldAccumulator() for field_name in reader.fieldnames}
        candidate_sets = [set() for _ in spec.candidate_keys]
        candidate_duplicates = [0 for _ in spec.candidate_keys]
        coverage: dict[str, set[str]] = defaultdict(set)
        row_count = 0

        for row in reader:
            row_count += 1
            for field_name, raw_value in row.items():
                accumulators[field_name].consume(raw_value)

            for index, candidate_key in enumerate(spec.candidate_keys):
                key_tuple = tuple((row.get(column) or "").strip() for column in candidate_key.columns)
                if key_tuple in candidate_sets[index]:
                    candidate_duplicates[index] += 1
                else:
                    candidate_sets[index].add(key_tuple)

            for field_name in spec.city_columns:
                if row.get(field_name):
                    coverage["cities"].add(row[field_name].strip())
            for field_name in spec.period_columns:
                if row.get(field_name):
                    coverage["periods"].add(row[field_name].strip())
            for field_name in spec.date_columns:
                if row.get(field_name):
                    coverage["snapshot_dates"].add(row[field_name].strip())

    field_profiles = [
        accumulators[field_name].to_profile(field_name, spec.categorical_hints)
        for field_name in reader.fieldnames
    ]

    candidate_key_results = [
        CandidateKeyResult(
            columns=definition.columns,
            is_unique=(duplicate_count == 0),
            duplicate_key_count=duplicate_count,
        )
        for definition, duplicate_count in zip(spec.candidate_keys, candidate_duplicates)
    ]

    return ObservedDatasetProfile(
        dataset_name=spec.name,
        relative_path=spec.relative_path,
        format=spec.file_format,
        grain=spec.grain,
        row_count=row_count,
        fields=field_profiles,
        coverage={key: sorted(values) for key, values in coverage.items()},
        candidate_keys=candidate_key_results,
        notes=spec.known_limitations,
    )


def _inspect_geojson_dataset(spec: SourceDatasetDescriptor, repo_root: Path) -> ObservedDatasetProfile:
    path = spec.absolute_path(repo_root)
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    features = payload.get("features", [])
    property_accumulators: dict[str, _FieldAccumulator] = {}
    geometry_types: set[str] = set()

    for feature in features:
        properties = feature.get("properties") or {}
        for field_name in properties:
            property_accumulators.setdefault(field_name, _FieldAccumulator())
        for field_name, accumulator in property_accumulators.items():
            accumulator.consume(properties.get(field_name))
        geometry = feature.get("geometry") or {}
        if geometry.get("type"):
            geometry_types.add(str(geometry["type"]))

    field_profiles = [
        property_accumulators[field_name].to_profile(field_name, spec.categorical_hints)
        for field_name in sorted(property_accumulators)
    ]

    return ObservedDatasetProfile(
        dataset_name=spec.name,
        relative_path=spec.relative_path,
        format=spec.file_format,
        grain=spec.grain,
        feature_count=len(features),
        geometry_types=sorted(geometry_types),
        fields=field_profiles,
        coverage={},
        candidate_keys=[],
        notes=spec.known_limitations,
    )
