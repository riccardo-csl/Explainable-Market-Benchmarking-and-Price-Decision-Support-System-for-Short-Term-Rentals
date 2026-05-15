"""Stable feature lists and artifact metadata for Goal 2."""

from __future__ import annotations

TARGET_COLUMN = "nightly_price"
GROUP_COLUMN = "listing_id"

IDENTIFIER_COLUMNS = [
    "listing_id",
    "snapshot_date",
    "city_name",
    "period_label",
    "neighbourhood_name",
]

NUMERIC_MODEL_FEATURES = [
    "accommodates_count",
    "beds_count",
    "bedrooms_count",
    "bathrooms_count",
    "host_listing_count",
    "total_reviews",
    "reviews_last_twelve_months",
    "reviews_per_month",
    "rating_score",
    "accuracy_score",
    "cleanliness_score",
    "checkin_score",
    "communication_score",
    "location_score",
    "value_score",
    "latitude",
    "longitude",
    "host_tenure_days",
    "distance_to_city_center_km",
    "distance_to_neighbourhood_center_km",
]

CATEGORICAL_MODEL_FEATURES = [
    "room_type",
    "bathroom_type",
    "is_superhost",
    "season_peak_flag",
    "season_shoulder_flag",
    "venezia_group_name",
]

RICH_CATBOOST_CATEGORICAL_FEATURES = [
    "city_name",
    "period_label",
    "neighbourhood_name",
]


def model_feature_columns() -> list[str]:
    """Return the ordered raw feature columns used by Goal 2 models."""

    return [*NUMERIC_MODEL_FEATURES, *CATEGORICAL_MODEL_FEATURES]


def catboost_feature_columns(*, include_local_market_categoricals: bool = False) -> list[str]:
    """Return CatBoost feature columns, optionally including local-market categories."""

    categorical_features = list(CATEGORICAL_MODEL_FEATURES)
    if include_local_market_categoricals:
        categorical_features.extend(RICH_CATBOOST_CATEGORICAL_FEATURES)
    return [*NUMERIC_MODEL_FEATURES, *categorical_features]
