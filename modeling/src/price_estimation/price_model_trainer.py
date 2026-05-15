"""Training orchestration for Goal 2 models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupShuffleSplit

from evaluation.data_profile_report import build_data_profile_report
from evaluation.leakage_audit import audit_feature_columns
from evaluation.model_comparison_report import (
    ModelComparisonSummary,
    TrainedModelArtifact,
    choose_champion_model,
    evaluate_trained_model,
)
from explainability.local_explanation_builder import build_linear_explanation_context
from feature_engineering.feature_matrix_builder import build_feature_frame
from feature_engineering.feature_registry import GROUP_COLUMN, TARGET_COLUMN, model_feature_columns
from feature_engineering.feature_registry import catboost_feature_columns
from feature_engineering.model_input_builder import build_model_input_table, load_goal2_source_tables
from .model_registry import build_catboost_pipeline, build_linear_pipeline, build_tree_pipeline
from .training_config import CatBoostHyperparameters, Goal2TrainingConfig


@dataclass(frozen=True)
class Goal2TrainingResult:
    """Full Goal 2 training output."""

    feature_frame: pd.DataFrame
    train_frame: pd.DataFrame
    validation_frame: pd.DataFrame
    test_frame: pd.DataFrame
    linear_artifact: TrainedModelArtifact
    tree_artifact: TrainedModelArtifact
    catboost_artifact: TrainedModelArtifact
    model_artifacts: tuple[TrainedModelArtifact, ...]
    comparison: ModelComparisonSummary
    linear_explanation_context: dict[str, Any]
    data_profile: dict[str, object]


def train_goal2_models(
    repo_root,
    *,
    config: Goal2TrainingConfig | None = None,
) -> Goal2TrainingResult:
    """Train Goal 2 linear, tree, and CatBoost estimators on the canonical feature frame."""

    resolved_config = Goal2TrainingConfig() if config is None else config
    sources = load_goal2_source_tables(repo_root)
    model_input = build_model_input_table(
        sources["listing_snapshot"],
        sources["neighbourhood_reference"],
    )
    feature_frame = build_feature_frame(model_input.dataframe)
    return train_models_from_feature_frame(
        feature_frame,
        config=resolved_config,
        neighbourhood_period_summary=sources["neighbourhood_period_summary"],
        city_period_summary=sources["city_period_summary"],
    )


def train_models_from_feature_frame(
    feature_frame: pd.DataFrame,
    *,
    config: Goal2TrainingConfig | None = None,
    neighbourhood_period_summary: pd.DataFrame | None = None,
    city_period_summary: pd.DataFrame | None = None,
) -> Goal2TrainingResult:
    """Train Goal 2 estimators from a prepared feature frame."""

    resolved_config = Goal2TrainingConfig() if config is None else config
    feature_columns = model_feature_columns()
    catboost_columns = catboost_feature_columns(
        include_local_market_categoricals=resolved_config.catboost_rich_categorical_experiments_enabled
    )
    leakage_findings = audit_feature_columns(sorted(set([*feature_columns, *catboost_columns])))
    if leakage_findings:
        raise ValueError(f"Leakage audit failed: {leakage_findings}")

    train_frame, validation_frame, test_frame = split_feature_frame(feature_frame, resolved_config)
    combined_train_frame = pd.concat([train_frame, validation_frame], ignore_index=True)

    linear_pipeline = build_linear_pipeline(resolved_config)
    linear_pipeline.fit(combined_train_frame[feature_columns], combined_train_frame[TARGET_COLUMN])
    tree_pipeline = build_tree_pipeline(resolved_config)
    tree_pipeline.fit(combined_train_frame[feature_columns], combined_train_frame[TARGET_COLUMN])
    catboost_pipeline, catboost_tuning_metadata = fit_tuned_catboost_pipeline(
        train_frame,
        validation_frame,
        combined_train_frame,
        feature_columns=catboost_columns,
        config=resolved_config,
    )

    linear_artifact = evaluate_trained_model(
        "linear_baseline",
        linear_pipeline,
        feature_frame,
        test_frame,
        raw_feature_columns=feature_columns,
        config=resolved_config,
        neighbourhood_period_summary=neighbourhood_period_summary,
        city_period_summary=city_period_summary,
    )
    tree_artifact = evaluate_trained_model(
        "tree_challenger",
        tree_pipeline,
        feature_frame,
        test_frame,
        raw_feature_columns=feature_columns,
        config=resolved_config,
        neighbourhood_period_summary=neighbourhood_period_summary,
        city_period_summary=city_period_summary,
    )
    catboost_artifact = evaluate_trained_model(
        "catboost_challenger",
        catboost_pipeline,
        feature_frame,
        test_frame,
        raw_feature_columns=catboost_columns,
        config=resolved_config,
        metadata=catboost_tuning_metadata,
        neighbourhood_period_summary=neighbourhood_period_summary,
        city_period_summary=city_period_summary,
    )
    model_artifacts = (linear_artifact, tree_artifact, catboost_artifact)
    comparison = choose_champion_model(
        linear_artifact,
        tree_artifact,
        catboost_artifact,
        config=resolved_config,
    )
    linear_explanation_context = build_linear_explanation_context(
        linear_pipeline,
        combined_train_frame,
        feature_columns=feature_columns,
    )
    data_profile = build_data_profile_report(feature_frame).to_dict()
    return Goal2TrainingResult(
        feature_frame=feature_frame,
        train_frame=train_frame,
        validation_frame=validation_frame,
        test_frame=test_frame,
        linear_artifact=linear_artifact,
        tree_artifact=tree_artifact,
        catboost_artifact=catboost_artifact,
        model_artifacts=model_artifacts,
        comparison=comparison,
        linear_explanation_context=linear_explanation_context,
        data_profile=data_profile,
    )


def fit_tuned_catboost_pipeline(
    train_frame: pd.DataFrame,
    validation_frame: pd.DataFrame,
    combined_train_frame: pd.DataFrame,
    *,
    feature_columns: list[str],
    config: Goal2TrainingConfig,
):
    """Select CatBoost parameters on validation, then refit on train+validation."""

    candidates = build_catboost_tuning_candidates(config)
    validation_results = []
    best_candidate = candidates[0]
    best_mae = float("inf")
    best_rmse = float("inf")

    for candidate in candidates:
        pipeline = build_catboost_pipeline(config, candidate)
        pipeline.fit(train_frame[feature_columns], train_frame[TARGET_COLUMN])
        predictions = pipeline.predict(validation_frame[feature_columns])
        target = validation_frame[TARGET_COLUMN]
        mae = float(mean_absolute_error(target, predictions))
        rmse = float(np.sqrt(mean_squared_error(target, predictions)))
        candidate_payload = {
            **candidate.to_dict(),
            "validation_mae": mae,
            "validation_rmse": rmse,
        }
        validation_results.append(candidate_payload)
        if (mae, rmse) < (best_mae, best_rmse):
            best_candidate = candidate
            best_mae = mae
            best_rmse = rmse

    tuned_pipeline = build_catboost_pipeline(config, best_candidate)
    tuned_pipeline.fit(combined_train_frame[feature_columns], combined_train_frame[TARGET_COLUMN])
    metadata = {
        "tuning": {
            "strategy": "validation_mae_grid_search",
            "selection_metric": "validation_mae",
            "candidate_count": len(candidates),
            "feature_columns": feature_columns,
            "rich_categorical_features_enabled": config.catboost_rich_categorical_experiments_enabled,
            "best_params": best_candidate.to_dict(),
            "best_validation_mae": best_mae,
            "best_validation_rmse": best_rmse,
            "validation_results": validation_results,
        }
    }
    return tuned_pipeline, metadata


def build_catboost_tuning_candidates(config: Goal2TrainingConfig) -> tuple[CatBoostHyperparameters, ...]:
    """Return a bounded CatBoost search set based on the roadmap candidate grid."""

    baseline = config.base_catboost_hyperparameters()
    if not config.catboost_tuning_enabled or config.catboost_iterations < 100:
        return (baseline,)

    candidates = [
        baseline,
        CatBoostHyperparameters(
            iterations=600,
            learning_rate=0.03,
            depth=6,
            l2_leaf_reg=3.0,
            bagging_temperature=0.0,
            random_strength=1.0,
        ),
        CatBoostHyperparameters(
            iterations=600,
            learning_rate=0.05,
            depth=6,
            l2_leaf_reg=5.0,
            bagging_temperature=0.5,
            random_strength=1.0,
        ),
        CatBoostHyperparameters(
            iterations=600,
            learning_rate=0.05,
            depth=8,
            l2_leaf_reg=5.0,
            bagging_temperature=0.5,
            random_strength=1.0,
        ),
        CatBoostHyperparameters(
            iterations=1000,
            learning_rate=0.03,
            depth=6,
            l2_leaf_reg=10.0,
            bagging_temperature=1.0,
            random_strength=2.0,
        ),
        CatBoostHyperparameters(
            iterations=300,
            learning_rate=0.08,
            depth=4,
            l2_leaf_reg=3.0,
            bagging_temperature=0.5,
            random_strength=0.5,
        ),
    ]
    if config.catboost_loss_experiments_enabled:
        candidates.extend(
            [
                CatBoostHyperparameters(
                    iterations=600,
                    learning_rate=0.05,
                    depth=8,
                    l2_leaf_reg=5.0,
                    bagging_temperature=0.5,
                    random_strength=1.0,
                    loss_function="RMSE",
                    eval_metric="MAE",
                ),
                CatBoostHyperparameters(
                    iterations=600,
                    learning_rate=0.05,
                    depth=8,
                    l2_leaf_reg=5.0,
                    bagging_temperature=0.5,
                    random_strength=1.0,
                    loss_function="MAE",
                    eval_metric="MAE",
                ),
                CatBoostHyperparameters(
                    iterations=600,
                    learning_rate=0.05,
                    depth=8,
                    l2_leaf_reg=5.0,
                    bagging_temperature=0.5,
                    random_strength=1.0,
                    loss_function="Huber:delta=10.0",
                    eval_metric="MAE",
                ),
            ]
        )
    if config.catboost_log_target_experiments_enabled:
        candidates.extend(
            [
                CatBoostHyperparameters(
                    iterations=600,
                    learning_rate=0.05,
                    depth=8,
                    l2_leaf_reg=5.0,
                    bagging_temperature=0.5,
                    random_strength=1.0,
                    target_transform="log1p",
                ),
                CatBoostHyperparameters(
                    iterations=1000,
                    learning_rate=0.03,
                    depth=6,
                    l2_leaf_reg=10.0,
                    bagging_temperature=1.0,
                    random_strength=2.0,
                    target_transform="log1p",
                ),
                CatBoostHyperparameters(
                    iterations=600,
                    learning_rate=0.05,
                    depth=8,
                    l2_leaf_reg=10.0,
                    bagging_temperature=0.5,
                    random_strength=2.0,
                    target_transform="log1p",
                ),
            ]
        )
    return tuple(candidates[: max(1, config.catboost_tuning_max_candidates)])


def split_feature_frame(
    feature_frame: pd.DataFrame,
    config: Goal2TrainingConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return grouped train, validation, and test splits by listing id."""

    splitter = GroupShuffleSplit(
        n_splits=1,
        train_size=config.train_size + config.validation_size,
        test_size=config.test_size,
        random_state=config.random_state,
    )
    features = feature_frame.drop(columns=[TARGET_COLUMN])
    groups = feature_frame[GROUP_COLUMN]
    train_validation_indices, test_indices = next(splitter.split(features, feature_frame[TARGET_COLUMN], groups))

    train_validation_frame = feature_frame.iloc[train_validation_indices].reset_index(drop=True)
    test_frame = feature_frame.iloc[test_indices].reset_index(drop=True)
    inner_groups = train_validation_frame[GROUP_COLUMN]
    inner_features = train_validation_frame.drop(columns=[TARGET_COLUMN])
    validation_fraction = config.validation_size / (config.train_size + config.validation_size)
    inner_splitter = GroupShuffleSplit(
        n_splits=1,
        train_size=1.0 - validation_fraction,
        test_size=validation_fraction,
        random_state=config.random_state,
    )
    train_indices, validation_indices = next(
        inner_splitter.split(inner_features, train_validation_frame[TARGET_COLUMN], inner_groups)
    )
    train_frame = train_validation_frame.iloc[train_indices].reset_index(drop=True)
    validation_frame = train_validation_frame.iloc[validation_indices].reset_index(drop=True)
    return train_frame, validation_frame, test_frame
