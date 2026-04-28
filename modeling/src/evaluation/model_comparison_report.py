"""Model evaluation summaries and champion selection for Goal 2."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error

from feature_engineering.feature_registry import TARGET_COLUMN
from price_estimation.training_config import Goal2TrainingConfig, ModelEvaluationResult


@dataclass(frozen=True)
class TrainedModelArtifact:
    """Trained estimator plus Goal 2 evaluation outputs."""

    model_name: str
    pipeline: Any
    evaluation: ModelEvaluationResult
    feature_importances: dict[str, float]
    raw_feature_columns: list[str]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["pipeline"] = None
        return payload


@dataclass(frozen=True)
class ModelComparisonSummary:
    """Champion/fallback summary for Goal 2."""

    champion_model_name: str
    fallback_model_name: str
    evaluations: dict[str, dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_trained_model(
    model_name: str,
    pipeline: Any,
    feature_frame: pd.DataFrame,
    test_frame: pd.DataFrame,
    *,
    raw_feature_columns: list[str],
    config: Goal2TrainingConfig,
) -> TrainedModelArtifact:
    """Evaluate a trained model and collect feature importance artifacts."""

    features = raw_feature_columns
    predictions = pipeline.predict(test_frame[features])
    target = test_frame[TARGET_COLUMN]
    mae = float(mean_absolute_error(target, predictions))
    rmse = float(np.sqrt(mean_squared_error(target, predictions)))

    scored = test_frame[["city_name", "period_label", TARGET_COLUMN]].copy()
    scored["prediction"] = predictions
    scored["absolute_error"] = (scored[TARGET_COLUMN] - scored["prediction"]).abs()
    scored["price_band"] = pd.qcut(
        scored[TARGET_COLUMN],
        q=3,
        labels=["lower", "middle", "upper"],
        duplicates="drop",
    )

    evaluation = ModelEvaluationResult(
        model_name=model_name,
        mae=mae,
        rmse=rmse,
        per_city_mae=_grouped_mae(scored, "city_name"),
        per_period_mae=_grouped_mae(scored, "period_label"),
        price_band_mae=_grouped_mae(scored, "price_band"),
    )
    sampled = test_frame.sample(
        n=min(config.importance_sample_size, len(test_frame)),
        random_state=config.random_state,
    )
    importance = permutation_importance(
        pipeline,
        sampled[features],
        sampled[TARGET_COLUMN],
        n_repeats=5,
        random_state=config.random_state,
    )
    feature_importances = {
        feature_name: float(value)
        for feature_name, value in zip(features, importance.importances_mean)
    }
    return TrainedModelArtifact(
        model_name=model_name,
        pipeline=pipeline,
        evaluation=evaluation,
        feature_importances=feature_importances,
        raw_feature_columns=features,
    )


def choose_champion_model(
    linear_artifact: TrainedModelArtifact,
    tree_artifact: TrainedModelArtifact,
    config: Goal2TrainingConfig,
) -> ModelComparisonSummary:
    """Choose the champion model using the Goal 2 selection rule."""

    linear_mae = linear_artifact.evaluation.mae
    tree_mae = tree_artifact.evaluation.mae
    required_mae = linear_mae * (1.0 - config.champion_mae_improvement_threshold)
    tree_city_spread = _metric_spread(tree_artifact.evaluation.per_city_mae)
    linear_city_spread = _metric_spread(linear_artifact.evaluation.per_city_mae)

    if tree_mae <= required_mae and tree_city_spread <= linear_city_spread * 1.10:
        champion = tree_artifact
        fallback = linear_artifact
    else:
        champion = linear_artifact
        fallback = tree_artifact

    return ModelComparisonSummary(
        champion_model_name=champion.model_name,
        fallback_model_name=fallback.model_name,
        evaluations={
            linear_artifact.model_name: linear_artifact.evaluation.to_dict(),
            tree_artifact.model_name: tree_artifact.evaluation.to_dict(),
        },
    )


def _grouped_mae(scored: pd.DataFrame, column: str) -> dict[str, float]:
    grouped = scored.groupby(column, observed=True)["absolute_error"].mean().sort_index()
    return {str(key): float(value) for key, value in grouped.items()}


def _metric_spread(metric_map: dict[str, float]) -> float:
    if not metric_map:
        return 0.0
    values = list(metric_map.values())
    return max(values) - min(values)
