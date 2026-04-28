import pandas as pd

from feature_engineering.feature_matrix_builder import build_feature_frame


def test_build_feature_frame_adds_distance_features_without_duplicate_listing_column() -> None:
    model_input = pd.DataFrame(
        [
            {
                "listing_id": 1,
                "snapshot_date": "2024-06-15",
                "city_name": "Roma",
                "period_label": "Early Summer",
                "neighbourhood_name": "Centro",
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "nightly_price": 120.0,
                "accommodates_count": 2,
                "beds_count": 1,
                "bedrooms_count": 1,
                "bathrooms_count": 1.0,
                "host_listing_count": 1,
                "total_reviews": 20,
                "reviews_last_twelve_months": 5,
                "reviews_per_month": 0.5,
                "rating_score": 95.0,
                "accuracy_score": 9.0,
                "cleanliness_score": 9.0,
                "checkin_score": 9.0,
                "communication_score": 9.0,
                "location_score": 10.0,
                "value_score": 8.0,
                "latitude": 41.9,
                "longitude": 12.49,
                "host_tenure_days": 1000,
                "is_superhost": True,
                "season_peak_flag": True,
                "season_shoulder_flag": False,
                "venezia_group_name": None,
            },
            {
                "listing_id": 2,
                "snapshot_date": "2024-06-15",
                "city_name": "Roma",
                "period_label": "Early Summer",
                "neighbourhood_name": "Centro",
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "nightly_price": 140.0,
                "accommodates_count": 3,
                "beds_count": 2,
                "bedrooms_count": 1,
                "bathrooms_count": 1.0,
                "host_listing_count": 2,
                "total_reviews": 30,
                "reviews_last_twelve_months": 6,
                "reviews_per_month": 0.6,
                "rating_score": 97.0,
                "accuracy_score": 10.0,
                "cleanliness_score": 9.0,
                "checkin_score": 10.0,
                "communication_score": 10.0,
                "location_score": 9.0,
                "value_score": 9.0,
                "latitude": 41.91,
                "longitude": 12.50,
                "host_tenure_days": 1200,
                "is_superhost": False,
                "season_peak_flag": True,
                "season_shoulder_flag": False,
                "venezia_group_name": None,
            },
        ]
    )

    feature_frame = build_feature_frame(model_input)

    assert list(feature_frame.columns).count("listing_id") == 1
    assert "distance_to_city_center_km" in feature_frame.columns
    assert "distance_to_neighbourhood_center_km" in feature_frame.columns
    assert (feature_frame["distance_to_city_center_km"] >= 0).all()
