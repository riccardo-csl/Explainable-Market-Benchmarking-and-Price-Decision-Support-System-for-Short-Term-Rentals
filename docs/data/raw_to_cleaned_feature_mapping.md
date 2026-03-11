# Raw-to-Cleaned Feature Mapping

This is the main human-readable reference for the cleaned Airbnb datasets generated under `data/processed/airbnb/csv/`.

Its purpose is simple:

`for every cleaned field, show the raw source field(s), the transformation applied, and any important caveat`

This document is intentionally more practical than the dataset contracts. It is meant for engineers, analysts, and reviewers who need to understand how the cleaned CSVs were built without reading the transformation code first.

## At a Glance

| Raw dataset | Cleaned dataset | Main purpose |
| --- | --- | --- |
| `data/raw/airbnb/listing_snapshots.csv` | `data/processed/airbnb/csv/listing_snapshot.csv` | Listing-level analytical base table |
| `data/raw/airbnb/city_period_summary.csv` | `data/processed/airbnb/csv/city_period_summary.csv` | City-level seasonal benchmarks |
| `data/raw/airbnb/neighbourhood_period_summary.csv` | `data/processed/airbnb/csv/neighbourhood_period_summary.csv` | Neighbourhood-level seasonal benchmarks |
| `data/raw/airbnb/neighbourhood_reference.csv` | `data/processed/airbnb/csv/neighbourhood_reference.csv` | Reference labels used for joins and normalization |
| `data/raw/airbnb/neighbourhood_boundaries.geojson` | `data/processed/airbnb/csv/neighbourhood_boundary.csv` | Spatial boundary layer for maps and local market context |

## Shared Transformation Rules

These rules appear across multiple cleaned datasets.

### Text normalization

String fields are normalized with the same text-cleaning rules:

- leading and trailing whitespace is removed
- repeated internal whitespace is collapsed
- Unicode text is normalized
- known mojibake cases are repaired where possible

Examples:

- ` roma ` becomes `Roma`
- `early spring` becomes `Early Spring`
- `VII San Giovanni/CinecittÃ ` becomes `VII San Giovanni/Cinecittà`
- `PARCO BOSCO IN CITTÂ…` is repaired to a readable uppercase Italian label

### Canonical city labels

All cleaned datasets use the same city labels:

- `Firenze`
- `Milano`
- `Napoli`
- `Roma`
- `Venezia`

### Canonical period labels

All cleaned datasets use the same seasonal labels:

- `Early Spring`
- `Early Summer`
- `Early Autumn`
- `Early Winter`

### Numeric casting

The cleaned layer does not keep raw numeric values as free-form strings.

- count-like fields are cast to nullable integer columns when the field is conceptually a count
- prices, scores, coordinates, medians, deviations, and entropy fields are cast to nullable float columns
- invalid numeric values are coerced to null

### Derived fields

Some cleaned columns do not exist as single raw fields and are built during cleaning:

- `is_superhost`
- `latitude`
- `longitude`
- `city_name` in `neighbourhood_boundary`
- `boundary_id`

## 1. `listing_snapshot`

### What this table is

`listing_snapshot.csv` is the main listing-level cleaned dataset. It keeps one row per listing per scrape date and is the base table for price estimation, comparable listing logic, and descriptive market analysis.

### Raw source

- `data/raw/airbnb/listing_snapshots.csv`

### Cleaned output

- `data/processed/airbnb/csv/listing_snapshot.csv`
- `data/processed/airbnb/parquet/listing_snapshot.parquet`

### Cleaned grain

One row per `(listing_id, snapshot_date)`.

### Field-by-field mapping

