"""Load and validate Goal 2 artifacts for serving."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from config.artifact_settings import Goal2ArtifactSettings
from price_estimation.inference_bundle_builder import load_inference_bundle


class ArtifactConfigurationError(RuntimeError):
    """Raised when required local Goal 2 artifacts are unavailable."""


@dataclass(frozen=True)
class Goal2Artifacts:
    """In-memory Goal 2 artifacts used by the pricing service."""

    bundle: dict[str, Any]
    metadata: dict[str, Any]
    feature_frame: pd.DataFrame
    city_period_summary: pd.DataFrame
    neighbourhood_period_summary: pd.DataFrame


def load_goal2_artifacts(settings: Goal2ArtifactSettings) -> Goal2Artifacts:
    """Load every artifact required to produce a price decision payload."""

    missing_paths = settings.missing_paths()
    if missing_paths:
        formatted_paths = ", ".join(str(path) for path in missing_paths)
        raise ArtifactConfigurationError(f"Missing required Goal 2 artifacts: {formatted_paths}")

    metadata = _load_yaml(settings.inference_metadata_path)
    return Goal2Artifacts(
        bundle=load_inference_bundle(settings.inference_bundle_path),
        metadata=metadata,
        feature_frame=pd.read_parquet(settings.feature_matrix_path),
        city_period_summary=pd.read_parquet(settings.city_period_summary_path),
        neighbourhood_period_summary=pd.read_parquet(settings.neighbourhood_period_summary_path),
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ArtifactConfigurationError(f"Expected YAML mapping in {path}")
    return loaded
