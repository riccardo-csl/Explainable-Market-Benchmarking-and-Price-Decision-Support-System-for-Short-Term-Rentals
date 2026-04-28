import pandas as pd

from price_estimation.price_model_trainer import split_feature_frame
from price_estimation.training_config import Goal2TrainingConfig


def test_split_feature_frame_keeps_listing_groups_isolated() -> None:
    rows = []
    for listing_id in range(1, 41):
        for snapshot_index in range(2):
            rows.append(
                {
                    "listing_id": listing_id,
                    "snapshot_date": f"2024-0{snapshot_index + 6}-15",
                    "city_name": "Roma" if listing_id % 2 else "Milano",
                    "period_label": "Early Summer" if snapshot_index == 0 else "Early Autumn",
                    "neighbourhood_name": "Centro",
                    "nightly_price": float(100 + listing_id),
                    "accommodates_count": 2,
                    "beds_count": 1,
                    "bedrooms_count": 1,
                    "bathrooms_count": 1.0,
                    "host_listing_count": 1,
                    "total_reviews": 10,
                    "reviews_last_twelve_months": 2,
                    "reviews_per_month": 0.2,
                    "rating_score": 90.0,
                    "accuracy_score": 9.0,
                    "cleanliness_score": 9.0,
                    "checkin_score": 9.0,
                    "communication_score": 9.0,
                    "location_score": 9.0,
                    "value_score": 8.0,
                    "latitude": 41.9,
                    "longitude": 12.49,
                    "host_tenure_days": 500,
                    "distance_to_city_center_km": 1.0,
                    "distance_to_neighbourhood_center_km": 0.3,
                    "room_type": "Entire home",
                    "bathroom_type": "Private bath",
                    "is_superhost": True,
                    "season_peak_flag": True,
                    "season_shoulder_flag": False,
                    "venezia_group_name": None,
                }
            )
    feature_frame = pd.DataFrame(rows)

    train_frame, validation_frame, test_frame = split_feature_frame(
        feature_frame,
        Goal2TrainingConfig(),
    )

    assert not train_frame["listing_id"].isin(test_frame["listing_id"]).any()
    assert not train_frame["listing_id"].isin(validation_frame["listing_id"]).any()
    assert not validation_frame["listing_id"].isin(test_frame["listing_id"]).any()
