"""Model factory functions for Goal 2 estimators."""

from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from feature_engineering.feature_registry import CATEGORICAL_MODEL_FEATURES, NUMERIC_MODEL_FEATURES
from .training_config import Goal2TrainingConfig


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
