import pandas as pd

from feature_engineering.feature_registry import catboost_feature_columns
from price_estimation.model_registry import build_catboost_pipeline
from price_estimation.price_model_trainer import (
    build_catboost_tuning_candidates,
    train_models_from_feature_frame,
)
from price_estimation.training_config import Goal2TrainingConfig


def test_catboost_pipeline_preserves_categorical_feature_support() -> None:
    feature_frame = _feature_frame(row_count=40)
    feature_columns = [column for column in feature_frame.columns if column not in {"listing_id", "snapshot_date", "city_name", "period_label", "neighbourhood_name", "nightly_price"}]
    pipeline = build_catboost_pipeline(Goal2TrainingConfig(catboost_iterations=5))

    pipeline.fit(feature_frame[feature_columns], feature_frame["nightly_price"])
    predictions = pipeline.predict(feature_frame[feature_columns].head(3))

    assert len(predictions) == 3


def test_catboost_pipeline_supports_rich_categorical_features_and_unseen_values() -> None:
    feature_frame = _feature_frame(row_count=40)
    feature_columns = catboost_feature_columns(include_local_market_categoricals=True)
    pipeline = build_catboost_pipeline(
        Goal2TrainingConfig(
            catboost_iterations=5,
            catboost_rich_categorical_experiments_enabled=True,
        )
    )

    pipeline.fit(feature_frame[feature_columns], feature_frame["nightly_price"])
    unseen_listing = feature_frame[feature_columns].head(1).copy()
    unseen_listing["city_name"] = "Torino"
    unseen_listing["period_label"] = "Late Winter"
    unseen_listing["neighbourhood_name"] = "Unseen District"

    predictions = pipeline.predict(unseen_listing)

    assert len(predictions) == 1


def test_training_result_includes_catboost_challenger_evaluation() -> None:
    training_result = train_models_from_feature_frame(
        _feature_frame(row_count=90),
        config=Goal2TrainingConfig(
            tree_max_iter=10,
            catboost_iterations=10,
            importance_sample_size=20,
        ),
    )

    assert training_result.catboost_artifact.model_name == "catboost_challenger"
    assert "catboost_challenger" in training_result.comparison.evaluations
    assert "Entire home" in training_result.catboost_artifact.evaluation.per_room_type_mae
    assert training_result.catboost_artifact.evaluation.mape is not None
    assert {artifact.model_name for artifact in training_result.model_artifacts} == {
        "linear_baseline",
        "tree_challenger",
        "catboost_challenger",
    }
    assert training_result.catboost_artifact.evaluation.metadata["tuning"]["candidate_count"] == 1


def test_catboost_tuning_candidates_use_roadmap_grid_when_iterations_are_realistic() -> None:
    candidates = build_catboost_tuning_candidates(
        Goal2TrainingConfig(catboost_iterations=300, catboost_tuning_max_candidates=3)
    )

    assert len(candidates) == 3
    assert candidates[0].iterations == 300
    assert candidates[1].learning_rate == 0.03
    assert candidates[2].bagging_temperature == 0.5


def test_catboost_tuning_candidates_include_phase_two_loss_experiments() -> None:
    candidates = build_catboost_tuning_candidates(
        Goal2TrainingConfig(
            catboost_iterations=300,
            catboost_loss_experiments_enabled=True,
            catboost_tuning_max_candidates=9,
        )
    )

    losses = {(candidate.loss_function, candidate.eval_metric) for candidate in candidates}

    assert ("RMSE", "MAE") in losses
    assert ("MAE", "MAE") in losses
    assert ("Huber:delta=10.0", "MAE") in losses


def test_catboost_tuning_candidates_include_phase_three_log_target_experiments() -> None:
    candidates = build_catboost_tuning_candidates(
        Goal2TrainingConfig(
            catboost_iterations=300,
            catboost_log_target_experiments_enabled=True,
            catboost_tuning_max_candidates=9,
        )
    )

    assert any(candidate.target_transform == "log1p" for candidate in candidates)


def test_training_result_can_include_rich_catboost_feature_columns() -> None:
    training_result = train_models_from_feature_frame(
        _feature_frame(row_count=90),
        config=Goal2TrainingConfig(
            tree_max_iter=10,
            catboost_iterations=10,
            importance_sample_size=20,
            catboost_rich_categorical_experiments_enabled=True,
        ),
    )

    assert "city_name" in training_result.catboost_artifact.raw_feature_columns
    assert "period_label" in training_result.catboost_artifact.raw_feature_columns
    assert "neighbourhood_name" in training_result.catboost_artifact.raw_feature_columns
    assert "city_name" not in training_result.linear_artifact.raw_feature_columns


def _feature_frame(*, row_count: int) -> pd.DataFrame:
    rows = []
    for listing_id in range(1, row_count + 1):
        rows.append(
            {
                "listing_id": listing_id,
                "snapshot_date": "2024-06-15",
                "city_name": "Roma" if listing_id % 2 else "Milano",
                "period_label": "Early Summer",
                "neighbourhood_name": "Centro" if listing_id % 3 else "Navigli",
                "nightly_price": float(80 + listing_id * 2),
                "accommodates_count": 1 + (listing_id % 4),
                "beds_count": 1 + (listing_id % 3),
                "bedrooms_count": 1 + (listing_id % 2),
                "bathrooms_count": 1.0,
                "host_listing_count": 1 + (listing_id % 5),
                "total_reviews": 10 + listing_id,
                "reviews_last_twelve_months": 2 + (listing_id % 4),
                "reviews_per_month": 0.2 + (listing_id % 5) * 0.1,
                "rating_score": 85.0 + (listing_id % 10),
                "accuracy_score": 8.0 + (listing_id % 3),
                "cleanliness_score": 8.0 + (listing_id % 2),
                "checkin_score": 8.0 + (listing_id % 3),
                "communication_score": 8.0 + (listing_id % 3),
                "location_score": 8.0 + (listing_id % 3),
                "value_score": 7.0 + (listing_id % 3),
                "latitude": 41.8 + listing_id * 0.001,
                "longitude": 12.4 + listing_id * 0.001,
                "host_tenure_days": 300 + listing_id,
                "distance_to_city_center_km": 0.2 + (listing_id % 6) * 0.3,
                "distance_to_neighbourhood_center_km": 0.1 + (listing_id % 4) * 0.1,
                "room_type": "Entire home" if listing_id % 4 else "Private room",
                "bathroom_type": "Private bath",
                "is_superhost": bool(listing_id % 2),
                "season_peak_flag": True,
                "season_shoulder_flag": False,
                "venezia_group_name": None,
            }
        )
    return pd.DataFrame(rows)
