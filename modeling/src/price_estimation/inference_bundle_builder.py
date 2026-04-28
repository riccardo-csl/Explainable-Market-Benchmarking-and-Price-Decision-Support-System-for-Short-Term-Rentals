"""Serialization helpers for the Goal 2 inference bundle."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import joblib
import yaml

from feature_engineering.feature_registry import GROUP_COLUMN, TARGET_COLUMN, model_feature_columns
from .price_model_trainer import Goal2TrainingResult


def build_inference_bundle(
    training_result: Goal2TrainingResult,
    output_root: Path,
    *,
    bundle_version: str = "goal2_v4",
) -> dict[str, Path]:
    """Serialize the Goal 2 model bundle and metadata."""

    output_root.mkdir(parents=True, exist_ok=True)
    bundle_path = output_root / "inference_bundle.joblib"
    metadata_path = output_root / "inference_bundle_metadata.yaml"

    comparison = training_result.comparison
    champion_artifact = (
        training_result.linear_artifact
        if comparison.champion_model_name == training_result.linear_artifact.model_name
        else training_result.tree_artifact
    )
    fallback_artifact = (
        training_result.tree_artifact
        if champion_artifact.model_name == training_result.linear_artifact.model_name
        else training_result.linear_artifact
    )
    payload: dict[str, Any] = {
        "bundle_version": bundle_version,
        "champion_model_name": champion_artifact.model_name,
        "fallback_model_name": fallback_artifact.model_name,
        "champion_pipeline": champion_artifact.pipeline,
        "fallback_pipeline": fallback_artifact.pipeline,
        "feature_columns": model_feature_columns(),
        "target_column": TARGET_COLUMN,
        "group_column": GROUP_COLUMN,
        "comparison": comparison.to_dict(),
        "linear_explanation_context": training_result.linear_explanation_context,
    }
    joblib.dump(payload, bundle_path)
    metadata = {
        "bundle_version": bundle_version,
        "champion_model_name": champion_artifact.model_name,
        "fallback_model_name": fallback_artifact.model_name,
        "training_date": date.today().isoformat(),
        "feature_columns": model_feature_columns(),
        "target_column": TARGET_COLUMN,
        "group_column": GROUP_COLUMN,
        "metrics": comparison.to_dict()["evaluations"],
    }
    with metadata_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(metadata, handle, sort_keys=False, allow_unicode=True)
    return {"bundle": bundle_path, "metadata": metadata_path}


def load_inference_bundle(bundle_path: Path) -> dict[str, Any]:
    """Load the serialized Goal 2 inference bundle."""

    return joblib.load(bundle_path)
