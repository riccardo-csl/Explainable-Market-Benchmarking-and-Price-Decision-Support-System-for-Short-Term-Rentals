"""Build the canonical Goal 2 modeling input table."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
import yaml


MAX_MODELING_NIGHTLY_PRICE = 1_500.0


@dataclass(frozen=True)
class ModelInputArtifact:
    """Goal 2 modeling input table plus reproducibility metadata."""

    dataframe: pd.DataFrame
    metadata: dict[str, object]


def load_goal2_source_tables(repo_root: Path) -> dict[str, pd.DataFrame]:
    """Load canonical cleaned datasets required by Goal 2."""

    base_path = repo_root / "data" / "processed" / "airbnb" / "parquet"
    return {
        "listing_snapshot": pd.read_parquet(base_path / "listing_snapshot.parquet"),
        "neighbourhood_reference": pd.read_parquet(base_path / "neighbourhood_reference.parquet"),
        "city_period_summary": pd.read_parquet(base_path / "city_period_summary.parquet"),
        "neighbourhood_period_summary": pd.read_parquet(base_path / "neighbourhood_period_summary.parquet"),
    }


def build_model_input_table(
    listing_snapshot: pd.DataFrame,
    neighbourhood_reference: pd.DataFrame,
) -> ModelInputArtifact:
    """Return the canonical Goal 2 listing-level modeling dataset."""

    dataframe = listing_snapshot.copy()
    dataframe["snapshot_date"] = pd.to_datetime(dataframe["snapshot_date"], errors="coerce")
    dataframe["host_since"] = pd.to_datetime(dataframe["host_since"], errors="coerce")

    reference = neighbourhood_reference.rename(
        columns={"neighbourhood_group_name": "reference_neighbourhood_group_name"}
    )
    dataframe = dataframe.merge(
        reference,
        on=["city_name", "neighbourhood_name"],
        how="left",
    )
    dataframe["neighbourhood_group_name"] = dataframe["reference_neighbourhood_group_name"]
    dataframe["venezia_group_name"] = dataframe.apply(_build_venezia_group_name, axis=1)
    dataframe["host_tenure_days"] = (
        dataframe["snapshot_date"] - dataframe["host_since"]
    ).dt.days.clip(lower=0)
    dataframe["season_peak_flag"] = dataframe["period_label"].isin(["Early Summer", "Early Autumn"])
    dataframe["season_shoulder_flag"] = dataframe["period_label"].isin(["Early Spring", "Early Winter"])
    pre_filter_row_count = len(dataframe)
    dataframe = dataframe[dataframe["nightly_price"] <= MAX_MODELING_NIGHTLY_PRICE].copy()
    dataframe = dataframe.drop(columns=["reference_neighbourhood_group_name"])
    dataframe = dataframe.sort_values(["listing_id", "snapshot_date"], kind="stable").reset_index(drop=True)

    metadata = {
        "target_column": "nightly_price",
        "group_column": "listing_id",
        "row_count": int(len(dataframe)),
        "rows_removed_for_high_price_outliers": int(pre_filter_row_count - len(dataframe)),
        "max_modeling_nightly_price": MAX_MODELING_NIGHTLY_PRICE,
        "excluded_training_columns": [
            "city_period_summary.*nightly_price*",
            "neighbourhood_period_summary.*nightly_price*",
            "neighbourhood_name",
            "snapshot_date",
            "host_since",
        ],
        "joins": {
            "neighbourhood_reference": {
                "join_columns": ["city_name", "neighbourhood_name"],
                "null_rate_after_join": float(dataframe["neighbourhood_group_name"].isna().mean()),
            }
        },
    }
    return ModelInputArtifact(dataframe=dataframe, metadata=metadata)


def build_model_input_artifact(repo_root: Path, output_root: Path | None = None) -> dict[str, Path]:
    """Build and persist the Goal 2 modeling input artifact and metadata."""
    return build_model_input_artifact_versioned(repo_root, output_root=output_root, version=None)


def build_model_input_artifact_versioned(
    repo_root: Path,
    *,
    output_root: Path | None = None,
    version: str | None = None,
) -> dict[str, Path]:
    """Build and persist the Goal 2 modeling input artifact and metadata."""

    resolved_repo_root = repo_root.resolve()
    resolved_output_root = resolved_repo_root if output_root is None else output_root.resolve()
    sources = load_goal2_source_tables(resolved_repo_root)
    artifact = build_model_input_table(
        sources["listing_snapshot"],
        sources["neighbourhood_reference"],
    )
    artifact_root = resolved_output_root / "data" / "processed" / "airbnb" / "modeling"
    if version is not None:
        artifact_root = artifact_root / version
    artifact_root.mkdir(parents=True, exist_ok=True)
    parquet_path = artifact_root / "listing_price_model_input.parquet"
    csv_path = artifact_root / "listing_price_model_input.csv"
    metadata_path = artifact_root / "listing_price_model_input_metadata.yaml"
    artifact.dataframe.to_parquet(parquet_path, index=False)
    artifact.dataframe.to_csv(csv_path, index=False)
    with metadata_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(artifact.metadata, handle, sort_keys=False, allow_unicode=True)
    return {"parquet": parquet_path, "csv": csv_path, "metadata": metadata_path}


def _build_venezia_group_name(row: pd.Series) -> str | None:
    if row["city_name"] != "Venezia":
        return None
    value = row.get("neighbourhood_group_name")
    if pd.isna(value):
        return None
    return str(value)
