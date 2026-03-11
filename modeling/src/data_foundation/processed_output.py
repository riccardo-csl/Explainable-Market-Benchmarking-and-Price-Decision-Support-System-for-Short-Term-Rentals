"""Processed output writing and manifest generation."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from .report_writer import write_yaml


@dataclass(frozen=True)
class ProcessedDatasetManifest:
    dataset_name: str
    parquet_path: str
    csv_path: str
    row_count: int
    columns: list[str]
    source_datasets: list[str]
    generation_date: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def write_processed_dataset(
    dataset_name: str,
    dataframe: pd.DataFrame,
    source_datasets: list[str],
    output_root: Path,
    generation_date: str | None = None,
) -> tuple[list[Path], ProcessedDatasetManifest]:
    resolved_generation_date = generation_date or date.today().isoformat()
    parquet_root = output_root / "data" / "processed" / "airbnb" / "parquet"
    csv_root = output_root / "data" / "processed" / "airbnb" / "csv"
    manifest_root = output_root / "data" / "processed" / "airbnb" / "_manifests"

    parquet_root.mkdir(parents=True, exist_ok=True)
    csv_root.mkdir(parents=True, exist_ok=True)
    manifest_root.mkdir(parents=True, exist_ok=True)

    parquet_path = parquet_root / f"{dataset_name}.parquet"
    csv_path = csv_root / f"{dataset_name}.csv"
    manifest_path = manifest_root / f"{dataset_name}.yaml"

    dataframe.to_parquet(parquet_path, index=False)
    dataframe.to_csv(csv_path, index=False)

    manifest = ProcessedDatasetManifest(
        dataset_name=dataset_name,
        parquet_path=str(parquet_path.relative_to(output_root)),
        csv_path=str(csv_path.relative_to(output_root)),
        row_count=len(dataframe),
        columns=list(dataframe.columns),
        source_datasets=source_datasets,
        generation_date=resolved_generation_date,
    )
    write_yaml(manifest_path, manifest.to_dict())
    return [parquet_path, csv_path, manifest_path], manifest
