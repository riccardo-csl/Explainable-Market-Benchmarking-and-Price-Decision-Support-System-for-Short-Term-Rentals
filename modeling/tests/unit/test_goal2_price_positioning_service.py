import pandas as pd

from benchmarking.price_positioning_service import build_price_decision_payload
from explainability.local_explanation_builder import build_linear_explanation_context
from feature_engineering.feature_registry import model_feature_columns
from price_estimation.model_registry import build_linear_pipeline
from price_estimation.training_config import Goal2TrainingConfig


def test_build_price_decision_payload_is_benchmark_led() -> None:
    feature_columns = model_feature_columns()
    training_frame = pd.DataFrame(
        [
            {
                "listing_id": 1,
                "snapshot_date": "2024-03-15",
                "city_name": "Roma",
                "period_label": "Early Spring",
                "neighbourhood_name": "Centro",
                "nightly_price": 120.0,
                "accommodates_count": 2,
                "beds_count": 1,
                "bedrooms_count": 1,
                "bathrooms_count": 1.0,
                "host_listing_count": 1,
                "total_reviews": 10,
                "reviews_last_twelve_months": 4,
                "reviews_per_month": 0.3,
                "rating_score": 92.0,
                "accuracy_score": 9.0,
                "cleanliness_score": 9.0,
                "checkin_score": 9.0,
                "communication_score": 9.0,
                "location_score": 9.0,
                "value_score": 8.0,
                "latitude": 41.9,
                "longitude": 12.49,
                "host_tenure_days": 900,
                "distance_to_city_center_km": 0.8,
                "distance_to_neighbourhood_center_km": 0.2,
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "is_superhost": True,
                "season_peak_flag": True,
                "season_shoulder_flag": False,
                "venezia_group_name": None,
            },
            {
                "listing_id": 2,
                "snapshot_date": "2024-03-15",
                "city_name": "Roma",
                "period_label": "Early Spring",
                "neighbourhood_name": "Centro",
                "nightly_price": 140.0,
                "accommodates_count": 3,
                "beds_count": 2,
                "bedrooms_count": 1,
                "bathrooms_count": 1.0,
                "host_listing_count": 2,
                "total_reviews": 20,
                "reviews_last_twelve_months": 6,
                "reviews_per_month": 0.5,
                "rating_score": 95.0,
                "accuracy_score": 9.0,
                "cleanliness_score": 9.0,
                "checkin_score": 9.0,
                "communication_score": 10.0,
                "location_score": 10.0,
                "value_score": 8.0,
                "latitude": 41.901,
                "longitude": 12.491,
                "host_tenure_days": 1100,
                "distance_to_city_center_km": 0.6,
                "distance_to_neighbourhood_center_km": 0.1,
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "is_superhost": True,
                "season_peak_flag": True,
                "season_shoulder_flag": False,
                "venezia_group_name": None,
            },
            {
                "listing_id": 3,
                "snapshot_date": "2024-03-15",
                "city_name": "Roma",
                "period_label": "Early Spring",
                "neighbourhood_name": "Centro",
                "nightly_price": 160.0,
                "accommodates_count": 4,
                "beds_count": 2,
                "bedrooms_count": 2,
                "bathrooms_count": 1.0,
                "host_listing_count": 2,
                "total_reviews": 30,
                "reviews_last_twelve_months": 8,
                "reviews_per_month": 0.6,
                "rating_score": 97.0,
                "accuracy_score": 10.0,
                "cleanliness_score": 10.0,
                "checkin_score": 10.0,
                "communication_score": 10.0,
                "location_score": 10.0,
                "value_score": 9.0,
                "latitude": 41.902,
                "longitude": 12.492,
                "host_tenure_days": 1200,
                "distance_to_city_center_km": 0.5,
                "distance_to_neighbourhood_center_km": 0.1,
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "is_superhost": True,
                "season_peak_flag": True,
                "season_shoulder_flag": False,
                "venezia_group_name": None,
            },
        ]
    )
    pipeline = build_linear_pipeline(Goal2TrainingConfig())
    pipeline.fit(training_frame[feature_columns], training_frame["nightly_price"])
    explanation_context = build_linear_explanation_context(
        pipeline,
        training_frame,
        feature_columns=feature_columns,
    )

    neighbourhood_period_summary = pd.DataFrame(
        columns=["city_name", "period_label", "neighbourhood_name", "nightly_price_median", "nightly_price_mad"]
    )
    city_period_summary = pd.DataFrame(
        columns=["city_name", "period_label", "nightly_price_median", "nightly_price_mad"]
    )

    payload = build_price_decision_payload(
        feature_frame=training_frame,
        target_listing=training_frame.iloc[1],
        estimated_market_price=145.0,
        champion_model_name="linear_baseline",
        fallback_model_name="tree_challenger",
        linear_explanation_context=explanation_context,
        neighbourhood_period_summary=neighbourhood_period_summary,
        city_period_summary=city_period_summary,
    )

    assert payload["primary_decision_signal"] == "benchmark_range"
    assert payload["decision_policy"] == "benchmark_led_positioning"
    assert payload["model_estimate_role"] == "supporting_signal"
    assert "primary decision signal" in payload["decision_signal_summary"]
    assert payload["estimated_market_price"] == 145.0
