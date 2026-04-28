import pandas as pd

from explainability.local_explanation_builder import (
    _display_name_for_contribution,
    build_linear_explanation_context,
    build_local_explanation_payload,
)
from feature_engineering.feature_registry import model_feature_columns
from price_estimation.model_registry import build_linear_pipeline
from price_estimation.training_config import Goal2TrainingConfig


def test_build_local_explanation_payload_returns_ranked_driver_lists() -> None:
    feature_columns = model_feature_columns()
    training_frame = pd.DataFrame(
        [
            {
                "accommodates_count": 2,
                "beds_count": 1,
                "bedrooms_count": 1,
                "bathrooms_count": 1.0,
                "host_listing_count": 1,
                "total_reviews": 20,
                "reviews_last_twelve_months": 4,
                "reviews_per_month": 0.3,
                "rating_score": 94.0,
                "accuracy_score": 9.0,
                "cleanliness_score": 9.0,
                "checkin_score": 9.0,
                "communication_score": 9.0,
                "location_score": 9.0,
                "value_score": 8.0,
                "latitude": 41.9,
                "longitude": 12.49,
                "host_tenure_days": 1000,
                "distance_to_city_center_km": 1.0,
                "distance_to_neighbourhood_center_km": 0.2,
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "is_superhost": True,
                "season_peak_flag": True,
                "season_shoulder_flag": False,
                "venezia_group_name": None,
                "nightly_price": 120.0,
            },
            {
                "accommodates_count": 4,
                "beds_count": 2,
                "bedrooms_count": 2,
                "bathrooms_count": 1.0,
                "host_listing_count": 3,
                "total_reviews": 40,
                "reviews_last_twelve_months": 6,
                "reviews_per_month": 0.5,
                "rating_score": 98.0,
                "accuracy_score": 10.0,
                "cleanliness_score": 10.0,
                "checkin_score": 10.0,
                "communication_score": 10.0,
                "location_score": 10.0,
                "value_score": 9.0,
                "latitude": 41.91,
                "longitude": 12.48,
                "host_tenure_days": 1500,
                "distance_to_city_center_km": 0.4,
                "distance_to_neighbourhood_center_km": 0.1,
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "is_superhost": True,
                "season_peak_flag": True,
                "season_shoulder_flag": False,
                "venezia_group_name": None,
                "nightly_price": 190.0,
            },
            {
                "accommodates_count": 1,
                "beds_count": 1,
                "bedrooms_count": 1,
                "bathrooms_count": 1.0,
                "host_listing_count": 1,
                "total_reviews": 5,
                "reviews_last_twelve_months": 2,
                "reviews_per_month": 0.1,
                "rating_score": 85.0,
                "accuracy_score": 8.0,
                "cleanliness_score": 8.0,
                "checkin_score": 8.0,
                "communication_score": 8.0,
                "location_score": 8.0,
                "value_score": 7.0,
                "latitude": 41.88,
                "longitude": 12.52,
                "host_tenure_days": 500,
                "distance_to_city_center_km": 2.0,
                "distance_to_neighbourhood_center_km": 0.8,
                "room_type": "Private room",
                "bathroom_type": "Shared bath",
                "is_superhost": False,
                "season_peak_flag": False,
                "season_shoulder_flag": True,
                "venezia_group_name": None,
                "nightly_price": 75.0,
            },
        ]
    )
    pipeline = build_linear_pipeline(Goal2TrainingConfig())
    pipeline.fit(training_frame[feature_columns], training_frame["nightly_price"])
    context = build_linear_explanation_context(
        pipeline,
        training_frame,
        feature_columns=feature_columns,
    )

    payload = build_local_explanation_payload(
        target_listing=training_frame.iloc[1],
        comparables=pd.DataFrame({"nightly_price": [120.0, 140.0, 160.0]}),
        explanation_context=context,
    )

    assert payload["source_model_name"] == "linear_baseline"
    assert len(payload["top_upward_drivers"]) > 0
    assert "feature" in payload["top_upward_drivers"][0]