| Cleaned field | Raw field(s) | What happens in cleaning | Notes |
| --- | --- | --- | --- |
| `listing_id` | `Listings id` | Renamed and cast to nullable integer | Listing identifier used in the cleaned primary key |
| `reviews_last_twelve_months` | `Last year reviews` | Renamed and cast to nullable integer | Review count for the last 12 months |
| `host_since` | `Host since` | Renamed and parsed as datetime | Invalid values become null |
| `is_superhost` | `Host is superhost` | Converted from text label to nullable boolean | `Superhost -> true`, `Host -> false`, everything else -> null |
| `host_listing_count` | `Host number of listings` | Renamed, converted to numeric, rounded, cast to nullable integer | Host portfolio size |
| `neighbourhood_name` | `Neighbourhood` | Renamed and text-normalized | No semantic remapping beyond normalization |
| `beds_count` | `Beds number` | Renamed, converted to numeric, rounded, cast to nullable integer | Count field |
| `bedrooms_count` | `Bedrooms number` | Renamed, converted to numeric, rounded, cast to nullable integer | Count field |
| `room_type` | `Property type` | Renamed and text-normalized | The current pipeline preserves the raw meaning; it does not re-bucket room types |
| `accommodates_count` | `Maximum allowed guests` | Renamed, converted to numeric, rounded, cast to nullable integer | Guest capacity |
| `nightly_price` | `Price` | Renamed and cast to nullable float | Observed listing price in the snapshot |
| `total_reviews` | `Total reviews` | Renamed and cast to nullable integer | Lifetime review count |
| `rating_score` | `Rating score` | Renamed and cast to nullable float | Overall rating |
| `accuracy_score` | `Accuracy score` | Renamed and cast to nullable float | Review subscore |
| `cleanliness_score` | `Cleanliness score` | Renamed and cast to nullable float | Review subscore |
| `checkin_score` | `Checkin score` | Renamed and cast to nullable float | Review subscore |
| `communication_score` | `Communication score` | Renamed and cast to nullable float | Review subscore |
| `location_score` | `Location score` | Renamed and cast to nullable float | Review subscore |
| `value_score` | `Value for money score` | Renamed and cast to nullable float | Review subscore |
| `reviews_per_month` | `Reviews per month` | Renamed and cast to nullable float | Review frequency proxy |
| `city_name` | `City` | Renamed, text-normalized, then mapped to canonical city labels | Must resolve to one of the five supported cities |
| `period_label` | `Season` | Renamed and normalized to canonical seasonal labels | Aligns listing-level data with grouped summary datasets |
| `bathrooms_count` | `Bathrooms number` | Renamed and cast to nullable float | Kept as float because the raw values are not guaranteed to be whole numbers |
| `bathroom_type` | `Bathrooms type` | Renamed and text-normalized | Typically values such as private/shared |
| `latitude` | `Coordinates` | Derived by parsing the first numeric element in the raw coordinate string | Null if parsing fails |
| `longitude` | `Coordinates` | Derived by parsing the second numeric element in the raw coordinate string | Null if parsing fails |
| `snapshot_date` | `Date of scraping` | Renamed and parsed as datetime | Used in the cleaned primary key |

### Raw fields that do not survive as standalone columns

| Raw field | Why it disappears |
| --- | --- |
| `Host is superhost` | Replaced by the boolean field `is_superhost` |
| `Coordinates` | Replaced by the numeric fields `latitude` and `longitude` |

### Important implementation note

This table is almost entirely a rename-and-cast transformation, except for three cases:

- `is_superhost` is a categorical-to-boolean mapping
- `latitude` and `longitude` are parsed from one raw coordinate field
- `city_name` and `period_label` are normalized into canonical labels shared across all cleaned datasets

## 2. `city_period_summary`

### What this table is

`city_period_summary.csv` is the city-level benchmark table. Each row is already aggregated in the raw input, so the cleaning step does not recompute metrics. It standardizes names, types, and labels so the table can be joined or compared consistently.

### Raw source

- `data/raw/airbnb/city_period_summary.csv`

### Cleaned output

- `data/processed/airbnb/csv/city_period_summary.csv`
- `data/processed/airbnb/parquet/city_period_summary.parquet`

### Cleaned grain

One row per `(city_name, period_label)`.

### Identity and context fields

