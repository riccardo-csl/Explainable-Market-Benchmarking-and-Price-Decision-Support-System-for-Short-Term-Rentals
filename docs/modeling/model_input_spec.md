# Goal 2 Model Input Spec

The Goal 2 model input table is the canonical listing-level dataset used by feature engineering, comparable selection, and training.

## Source Tables

- `listing_snapshot`
- `neighbourhood_reference`

## Grain

One row per `(listing_id, snapshot_date)`.

## Added Goal 2 Fields

- `neighbourhood_group_name`
  - joined from `neighbourhood_reference`
- `venezia_group_name`
  - city-conditional version of `neighbourhood_group_name`
  - populated only when `city_name == Venezia`
- `host_tenure_days`
  - derived as `snapshot_date - host_since`
- `season_peak_flag`
  - true for `Early Summer` and `Early Autumn`
- `season_shoulder_flag`
  - true for `Early Spring` and `Early Winter`

## Explicit Exclusions From Supervised Training

The following columns are intentionally not used as model predictors in Goal 2:

- grouped benchmark price summaries
- grouped benchmark MAD summaries
- `neighbourhood_name`
- `snapshot_date`
- `host_since`

These exclusions exist to reduce leakage and keep the first model version interpretable and defensible.

## Stable Interfaces

- target column: `nightly_price`
- grouping column for split isolation: `listing_id`
- categorical city-conditional feature: `venezia_group_name`
