"""Training configuration and typed results for Goal 2."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class CatBoostHyperparameters:
    """CatBoost parameters evaluated during validation tuning."""

    iterations: int
    learning_rate: float
    depth: int
    l2_leaf_reg: float
    bagging_temperature: float
    random_strength: float
    loss_function: str = "RMSE"
    eval_metric: str | None = None
    target_transform: str = "raw"

    def to_dict(self) -> dict[str, int | float | str | None]:
        return asdict(self)


@dataclass(frozen=True)
class Goal2TrainingConfig:
    """Frozen training configuration for Goal 2."""

    random_state: int = 42
    train_size: float = 0.70
    validation_size: float = 0.15
    test_size: float = 0.15
    linear_alpha: float = 0.001
    linear_l1_ratio: float = 0.3
    tree_learning_rate: float = 0.05
    tree_max_depth: int = 6
    tree_max_iter: int = 250
    catboost_learning_rate: float = 0.05
    catboost_depth: int = 6
    catboost_iterations: int = 300
    catboost_l2_leaf_reg: float = 3.0
    catboost_bagging_temperature: float = 0.0
    catboost_random_strength: float = 1.0
    catboost_loss_function: str = "RMSE"
    catboost_eval_metric: str | None = None
    catboost_tuning_enabled: bool = True
    catboost_loss_experiments_enabled: bool = False
    catboost_log_target_experiments_enabled: bool = False
    catboost_rich_categorical_experiments_enabled: bool = False
    catboost_tuning_max_candidates: int = 6
    importance_sample_size: int = 1000
    benchmark_diagnostic_sample_size: int = 250
    prediction_interval_confidence_level: float = 0.80
    champion_mae_improvement_threshold: float = 0.05
    champion_city_mae_regression_tolerance: float = 0.10

    def base_catboost_hyperparameters(self) -> CatBoostHyperparameters:
        """Return the configured CatBoost baseline candidate."""

        return CatBoostHyperparameters(
            iterations=self.catboost_iterations,
            learning_rate=self.catboost_learning_rate,
            depth=self.catboost_depth,
            l2_leaf_reg=self.catboost_l2_leaf_reg,
            bagging_temperature=self.catboost_bagging_temperature,
            random_strength=self.catboost_random_strength,
            loss_function=self.catboost_loss_function,
            eval_metric=self.catboost_eval_metric,
        )


@dataclass(frozen=True)
class ModelEvaluationResult:
    """Evaluation result for one trained model."""

    model_name: str
    mae: float
    rmse: float
    per_city_mae: dict[str, float]
    per_period_mae: dict[str, float]
    per_room_type_mae: dict[str, float]
    price_band_mae: dict[str, float]
    mape: float | None
    benchmark_positioning_mae: dict[str, float] = field(default_factory=dict)
    model_prediction_inside_benchmark_rate: float | None = None
    model_positioning_agreement_rate: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
