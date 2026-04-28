"""Training configuration and typed results for Goal 2."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


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
    importance_sample_size: int = 1000
    champion_mae_improvement_threshold: float = 0.05


@dataclass(frozen=True)
class ModelEvaluationResult:
    """Evaluation result for one trained model."""

    model_name: str
    mae: float
    rmse: float
    per_city_mae: dict[str, float]
    per_period_mae: dict[str, float]
    price_band_mae: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
