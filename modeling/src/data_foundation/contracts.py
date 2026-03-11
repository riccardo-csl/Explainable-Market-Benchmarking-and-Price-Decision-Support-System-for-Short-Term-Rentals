"""Typed contracts for source datasets, observed profiles, and target outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def _drop_none(value: Any) -> Any:
    if isinstance(value, list):
        return [_drop_none(item) for item in value]
    if isinstance(value, dict):
        return {key: _drop_none(item) for key, item in value.items() if item is not None}
    return value


@dataclass(frozen=True)
class CandidateKeyDefinition:
    columns: list[str]


@dataclass(frozen=True)
class CandidateKeyResult:
    columns: list[str]
    is_unique: bool
    duplicate_key_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FieldProfile:
    name: str
    inferred_type: str
    nullable: bool
    non_empty_count: int
    null_count: int
    sample_values: list[str]
    likely_categorical: bool
    unique_values_observed: int | None = None
    unique_values_truncated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ObservedDatasetProfile:
    dataset_name: str
    relative_path: str
    format: str
    grain: str
    row_count: int | None = None
    feature_count: int | None = None
    geometry_types: list[str] = field(default_factory=list)
    fields: list[FieldProfile] = field(default_factory=list)
    coverage: dict[str, list[str]] = field(default_factory=dict)
    candidate_keys: list[CandidateKeyResult] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _drop_none(asdict(self))


@dataclass(frozen=True)
class SourceDatasetDescriptor:
    name: str
    relative_path: str
    original_filename: str
    file_format: str
    grain: str
    role: str
    source_category: str
    encoding: str
    steward: str
    description: str
    immutable: bool = True
    candidate_keys: list[CandidateKeyDefinition] = field(default_factory=list)
    city_columns: list[str] = field(default_factory=list)
    period_columns: list[str] = field(default_factory=list)
    date_columns: list[str] = field(default_factory=list)
    categorical_hints: list[str] = field(default_factory=list)
    known_limitations: list[str] = field(default_factory=list)

    def absolute_path(self, repo_root: Path) -> Path:
        return repo_root / self.relative_path

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["candidate_keys"] = [key.columns for key in self.candidate_keys]
        return payload


@dataclass(frozen=True)
class RawDatasetManifest:
    dataset_name: str
    canonical_path: str
    original_filename: str
    source_category: str
    file_format: str
    encoding: str
    size_bytes: int
    sha256: str
    import_date: str
    steward: str
    immutable: bool
    description: str
    known_limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DatasetRelationship:
    from_dataset: str
    to_dataset: str
    relation_type: str
    join_columns: list[str]
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TargetFieldDescriptor:
    name: str
    data_type: str
    nullable: bool
    description: str
    source_columns: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TargetDatasetContract:
    name: str
    description: str
    grain: str
    primary_key: list[str]
    source_datasets: list[str]
    fields: list[TargetFieldDescriptor]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["fields"] = [field.to_dict() for field in self.fields]
        return payload
