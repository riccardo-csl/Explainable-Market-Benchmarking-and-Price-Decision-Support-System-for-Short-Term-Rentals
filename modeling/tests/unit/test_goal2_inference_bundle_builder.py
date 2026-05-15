from pathlib import Path

import pandas as pd

from price_estimation.inference_bundle_builder import build_inference_bundle, load_inference_bundle
from price_estimation.price_model_trainer import train_models_from_feature_frame
from price_estimation.training_config import Goal2TrainingConfig


def test_build_inference_bundle_serializes_and_loads_models(tmp_path: Path) -> None:
    rows = []
    for listing_id in range(1, 81):
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
    feature_frame = pd.DataFrame(rows)
    training_result = train_models_from_feature_frame(
        feature_frame,
        config=Goal2TrainingConfig(
            tree_max_iter=50,
            catboost_iterations=25,
            catboost_rich_categorical_experiments_enabled=True,
        ),
    )

    paths = build_inference_bundle(training_result, tmp_path, bundle_version="test_bundle")
    bundle = load_inference_bundle(paths["bundle"])

    assert paths["bundle"].exists()
    assert bundle["champion_model_name"] in {"linear_baseline", "tree_challenger", "catboost_challenger"}
    assert "catboost_challenger" in bundle["available_model_names"]
    assert len(bundle["feature_columns"]) > 0
    assert "neighbourhood_name" in bundle["feature_columns_by_model"]["catboost_challenger"]
    assert bundle["model_estimate_interval_calibration"]["source"] == "heldout_residual_quantiles"
    assert bundle["model_estimate_interval_calibration"]["confidence_level"] == 0.8
