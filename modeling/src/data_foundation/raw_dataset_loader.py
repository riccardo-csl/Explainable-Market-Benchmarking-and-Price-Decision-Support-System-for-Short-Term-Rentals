"""Load canonical raw datasets into pandas dataframes."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .contracts import SourceDatasetDescriptor


def load_raw_dataset(descriptor: SourceDatasetDescriptor, repo_root: Path) -> pd.DataFrame:
    dataset_path = descriptor.absolute_path(repo_root)
    if descriptor.file_format == "csv":
        return pd.read_csv(dataset_path)
    if descriptor.file_format == "geojson":
        return _load_geojson_features(dataset_path)
    raise ValueError(f"Unsupported raw dataset format: {descriptor.file_format}")


def load_raw_datasets(
    descriptors: list[SourceDatasetDescriptor],
    repo_root: Path,
) -> dict[str, pd.DataFrame]:
    return {
        descriptor.name: load_raw_dataset(descriptor, repo_root)
        for descriptor in descriptors
    }


def _load_geojson_features(path: Path) -> pd.DataFrame:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    rows: list[dict] = []
    for index, feature in enumerate(payload.get("features", [])):
        properties = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        rows.append(
            {
                "raw_feature_index": index,
                "neighbourhood": properties.get("neighbourhood"),
                "neighbourhood_group": properties.get("neighbourhood_group"),
                "geometry_type": geometry.get("type"),
                "geometry": geometry,
            }
        )
    return pd.DataFrame(rows)
