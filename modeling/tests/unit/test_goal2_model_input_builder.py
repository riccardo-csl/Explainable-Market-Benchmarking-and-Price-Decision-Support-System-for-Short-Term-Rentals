from datetime import datetime

import pandas as pd

from feature_engineering.model_input_builder import build_model_input_table


def test_build_model_input_table_adds_goal2_fields_and_metadata() -> None:
    listing_snapshot = pd.DataFrame(
        [
            {
                "listing_id": 10,
                "snapshot_date": datetime(2024, 6, 15),
                "host_since": datetime(2020, 6, 15),
                "city_name": "Venezia",
                "period_label": "Early Summer",
                "neighbourhood_name": "Cannaregio",
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "nightly_price": 180.0,
                "accommodates_count": 4,
                "beds_count": 2,
                "bedrooms_count": 1,
                "bathrooms_count": 1.0,
                "host_listing_count": 3,
                "total_reviews": 12,
                "reviews_last_twelve_months": 4,
                "reviews_per_month": 0.4,
                "rating_score": 96.0,
                "accuracy_score": 9.0,
                "cleanliness_score": 9.0,
                "checkin_score": 10.0,
                "communication_score": 10.0,
                "location_score": 9.0,
                "value_score": 8.0,
                "latitude": 45.443,
                "longitude": 12.329,
                "is_superhost": True,
            }
        ]
    )
    neighbourhood_reference = pd.DataFrame(
        [
            {
                "city_name": "Venezia",
                "neighbourhood_name": "Cannaregio",
                "neighbourhood_group_name": "Lagoon North",
            }
        ]
    )

    artifact = build_model_input_table(listing_snapshot, neighbourhood_reference)

    assert artifact.dataframe.loc[0, "neighbourhood_group_name"] == "Lagoon North"
    assert artifact.dataframe.loc[0, "venezia_group_name"] == "Lagoon North"
    assert artifact.dataframe.loc[0, "host_tenure_days"] == 1461
    assert bool(artifact.dataframe.loc[0, "season_peak_flag"]) is True
    assert artifact.metadata["group_column"] == "listing_id"
    assert "neighbourhood_name" in artifact.metadata["excluded_training_columns"]


def test_build_model_input_table_filters_impossible_price_outliers() -> None:
    listing_snapshot = pd.DataFrame(
        [
            {
                "listing_id": 10,
                "snapshot_date": datetime(2024, 6, 15),
                "host_since": datetime(2020, 6, 15),
                "city_name": "Roma",
                "period_label": "Early Summer",
                "neighbourhood_name": "Centro",
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "nightly_price": 180.0,
                "accommodates_count": 4,
                "beds_count": 2,
                "bedrooms_count": 1,
                "bathrooms_count": 1.0,
                "host_listing_count": 3,
                "total_reviews": 12,
                "reviews_last_twelve_months": 4,
                "reviews_per_month": 0.4,
                "rating_score": 96.0,
                "accuracy_score": 9.0,
                "cleanliness_score": 9.0,
                "checkin_score": 10.0,
                "communication_score": 10.0,
                "location_score": 9.0,
                "value_score": 8.0,
                "latitude": 41.9,
                "longitude": 12.5,
                "is_superhost": True,
            },
            {
                "listing_id": 11,
                "snapshot_date": datetime(2024, 6, 15),
                "host_since": datetime(2020, 6, 15),
                "city_name": "Roma",
                "period_label": "Early Summer",
                "neighbourhood_name": "Centro",
                "room_type": "Entire home",
                "bathroom_type": "Private bath",
                "nightly_price": 50000.0,
                "accommodates_count": 4,
                "beds_count": 2,
                "bedrooms_count": 1,
                "bathrooms_count": 1.0,
                "host_listing_count": 3,
                "total_reviews": 12,
                "reviews_last_twelve_months": 4,
                "reviews_per_month": 0.4,
                "rating_score": 96.0,
                "accuracy_score": 9.0,
                "cleanliness_score": 9.0,
                "checkin_score": 10.0,
                "communication_score": 10.0,
                "location_score": 9.0,
                "value_score": 8.0,
                "latitude": 41.9,
                "longitude": 12.5,
                "is_superhost": True,
            },
        ]
    )
    neighbourhood_reference = pd.DataFrame(
        [
            {
                "city_name": "Roma",
                "neighbourhood_name": "Centro",
                "neighbourhood_group_name": None,
            }
        ]
    )

    artifact = build_model_input_table(listing_snapshot, neighbourhood_reference)

    assert len(artifact.dataframe) == 1
    assert artifact.dataframe.iloc[0]["listing_id"] == 10
    assert artifact.metadata["rows_removed_for_impossible_price_outliers"] == 1
    assert artifact.metadata["impossible_price_threshold"] == 10000.0
