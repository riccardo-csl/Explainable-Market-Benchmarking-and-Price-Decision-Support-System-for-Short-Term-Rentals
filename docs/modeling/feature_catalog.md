# Goal 2 Feature Catalog

This document summarizes the reusable feature set currently produced for Goal 2.

## Structural Features

- `accommodates_count`
- `beds_count`
- `bedrooms_count`
- `bathrooms_count`
- `room_type`
- `bathroom_type`

## Host and Review Features

- `host_listing_count`
- `is_superhost`
- `total_reviews`
- `reviews_last_twelve_months`
- `reviews_per_month`
- `rating_score`
- `accuracy_score`
- `cleanliness_score`
- `checkin_score`
- `communication_score`
- `location_score`
- `value_score`
- `host_tenure_days`

## Temporal Features

- `season_peak_flag`
- `season_shoulder_flag`

## Location Features

- `latitude`
- `longitude`
- `distance_to_city_center_km`
- `distance_to_neighbourhood_center_km`

## Conditional Features

- `venezia_group_name`

## Notes

- `neighbourhood_name` is retained for comparable selection and payload context, but not used as a model predictor in the v1 estimators.
- grouped summary price statistics are reserved for benchmark fallback logic, not for supervised training.