def test_build_local_explanation_payload_hides_venezia_feature_for_non_venezia_listing() -> None:
    feature_columns = model_feature_columns()
    training_frame = pd.DataFrame(
        [
            {
                "accommodates_count": 2,
                "beds_count": 1,
                "bedrooms_count": 1,
                "bathrooms_count": 1.0,
                "host_listing_count": 1,
                "total_reviews": 20,
                "reviews_last_twelve_months": 4,
                "reviews_per_month": 0.3,
                "rating_score": 94.0,
                "accuracy_score": 9.0,
                "cleanliness_score": 9.0,
                "checkin_score": 9.0,
                "communication_score": 9.0,
                "location_score": 9.0,
                "value_score": 8.0,
                "latitude": 41.9,
                "longitude": 12.49,
                "host_tenure_days": 1000,
                "distance_to_city_center_km": 1.0,
                "distance_to_neighbourhood_center_km": 0.2,
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "is_superhost": True,
                "season_peak_flag": True,
                "season_shoulder_flag": False,
                "venezia_group_name": None,
                "nightly_price": 120.0,
            },
            {
                "accommodates_count": 4,
                "beds_count": 2,
                "bedrooms_count": 2,
                "bathrooms_count": 1.0,
                "host_listing_count": 3,
                "total_reviews": 40,
                "reviews_last_twelve_months": 6,
                "reviews_per_month": 0.5,
                "rating_score": 98.0,
                "accuracy_score": 10.0,
                "cleanliness_score": 10.0,
                "checkin_score": 10.0,
                "communication_score": 10.0,
                "location_score": 10.0,
                "value_score": 9.0,
                "latitude": 41.91,
                "longitude": 12.48,
                "host_tenure_days": 1500,
                "distance_to_city_center_km": 0.4,
                "distance_to_neighbourhood_center_km": 0.1,
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "is_superhost": True,
                "season_peak_flag": True,
                "season_shoulder_flag": False,
                "venezia_group_name": None,
                "nightly_price": 190.0,
            },
            {
                "accommodates_count": 3,
                "beds_count": 2,
                "bedrooms_count": 1,
                "bathrooms_count": 1.0,
                "host_listing_count": 2,
                "total_reviews": 18,
                "reviews_last_twelve_months": 3,
                "reviews_per_month": 0.3,
                "rating_score": 92.0,
                "accuracy_score": 9.0,
                "cleanliness_score": 9.0,
                "checkin_score": 9.0,
                "communication_score": 9.0,
                "location_score": 9.0,
                "value_score": 8.0,
                "latitude": 45.44,
                "longitude": 12.33,
                "host_tenure_days": 900,
                "distance_to_city_center_km": 0.8,
                "distance_to_neighbourhood_center_km": 0.2,
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "is_superhost": True,
                "season_peak_flag": True,
                "season_shoulder_flag": False,
                "venezia_group_name": "Lagoon North",
                "nightly_price": 170.0,
            },
        ]
    )
    pipeline = build_linear_pipeline(Goal2TrainingConfig())
    pipeline.fit(training_frame[feature_columns], training_frame["nightly_price"])
    context = build_linear_explanation_context(
        pipeline,
        training_frame,
        feature_columns=feature_columns,
    )

    roma_listing = training_frame.iloc[1].copy()
    roma_listing["city_name"] = "Roma"
    payload = build_local_explanation_payload(
        target_listing=roma_listing,
        comparables=pd.DataFrame({"nightly_price": [120.0, 140.0, 160.0]}),
        explanation_context=context,
    )
    features = {
        item["feature"] for item in payload["top_upward_drivers"] + payload["top_downward_drivers"]
    }

    assert "venezia_group_name" not in features
    assert not any(feature.startswith("venezia_zone=") for feature in features)


def test_display_name_for_contribution_groups_location_signals() -> None:
    target_listing = pd.Series(
        {
            "city_name": "Roma",
        }
    )

    assert (
        _display_name_for_contribution(
            feature_name="numeric__latitude",
            transformed_value=1.0,
            target_listing=target_listing,
        )
        == "location"
    )
    assert (
        _display_name_for_contribution(
            feature_name="numeric__distance_to_city_center_km",
            transformed_value=1.0,
            target_listing=target_listing,
        )
        == "location"
    )