| Cleaned field | Raw field | What happens in cleaning | Notes |
| --- | --- | --- | --- |
| `city_name` | `place` | Renamed and normalized to canonical city labels | Join key and analytical dimension |
| `period_label` | `period` | Renamed and normalized to canonical seasonal labels | Join key and analytical dimension |
| `dominant_neighbourhood` | `neighbourhood_mode` | Renamed and text-normalized | Most common neighbourhood within the city-period slice |
| `neighbourhood_entropy` | `neighbourhood_shannon_entropy` | Renamed and cast to nullable float | Spread of neighbourhood distribution |
| `dominant_room_type` | `room_type_mode` | Renamed and text-normalized | Most common room type in the slice |
| `room_type_entropy` | `room_type_shannon_entropy` | Renamed and cast to nullable float | Spread of room type distribution |

### Metric fields

| Cleaned field | Raw field | What happens in cleaning |
| --- | --- | --- |
| `reviews_last_twelve_months_median` | `number_of_reviews_ltm_median` | Renamed and cast to nullable float |
| `reviews_last_twelve_months_median_abs_deviation` | `number_of_reviews_ltm_median_abs_deviation` | Renamed and cast to nullable float |
| `host_listing_count_median` | `host_total_listings_count_median` | Renamed and cast to nullable float |
| `host_listing_count_median_abs_deviation` | `host_total_listings_count_median_abs_deviation` | Renamed and cast to nullable float |
| `accommodates_count_median` | `accommodates_median` | Renamed and cast to nullable float |
| `accommodates_count_median_abs_deviation` | `accommodates_median_abs_deviation` | Renamed and cast to nullable float |
| `nightly_price_median` | `price_median` | Renamed and cast to nullable float |
| `nightly_price_median_abs_deviation` | `price_median_abs_deviation` | Renamed and cast to nullable float |
| `total_reviews_median` | `number_of_reviews_median` | Renamed and cast to nullable float |
| `total_reviews_median_abs_deviation` | `number_of_reviews_median_abs_deviation` | Renamed and cast to nullable float |
| `rating_score_median` | `review_scores_rating_median` | Renamed and cast to nullable float |
| `rating_score_median_abs_deviation` | `review_scores_rating_median_abs_deviation` | Renamed and cast to nullable float |
| `accuracy_score_median` | `review_scores_accuracy_median` | Renamed and cast to nullable float |
| `accuracy_score_median_abs_deviation` | `review_scores_accuracy_median_abs_deviation` | Renamed and cast to nullable float |
| `cleanliness_score_median` | `review_scores_cleanliness_median` | Renamed and cast to nullable float |
| `cleanliness_score_median_abs_deviation` | `review_scores_cleanliness_median_abs_deviation` | Renamed and cast to nullable float |
| `checkin_score_median` | `review_scores_checkin_median` | Renamed and cast to nullable float |
| `checkin_score_median_abs_deviation` | `review_scores_checkin_median_abs_deviation` | Renamed and cast to nullable float |
| `communication_score_median` | `review_scores_communication_median` | Renamed and cast to nullable float |
| `communication_score_median_abs_deviation` | `review_scores_communication_median_abs_deviation` | Renamed and cast to nullable float |
| `location_score_median` | `review_scores_location_median` | Renamed and cast to nullable float |
| `location_score_median_abs_deviation` | `review_scores_location_median_abs_deviation` | Renamed and cast to nullable float |
| `value_score_median` | `review_scores_value_median` | Renamed and cast to nullable float |
| `value_score_median_abs_deviation` | `review_scores_value_median_abs_deviation` | Renamed and cast to nullable float |
| `reviews_per_month_median` | `reviews_per_month_median` | Preserved semantically and cast to nullable float |
| `reviews_per_month_median_abs_deviation` | `reviews_per_month_median_abs_deviation` | Preserved semantically and cast to nullable float |
| `latitude_median` | `latitude_median` | Preserved semantically and cast to nullable float |
| `latitude_median_abs_deviation` | `latitude_median_abs_deviation` | Preserved semantically and cast to nullable float |
| `longitude_median` | `longitude_median` | Preserved semantically and cast to nullable float |
| `longitude_median_abs_deviation` | `longitude_median_abs_deviation` | Preserved semantically and cast to nullable float |

