"""Serialization helpers for the Goal 2 inference bundle."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import joblib
import yaml

from feature_engineering.feature_registry import GROUP_COLUMN, TARGET_COLUMN
from .price_model_trainer import Goal2TrainingResult


def build_inference_bundle(
    training_result: Goal2TrainingResult,
    output_root: Path,
    *,
    bundle_version: str = "goal2_v10_diagnostics",
) -> dict[str, Path]:
    """Serialize the Goal 2 model bundle and metadata."""

    output_root.mkdir(parents=True, exist_ok=True)
    bundle_path = output_root / "inference_bundle.joblib"
    metadata_path = output_root / "inference_bundle_metadata.yaml"

    comparison = training_result.comparison
    model_artifacts = getattr(
        training_result,
        "model_artifacts",
        (training_result.linear_artifact, training_result.tree_artifact),
    )
    artifact_by_name = {artifact.model_name: artifact for artifact in model_artifacts}
    champion_artifact = artifact_by_name[comparison.champion_model_name]
    fallback_artifact = artifact_by_name[comparison.fallback_model_name]
    feature_columns_by_model = {
        artifact.model_name: artifact.raw_feature_columns
        for artifact in model_artifacts
    }
    model_estimate_interval_calibration = champion_artifact.evaluation.metadata.get("prediction_interval", {})
    model_estimate_interval_calibration_by_model = {
        artifact.model_name: artifact.evaluation.metadata.get("prediction_interval", {})
        for artifact in model_artifacts
    }
    payload: dict[str, Any] = {
        "bundle_version": bundle_version,
        "champion_model_name": champion_artifact.model_name,
        "fallback_model_name": fallback_artifact.model_name,
        "champion_pipeline": champion_artifact.pipeline,
        "fallback_pipeline": fallback_artifact.pipeline,
        "available_model_names": [artifact.model_name for artifact in model_artifacts],
        "feature_columns": champion_artifact.raw_feature_columns,
        "feature_columns_by_model": feature_columns_by_model,
        "target_column": TARGET_COLUMN,
        "group_column": GROUP_COLUMN,
        "comparison": comparison.to_dict(),
        "model_estimate_interval_calibration": model_estimate_interval_calibration,
        "model_estimate_interval_calibration_by_model": model_estimate_interval_calibration_by_model,
        "linear_explanation_context": training_result.linear_explanation_context,
    }
    joblib.dump(payload, bundle_path)
    metadata = {
        "bundle_version": bundle_version,
        "champion_model_name": champion_artifact.model_name,
        "fallback_model_name": fallback_artifact.model_name,
        "available_model_names": [artifact.model_name for artifact in model_artifacts],
        "training_date": date.today().isoformat(),
        "feature_columns": champion_artifact.raw_feature_columns,
        "feature_columns_by_model": feature_columns_by_model,
        "target_column": TARGET_COLUMN,
        "group_column": GROUP_COLUMN,
        "model_estimate_interval_calibration": model_estimate_interval_calibration,
        "model_estimate_interval_calibration_by_model": model_estimate_interval_calibration_by_model,
        "metrics": comparison.to_dict()["evaluations"],
    }
    with metadata_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(metadata, handle, sort_keys=False, allow_unicode=True)
    return {"bundle": bundle_path, "metadata": metadata_path}


def load_inference_bundle(bundle_path: Path) -> dict[str, Any]:
    """Load the serialized Goal 2 inference bundle."""

    return joblib.load(bundle_path)
