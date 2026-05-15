from evaluation.model_comparison_report import (
    TrainedModelArtifact,
    choose_champion_model,
)
from price_estimation.training_config import Goal2TrainingConfig, ModelEvaluationResult


def test_catboost_can_become_champion_when_it_improves_mae_and_city_stability() -> None:
    linear = _artifact(
        "linear_baseline",
        mae=100.0,
        per_city_mae={"Roma": 95.0, "Milano": 105.0},
    )
    tree = _artifact(
        "tree_challenger",
        mae=98.0,
        per_city_mae={"Roma": 90.0, "Milano": 108.0},
    )
    catboost = _artifact(
        "catboost_challenger",
        mae=88.0,
        per_city_mae={"Roma": 84.0, "Milano": 94.0},
    )

    comparison = choose_champion_model(
        linear,
        tree,
        catboost,
        config=Goal2TrainingConfig(champion_mae_improvement_threshold=0.05),
    )

    assert comparison.champion_model_name == "catboost_challenger"
    assert comparison.fallback_model_name == "linear_baseline"
    assert set(comparison.evaluations) == {
        "linear_baseline",
        "tree_challenger",
        "catboost_challenger",
    }


def test_challenger_is_rejected_when_city_stability_worsens_too_much() -> None:
    linear = _artifact(
        "linear_baseline",
        mae=100.0,
        per_city_mae={"Roma": 95.0, "Milano": 105.0},
    )
    catboost = _artifact(
        "catboost_challenger",
        mae=80.0,
        per_city_mae={"Roma": 55.0, "Milano": 125.0},
    )

    comparison = choose_champion_model(
        linear,
        catboost,
        config=Goal2TrainingConfig(champion_mae_improvement_threshold=0.05),
    )

    assert comparison.champion_model_name == "linear_baseline"
    assert comparison.fallback_model_name == "catboost_challenger"


def _artifact(
    model_name: str,
    *,
    mae: float,
    per_city_mae: dict[str, float],
) -> TrainedModelArtifact:
    evaluation = ModelEvaluationResult(
        model_name=model_name,
        mae=mae,
        rmse=mae * 2,
        per_city_mae=per_city_mae,
        per_period_mae={"Early Summer": mae},
        per_room_type_mae={"Entire home": mae},
        price_band_mae={"middle": mae},
        mape=mae,
    )
    return TrainedModelArtifact(
        model_name=model_name,
        pipeline=None,
        evaluation=evaluation,
        feature_importances={},
        raw_feature_columns=[],
    )