### Important implementation note

No new city-level benchmark is computed here. The raw file is already aggregated. Cleaning only standardizes field names, types, and labels so this table matches the rest of the project.

## 3. `neighbourhood_period_summary`

### What this table is

`neighbourhood_period_summary.csv` is the local micro-market benchmark table. It follows the same transformation pattern as `city_period_summary`, but the grain is finer because each row is for one city, one neighbourhood, and one seasonal period.

### Raw source

- `data/raw/airbnb/neighbourhood_period_summary.csv`

### Cleaned output

- `data/processed/airbnb/csv/neighbourhood_period_summary.csv`
- `data/processed/airbnb/parquet/neighbourhood_period_summary.parquet`

### Cleaned grain

One row per `(city_name, neighbourhood_name, period_label)`.

### Identity and context fields

| Cleaned field | Raw field | What happens in cleaning | Notes |
| --- | --- | --- | --- |
| `city_name` | `place` | Renamed and normalized to canonical city labels | Join key and analytical dimension |
| `neighbourhood_name` | `neighbourhood` | Renamed and text-normalized | Local market identifier |
| `period_label` | `period` | Renamed and normalized to canonical seasonal labels | Time slice label |
| `dominant_room_type` | `room_type_mode` | Renamed and text-normalized | Most common room type in the neighbourhood-period slice |
| `room_type_entropy` | `room_type_shannon_entropy` | Renamed and cast to nullable float | Spread of room type distribution |

### Metric fields

| Cleaned field | Raw field | What happens in cleaning |
| --- | --- | --- |
| `reviews_last_twelve_months_median` | `number_of_reviews_ltm_median` | Renamed and cast to nullable float |
| `reviews_last_twelve_months_median_abs_deviation` | `number_of_reviews_ltm_median_abs_deviation` | Renamed and cast to nullable float |
| `host_listing_count_median` | `host_total_listings_count_median` | Renamed and cast to nullable float |
| `host_listing_count_median_abs_deviation` | `host_total_listings_count_median_abs_deviation` | Renamed and cast to nullable float |
| `accommodates_count_median` | `accommodates_median` | Renamed and cast to nullable float |
| `accommodates_count_median_abs_deviation` | `accommodates_median_abs_deviation` | Renamed and cast to nullable float |
| `nightly_price_median` | `price_median` | Renamed and cast to nullable float |
| `nightly_price_median_abs_deviation` | `price_median_abs_deviation` | Renamed and cast to nullable float |
| `total_reviews_median` | `number_of_reviews_median` | Renamed and cast to nullable float |
| `total_reviews_median_abs_deviation` | `number_of_reviews_median_abs_deviation` | Renamed and cast to nullable float |
| `rating_score_median` | `review_scores_rating_median` | Renamed and cast to nullable float |
| `rating_score_median_abs_deviation` | `review_scores_rating_median_abs_deviation` | Renamed and cast to nullable float |
| `accuracy_score_median` | `review_scores_accuracy_median` | Renamed and cast to nullable float |
| `accuracy_score_median_abs_deviation` | `review_scores_accuracy_median_abs_deviation` | Renamed and cast to nullable float |
| `cleanliness_score_median` | `review_scores_cleanliness_median` | Renamed and cast to nullable float |
| `cleanliness_score_median_abs_deviation` | `review_scores_cleanliness_median_abs_deviation` | Renamed and cast to nullable float |
| `checkin_score_median` | `review_scores_checkin_median` | Renamed and cast to nullable float |
| `checkin_score_median_abs_deviation` | `review_scores_checkin_median_abs_deviation` | Renamed and cast to nullable float |
| `communication_score_median` | `review_scores_communication_median` | Renamed and cast to nullable float |
| `communication_score_median_abs_deviation` | `review_scores_communication_median_abs_deviation` | Renamed and cast to nullable float |
| `location_score_median` | `review_scores_location_median` | Renamed and cast to nullable float |
| `location_score_median_abs_deviation` | `review_scores_location_median_abs_deviation` | Renamed and cast to nullable float |
| `value_score_median` | `review_scores_value_median` | Renamed and cast to nullable float |
| `value_score_median_abs_deviation` | `review_scores_value_median_abs_deviation` | Renamed and cast to nullable float |
| `reviews_per_month_median` | `reviews_per_month_median` | Preserved semantically and cast to nullable float |
| `reviews_per_month_median_abs_deviation` | `reviews_per_month_median_abs_deviation` | Preserved semantically and cast to nullable float |
| `latitude_median` | `latitude_median` | Preserved semantically and cast to nullable float |
| `latitude_median_abs_deviation` | `latitude_median_abs_deviation` | Preserved semantically and cast to nullable float |
| `longitude_median` | `longitude_median` | Preserved semantically and cast to nullable float |
| `longitude_median_abs_deviation` | `longitude_median_abs_deviation` | Preserved semantically and cast to nullable float |

