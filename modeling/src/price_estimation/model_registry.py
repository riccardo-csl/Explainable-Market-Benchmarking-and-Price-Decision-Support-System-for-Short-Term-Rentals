"""Model factory functions for Goal 2 estimators."""

from __future__ import annotations

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from feature_engineering.feature_registry import (
    CATEGORICAL_MODEL_FEATURES,
    NUMERIC_MODEL_FEATURES,
    RICH_CATBOOST_CATEGORICAL_FEATURES,
)
from .training_config import CatBoostHyperparameters, Goal2TrainingConfig


class CatBoostFeaturePreprocessor(BaseEstimator, TransformerMixin):
    """Prepare raw Goal 2 features while preserving DataFrame columns for CatBoost."""

    def __init__(
        self,
        numeric_features: tuple[str, ...] = tuple(NUMERIC_MODEL_FEATURES),
        categorical_features: tuple[str, ...] = tuple(CATEGORICAL_MODEL_FEATURES),
    ) -> None:
        self.numeric_features = numeric_features
        self.categorical_features = categorical_features
        self.numeric_medians_: dict[str, float] = {}

    def fit(self, X: pd.DataFrame, y=None):  # noqa: ANN001
        frame = pd.DataFrame(X).copy()
        self.numeric_medians_ = {
            feature_name: float(frame[feature_name].median())
            for feature_name in self.numeric_features
        }
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        frame = pd.DataFrame(X).copy()
        for feature_name in self.numeric_features:
            frame[feature_name] = pd.to_numeric(frame[feature_name], errors="coerce").fillna(
                self.numeric_medians_[feature_name]
            )
        for feature_name in self.categorical_features:
            frame[feature_name] = frame[feature_name].astype("object").where(
                frame[feature_name].notna(),
                "__missing__",
            )
            frame[feature_name] = frame[feature_name].astype(str)
        return frame[[*self.numeric_features, *self.categorical_features]]


def build_linear_pipeline(config: Goal2TrainingConfig) -> Pipeline:
    """Return the regularized linear baseline pipeline."""

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_MODEL_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_MODEL_FEATURES),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            (
                "model",
                ElasticNet(
                    alpha=config.linear_alpha,
                    l1_ratio=config.linear_l1_ratio,
                    random_state=config.random_state,
                    max_iter=5000,
                ),
            ),
        ]
    )


def build_tree_pipeline(config: Goal2TrainingConfig) -> Pipeline:
    """Return the non-linear challenger pipeline."""

    numeric_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median"))]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_MODEL_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_MODEL_FEATURES),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            (
                "model",
                HistGradientBoostingRegressor(
                    learning_rate=config.tree_learning_rate,
                    max_depth=config.tree_max_depth,
                    max_iter=config.tree_max_iter,
                    random_state=config.random_state,
                ),
            ),
        ]
    )


def build_catboost_pipeline(
    config: Goal2TrainingConfig,
    hyperparameters: CatBoostHyperparameters | None = None,
) -> Pipeline | TransformedTargetRegressor:
    """Return the categorical-aware gradient boosting challenger pipeline."""

    resolved_hyperparameters = config.base_catboost_hyperparameters() if hyperparameters is None else hyperparameters
    categorical_features = list(CATEGORICAL_MODEL_FEATURES)
    if config.catboost_rich_categorical_experiments_enabled:
        categorical_features.extend(RICH_CATBOOST_CATEGORICAL_FEATURES)
    model_parameters = {
        "iterations": resolved_hyperparameters.iterations,
        "learning_rate": resolved_hyperparameters.learning_rate,
        "depth": resolved_hyperparameters.depth,
        "l2_leaf_reg": resolved_hyperparameters.l2_leaf_reg,
        "bagging_temperature": resolved_hyperparameters.bagging_temperature,
        "random_strength": resolved_hyperparameters.random_strength,
        "loss_function": resolved_hyperparameters.loss_function,
        "random_seed": config.random_state,
        "cat_features": categorical_features,
        "allow_writing_files": False,
        "verbose": False,
    }
    if resolved_hyperparameters.eval_metric is not None:
        model_parameters["eval_metric"] = resolved_hyperparameters.eval_metric

    pipeline = Pipeline(
        steps=[
            (
                "preprocess",
                CatBoostFeaturePreprocessor(
                    numeric_features=tuple(NUMERIC_MODEL_FEATURES),
                    categorical_features=tuple(categorical_features),
                ),
            ),
            (
                "model",
                CatBoostRegressor(**model_parameters),
            ),
        ]
    )
    if resolved_hyperparameters.target_transform == "log1p":
        return TransformedTargetRegressor(
            regressor=pipeline,
            func=np.log1p,
            inverse_func=np.expm1,
            check_inverse=False,
        )
    if resolved_hyperparameters.target_transform != "raw":
        raise ValueError(f"Unsupported CatBoost target transform: {resolved_hyperparameters.target_transform}")
    return pipeline
