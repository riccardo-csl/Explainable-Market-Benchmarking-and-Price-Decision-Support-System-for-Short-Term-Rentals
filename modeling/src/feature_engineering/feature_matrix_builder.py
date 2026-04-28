"""Build the reusable Goal 2 feature matrix."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from .feature_registry import GROUP_COLUMN, IDENTIFIER_COLUMNS, TARGET_COLUMN, model_feature_columns
from .location_feature_builder import attach_distance_features
from .model_input_builder import ModelInputArtifact, build_model_input_table, load_goal2_source_tables


def build_feature_frame(model_input: pd.DataFrame) -> pd.DataFrame:
    """Add derived Goal 2 features on top of the canonical modeling input."""

    dataframe = model_input.copy()
    dataframe = attach_distance_features(dataframe)
    ordered_columns = [
        *IDENTIFIER_COLUMNS,
        TARGET_COLUMN,
        *model_feature_columns(),
    ]
    return dataframe[ordered_columns].drop_duplicates(subset=["listing_id", "snapshot_date"])


def build_feature_matrix_artifact(repo_root: Path, output_root: Path | None = None) -> dict[str, Path]:
    """Build and persist the Goal 2 feature matrix artifact and metadata."""
    return build_feature_matrix_artifact_versioned(repo_root, output_root=output_root, version=None)


def build_feature_matrix_artifact_versioned(
    repo_root: Path,
    *,
    output_root: Path | None = None,
    version: str | None = None,
) -> dict[str, Path]:
    """Build and persist the Goal 2 feature matrix artifact and metadata."""

    resolved_repo_root = repo_root.resolve()
    resolved_output_root = resolved_repo_root if output_root is None else output_root.resolve()
    sources = load_goal2_source_tables(resolved_repo_root)
    model_input_artifact: ModelInputArtifact = build_model_input_table(
        sources["listing_snapshot"],
        sources["neighbourhood_reference"],
    )
    feature_frame = build_feature_frame(model_input_artifact.dataframe)
    artifact_root = resolved_output_root / "data" / "processed" / "airbnb" / "modeling"
    if version is not None:
        artifact_root = artifact_root / version
    artifact_root.mkdir(parents=True, exist_ok=True)
    parquet_path = artifact_root / "price_feature_matrix.parquet"
    csv_path = artifact_root / "price_feature_matrix.csv"
    metadata_path = artifact_root / "price_feature_matrix_metadata.yaml"
    feature_frame.to_parquet(parquet_path, index=False)
    feature_frame.to_csv(csv_path, index=False)
    metadata = {
        "target_column": TARGET_COLUMN,
        "group_column": GROUP_COLUMN,
        "feature_columns": model_feature_columns(),
        "row_count": int(len(feature_frame)),
    }
    with metadata_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(metadata, handle, sort_keys=False, allow_unicode=True)
    return {"parquet": parquet_path, "csv": csv_path, "metadata": metadata_path}