### Important implementation note

As with the city-level table, the metrics already exist in raw form. The cleaning step standardizes them so neighbourhood and city aggregates use aligned names and types.

## 4. `neighbourhood_reference`

### What this table is

`neighbourhood_reference.csv` is the reference table used to normalize location labels and enrich the spatial boundary layer. It is intentionally small and simple, but it is structurally important because it supplies the clean join vocabulary for neighbourhood names and groups.

### Raw source

- `data/raw/airbnb/neighbourhood_reference.csv`

### Cleaned output

- `data/processed/airbnb/csv/neighbourhood_reference.csv`
- `data/processed/airbnb/parquet/neighbourhood_reference.parquet`

### Cleaned grain

One row per city-neighbourhood reference record.

### Field-by-field mapping

| Cleaned field | Raw field | What happens in cleaning | Notes |
| --- | --- | --- | --- |
| `city_name` | `city` | Renamed and normalized to canonical city labels | Used in joins and reporting |
| `neighbourhood_name` | `neighbourhood` | Renamed and text-normalized | Main neighbourhood key used across cleaned data |
| `neighbourhood_group_name` | `neighbourhood_group` | Renamed and text-normalized | May remain null if the raw value is missing |

### Important implementation note

This table does not derive new attributes. Its value comes from standardization. It provides a consistent spelling layer that makes the joins between grouped summaries and boundary data workable.

## 5. `neighbourhood_boundary`

### What this table is

`neighbourhood_boundary.csv` is the cleaned spatial layer derived from the GeoJSON boundary file. It keeps one row per raw geometry feature after normalization. It is designed for mapping and spatial context, not for aggregate statistics.

### Raw source

- `data/raw/airbnb/neighbourhood_boundaries.geojson`
- enriched during cleaning with `data/raw/airbnb/neighbourhood_reference.csv`

### Cleaned output

- `data/processed/airbnb/csv/neighbourhood_boundary.csv`
- `data/processed/airbnb/parquet/neighbourhood_boundary.parquet`

### Cleaned grain

One row per raw GeoJSON feature after normalization. The pipeline does not dissolve multiple geometries into one logical neighbourhood row.

### Field-by-field mapping

| Cleaned field | Raw field(s) | What happens in cleaning | Notes |
| --- | --- | --- | --- |
| `boundary_id` | `neighbourhood`, `neighbourhood_group`, enriched `city_name`, raw feature order | Generated deterministically | Readable unique identifier such as `roma_castello_001` |
| `city_name` | no direct field in GeoJSON | Added by joining the normalized boundary rows to `neighbourhood_reference` on `neighbourhood_name` | This is an enriched field, not a direct raw extraction |
| `neighbourhood_name` | `properties.neighbourhood` | Extracted from GeoJSON properties and text-normalized | Human-readable boundary label |
| `neighbourhood_group_name` | `properties.neighbourhood_group` | Extracted and text-normalized, then completed from the reference table if missing | Helps align boundary records with the reference vocabulary |
| `geometry_type` | `geometry.type` | Extracted directly from the GeoJSON geometry object | For the current dataset this is typically `MultiPolygon` |
| `geometry` | `geometry` | Serialized into stable JSON text | Stored as a GeoJSON-compatible payload in the cleaned CSV and Parquet outputs |

