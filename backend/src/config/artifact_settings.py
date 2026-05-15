"""Artifact path configuration for the local Goal 4 beta."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_ARTIFACT_VERSION = "goal2_v10_diagnostics"


@dataclass(frozen=True)
class Goal2ArtifactSettings:
    """Resolved paths for the Goal 2 artifacts served by the backend."""

    repo_root: Path
    artifact_version: str = DEFAULT_ARTIFACT_VERSION

    @classmethod
    def from_environment(cls) -> "Goal2ArtifactSettings":
        repo_root = Path(
            os.getenv("GOAL4_REPO_ROOT", Path(__file__).resolve().parents[3])
        ).resolve()
        artifact_version = os.getenv("GOAL4_ARTIFACT_VERSION", DEFAULT_ARTIFACT_VERSION)
        return cls(repo_root=repo_root, artifact_version=artifact_version)

    @property
    def artifact_root(self) -> Path:
        return (
            self.repo_root
            / "data"
            / "processed"
            / "airbnb"
            / "modeling"
            / self.artifact_version
        )

    @property
    def processed_parquet_root(self) -> Path:
        return self.repo_root / "data" / "processed" / "airbnb" / "parquet"

    @property
    def inference_bundle_path(self) -> Path:
        return self.artifact_root / "inference_bundle.joblib"

    @property
    def inference_metadata_path(self) -> Path:
        return self.artifact_root / "inference_bundle_metadata.yaml"

    @property
    def feature_matrix_path(self) -> Path:
        return self.artifact_root / "price_feature_matrix.parquet"

    @property
    def city_period_summary_path(self) -> Path:
        return self.processed_parquet_root / "city_period_summary.parquet"

    @property
    def neighbourhood_period_summary_path(self) -> Path:
        return self.processed_parquet_root / "neighbourhood_period_summary.parquet"

    def required_paths(self) -> tuple[Path, ...]:
        return (
            self.inference_bundle_path,
            self.inference_metadata_path,
            self.feature_matrix_path,
            self.city_period_summary_path,
            self.neighbourhood_period_summary_path,
        )

    def missing_paths(self) -> list[Path]:
        return [path for path in self.required_paths() if not path.exists()]
