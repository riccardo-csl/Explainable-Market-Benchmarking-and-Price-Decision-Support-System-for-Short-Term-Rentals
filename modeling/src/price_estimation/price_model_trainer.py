"""Training orchestration for Goal 2 models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from joblib import dump
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
from feature_engineering.model_input_builder import build_model_input_table, load_goal2_source_tables
from .model_registry import build_linear_pipeline, build_tree_pipeline
from .training_config import Goal2TrainingConfig


@dataclass(frozen=True)
class Goal2TrainingResult:
    """Full Goal 2 training output."""

    feature_frame: pd.DataFrame
    train_frame: pd.DataFrame
    validation_frame: pd.DataFrame
    test_frame: pd.DataFrame
    linear_artifact: TrainedModelArtifact
    tree_artifact: TrainedModelArtifact
    comparison: ModelComparisonSummary
    linear_explanation_context: dict[str, Any]
    data_profile: dict[str, object]


def train_goal2_models(
    repo_root,
    *,
    config: Goal2TrainingConfig | None = None,
) -> Goal2TrainingResult:
    """Train Goal 2 linear and tree estimators on the canonical feature frame."""

    resolved_config = Goal2TrainingConfig() if config is None else config
    sources = load_goal2_source_tables(repo_root)
    model_input = build_model_input_table(
        sources["listing_snapshot"],
        sources["neighbourhood_reference"],
    )
    feature_frame = build_feature_frame(model_input.dataframe)
    return train_models_from_feature_frame(feature_frame, config=resolved_config)


def train_models_from_feature_frame(
    feature_frame: pd.DataFrame,
    *,
    config: Goal2TrainingConfig | None = None,
) -> Goal2TrainingResult:
    """Train Goal 2 estimators from a prepared feature frame."""

    resolved_config = Goal2TrainingConfig() if config is None else config
    feature_columns = model_feature_columns()
    leakage_findings = audit_feature_columns(feature_columns)
    if leakage_findings:
        raise ValueError(f"Leakage audit failed: {leakage_findings}")

    train_frame, validation_frame, test_frame = split_feature_frame(feature_frame, resolved_config)
    combined_train_frame = pd.concat([train_frame, validation_frame], ignore_index=True)

    linear_pipeline = build_linear_pipeline(resolved_config)
    linear_pipeline.fit(combined_train_frame[feature_columns], combined_train_frame[TARGET_COLUMN])
    tree_pipeline = build_tree_pipeline(resolved_config)
    tree_pipeline.fit(combined_train_frame[feature_columns], combined_train_frame[TARGET_COLUMN])

    linear_artifact = evaluate_trained_model(
        "linear_baseline",
        linear_pipeline,
        feature_frame,
        test_frame,
        raw_feature_columns=feature_columns,
        config=resolved_config,
    )
    tree_artifact = evaluate_trained_model(
        "tree_challenger",
        tree_pipeline,
        feature_frame,
        test_frame,
        raw_feature_columns=feature_columns,
        config=resolved_config,
    )
    comparison = choose_champion_model(linear_artifact, tree_artifact, resolved_config)
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
        comparison=comparison,
        linear_explanation_context=linear_explanation_context,
        data_profile=data_profile,
    )


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