### Raw fields introduced during loading before final cleaning

The GeoJSON loader creates an intermediate tabular structure before the final cleaned dataset is written.

| Intermediate field | Origin | Why it exists |
| --- | --- | --- |
| `raw_feature_index` | GeoJSON feature order | Keeps the original feature order so deterministic IDs can be generated |
| `neighbourhood` | `properties.neighbourhood` | Raw property extracted before renaming |
| `neighbourhood_group` | `properties.neighbourhood_group` | Raw property extracted before renaming |
| `geometry_type` | `geometry.type` | Easier tabular access to the geometry type |
| `geometry` | full GeoJSON geometry object | Converted later into JSON text for the cleaned layer |

### How `boundary_id` is generated

`boundary_id` does not exist in the raw data. It is generated because `neighbourhood_name` alone is not guaranteed to be unique inside the boundary file.

The logic is:

1. normalize `city_name`, `neighbourhood_name`, and `neighbourhood_group_name`
2. convert those values into a readable slug base
3. sort rows stably by slug base and original feature order
4. assign a zero-padded suffix inside each slug group

Examples:

- `roma_castello_001`
- `roma_castello_002`

This gives the cleaned table three properties that are important for engineering:

- uniqueness
- reproducibility
- readability

### Raw fields that do not survive as standalone columns

| Raw or intermediate field | Why it disappears |
| --- | --- |
| `raw_feature_index` | Used only to stabilize `boundary_id` generation |
| `neighbourhood` | Replaced by `neighbourhood_name` |
| `neighbourhood_group` | Replaced by `neighbourhood_group_name` |
| `neighbourhood_group_name_reference` | Temporary join helper used during enrichment |

## Cross-Dataset Join Logic

The cleaned layer is designed so the CSVs can be joined in a predictable way.

| Join | Shared fields | Why it works |
| --- | --- | --- |
| `listing_snapshot` -> `city_period_summary` | `city_name`, `period_label` | Listing-level rows and city-level benchmarks use the same normalized labels |
| `listing_snapshot` -> `neighbourhood_period_summary` | `city_name`, `neighbourhood_name`, `period_label` | Listing rows can be matched to local neighbourhood benchmarks |
| `neighbourhood_period_summary` -> `neighbourhood_reference` | `city_name`, `neighbourhood_name` | Reference table supplies standardized local labels |
| `neighbourhood_boundary` -> `neighbourhood_reference` | `neighbourhood_name` plus completed `neighbourhood_group_name` | Boundary data is enriched to align with the same cleaned vocabulary |

## Non-Trivial Fields Worth Remembering

These cleaned fields are the ones most likely to matter during debugging or modeling work.

| Cleaned field | Why it needs special attention |
| --- | --- |
| `is_superhost` | Derived from a text status field rather than copied directly |
| `latitude` | Parsed from a combined coordinate string |
| `longitude` | Parsed from a combined coordinate string |
| `city_name` in `neighbourhood_boundary` | Added via enrichment, not present in the raw GeoJSON |
| `boundary_id` | Generated to create a stable feature identifier |
| `geometry` in `neighbourhood_boundary` | Serialized from nested GeoJSON into flat tabular storage |

## Quick Reading Guide

If you need to understand the cleaned outputs quickly:

- start with `listing_snapshot` for property-level analytics
- use `city_period_summary` for city-wide seasonal benchmarks
- use `neighbourhood_period_summary` for micro-market comparisons
- use `neighbourhood_reference` when you need clean join labels
- use `neighbourhood_boundary` when you need map-ready geometry

If you need the implementation details behind these mappings, the transformation code lives in:

- `modeling/src/data_foundation/cleaned_dataset_builder.py`
- `modeling/src/data_foundation/normalization.py`
- `modeling/src/data_foundation/raw_dataset_loader.py`
