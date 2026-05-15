"""Model evaluation summaries and champion selection for Goal 2."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error

from benchmarking.benchmark_range_calculator import calculate_benchmark_range, classify_price_positioning
from benchmarking.listing_similarity_engine import select_comparable_listings
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
    metadata: dict[str, Any] | None = None,
    neighbourhood_period_summary: pd.DataFrame | None = None,
    city_period_summary: pd.DataFrame | None = None,
) -> TrainedModelArtifact:
    """Evaluate a trained model and collect feature importance artifacts."""

    features = raw_feature_columns
    predictions = pipeline.predict(test_frame[features])
    target = test_frame[TARGET_COLUMN]
    mae = float(mean_absolute_error(target, predictions))
    rmse = float(np.sqrt(mean_squared_error(target, predictions)))

    scored = test_frame[["city_name", "period_label", "room_type", TARGET_COLUMN]].copy()
    scored["prediction"] = predictions
    scored["absolute_error"] = (scored[TARGET_COLUMN] - scored["prediction"]).abs()
    scored["absolute_percentage_error"] = np.where(
        scored[TARGET_COLUMN] > 0,
        scored["absolute_error"] / scored[TARGET_COLUMN],
        np.nan,
    )
    scored["price_band"] = pd.qcut(
        scored[TARGET_COLUMN],
        q=3,
        labels=["lower", "middle", "upper"],
        duplicates="drop",
    )
    benchmark_diagnostics = _build_benchmark_diagnostics(
        feature_frame,
        test_frame,
        predictions,
        config=config,
        neighbourhood_period_summary=neighbourhood_period_summary,
        city_period_summary=city_period_summary,
    )
    mape = _safe_mean(scored["absolute_percentage_error"])

    evaluation_metadata = {} if metadata is None else dict(metadata)
    evaluation_metadata["prediction_interval"] = _build_prediction_interval_calibration(
        target=target,
        predictions=predictions,
        config=config,
    )

    evaluation = ModelEvaluationResult(
        model_name=model_name,
        mae=mae,
        rmse=rmse,
        per_city_mae=_grouped_mae(scored, "city_name"),
        per_period_mae=_grouped_mae(scored, "period_label"),
        per_room_type_mae=_grouped_mae(scored, "room_type"),
        price_band_mae=_grouped_mae(scored, "price_band"),
        mape=None if mape is None else mape * 100.0,
        benchmark_positioning_mae=benchmark_diagnostics["benchmark_positioning_mae"],
        model_prediction_inside_benchmark_rate=benchmark_diagnostics["model_prediction_inside_benchmark_rate"],
        model_positioning_agreement_rate=benchmark_diagnostics["model_positioning_agreement_rate"],
        metadata=evaluation_metadata,
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
    baseline_artifact: TrainedModelArtifact,
    *challenger_artifacts: TrainedModelArtifact,
    config: Goal2TrainingConfig,
) -> ModelComparisonSummary:
    """Choose the champion model using MAE improvement and per-city regression gates."""

    artifacts = (baseline_artifact, *challenger_artifacts)
    baseline_mae = baseline_artifact.evaluation.mae
    required_mae = baseline_mae * (1.0 - config.champion_mae_improvement_threshold)
    eligible_challengers = [
        artifact
        for artifact in challenger_artifacts
        if artifact.evaluation.mae <= required_mae
        and _does_not_materially_regress_city_mae(
            baseline_artifact.evaluation.per_city_mae,
            artifact.evaluation.per_city_mae,
            tolerance=config.champion_city_mae_regression_tolerance,
        )
    ]
    if eligible_challengers:
        champion = min(eligible_challengers, key=lambda artifact: artifact.evaluation.mae)
    else:
        champion = baseline_artifact

    fallback_candidates = [artifact for artifact in artifacts if artifact.model_name != champion.model_name]
    if champion.model_name != baseline_artifact.model_name:
        fallback = baseline_artifact
    else:
        fallback = min(fallback_candidates, key=lambda artifact: artifact.evaluation.mae)

    return ModelComparisonSummary(
        champion_model_name=champion.model_name,
        fallback_model_name=fallback.model_name,
        evaluations={
            artifact.model_name: artifact.evaluation.to_dict()
            for artifact in artifacts
        },
    )


def _grouped_mae(scored: pd.DataFrame, column: str) -> dict[str, float]:
    grouped = scored.groupby(column, observed=True)["absolute_error"].mean().sort_index()
    return {str(key): float(value) for key, value in grouped.items()}


def _build_benchmark_diagnostics(
    feature_frame: pd.DataFrame,
    test_frame: pd.DataFrame,
    predictions: np.ndarray,
    *,
    config: Goal2TrainingConfig,
    neighbourhood_period_summary: pd.DataFrame | None,
    city_period_summary: pd.DataFrame | None,
) -> dict[str, object]:
    if neighbourhood_period_summary is None or city_period_summary is None:
        return {
            "benchmark_positioning_mae": {},
            "model_prediction_inside_benchmark_rate": None,
            "model_positioning_agreement_rate": None,
        }

    diagnostic_frame = test_frame.copy()
    diagnostic_frame["prediction"] = predictions
    if len(diagnostic_frame) > config.benchmark_diagnostic_sample_size:
        diagnostic_frame = diagnostic_frame.sample(
            n=config.benchmark_diagnostic_sample_size,
            random_state=config.random_state,
        )

    rows = []
    for _, target_listing in diagnostic_frame.iterrows():
        comparable_result = select_comparable_listings(feature_frame, target_listing)
        benchmark_range = calculate_benchmark_range(
            target_listing,
            comparable_result.comparables,
            neighbourhood_period_summary,
            city_period_summary,
        )
        observed_label = classify_price_positioning(
            float(target_listing[TARGET_COLUMN]),
            benchmark_range,
        )
        prediction = float(target_listing["prediction"])
        predicted_label = classify_price_positioning(prediction, benchmark_range)
        rows.append(
            {
                "observed_benchmark_positioning": observed_label,
                "predicted_benchmark_positioning": predicted_label,
                "prediction_inside_benchmark": predicted_label == "aligned",
                "positioning_agrees": predicted_label == observed_label,
                "absolute_error": abs(float(target_listing[TARGET_COLUMN]) - prediction),
            }
        )

    benchmark_scored = pd.DataFrame(rows)
    if benchmark_scored.empty:
        return {
            "benchmark_positioning_mae": {},
            "model_prediction_inside_benchmark_rate": None,
            "model_positioning_agreement_rate": None,
        }
    return {
        "benchmark_positioning_mae": _grouped_mae(
            benchmark_scored.rename(columns={"observed_benchmark_positioning": "positioning"}),
            "positioning",
        ),
        "model_prediction_inside_benchmark_rate": float(
            benchmark_scored["prediction_inside_benchmark"].mean()
        ),
        "model_positioning_agreement_rate": float(
            benchmark_scored["positioning_agrees"].mean()
        ),
    }


def _safe_mean(series: pd.Series) -> float | None:
    value = series.dropna().mean()
    if pd.isna(value):
        return None
    return float(value)


def _build_prediction_interval_calibration(
    *,
    target: pd.Series,
    predictions: np.ndarray,
    config: Goal2TrainingConfig,
) -> dict[str, float | str]:
    confidence_level = min(max(float(config.prediction_interval_confidence_level), 0.01), 0.99)
    tail_probability = (1.0 - confidence_level) / 2.0
    residuals = target.to_numpy(dtype=float) - np.asarray(predictions, dtype=float)
    lower_residual_quantile = float(np.quantile(residuals, tail_probability))
    upper_residual_quantile = float(np.quantile(residuals, 1.0 - tail_probability))
    interval_lower = np.asarray(predictions, dtype=float) + lower_residual_quantile
    interval_upper = np.asarray(predictions, dtype=float) + upper_residual_quantile
    empirical_coverage_rate = float(
        np.mean((target.to_numpy(dtype=float) >= interval_lower) & (target.to_numpy(dtype=float) <= interval_upper))
    )
    return {
        "source": "heldout_residual_quantiles",
        "confidence_level": confidence_level,
        "lower_residual_quantile": lower_residual_quantile,
        "upper_residual_quantile": upper_residual_quantile,
        "empirical_coverage_rate": empirical_coverage_rate,
    }


def _does_not_materially_regress_city_mae(
    baseline_city_mae: dict[str, float],
    challenger_city_mae: dict[str, float],
    *,
    tolerance: float,
) -> bool:
    for city_name, baseline_value in baseline_city_mae.items():
        challenger_value = challenger_city_mae.get(city_name)
        if challenger_value is None:
            return False
        if challenger_value > baseline_value * (1.0 + tolerance):
            return False
    return True
