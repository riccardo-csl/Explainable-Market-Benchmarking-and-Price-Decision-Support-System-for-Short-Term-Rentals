# Source Dataset Inventory

This document describes the inventory of the raw source datasets currently available in the repository. It records what each source file contains, how it is expected to be used, and which limitations must be carried forward into later stages.

## Dataset Overview

| Dataset | Format | Grain | Rows/Features | Path |
| --- | --- | --- | --- | --- |
| airbnb_listing_snapshots | csv | listing_snapshot_per_scrape_date | 282047 | data/raw/airbnb/listing_snapshots.csv |
| city_period_summary | csv | city_period_aggregate | 17 | data/raw/airbnb/city_period_summary.csv |
| neighbourhood_period_summary | csv | city_neighbourhood_period_aggregate | 655 | data/raw/airbnb/neighbourhood_period_summary.csv |
| neighbourhood_reference | csv | city_neighbourhood_reference_row | 252 | data/raw/airbnb/neighbourhood_reference.csv |
| neighbourhood_boundaries | geojson | boundary_feature | 710 | data/raw/airbnb/neighbourhood_boundaries.geojson |

## airbnb_listing_snapshots

Listing-level Airbnb snapshot data with pricing, review metrics, location, and seasonal scrape metadata.

- Raw path: `data/raw/airbnb/listing_snapshots.csv`
- Original filename: `airbnb.csv`
- Format: `csv`
- Grain: `listing_snapshot_per_scrape_date`
- Role: `primary_listing_level_dataset`
- Source category: `third_party_export`
- Steward: `project_team`
- Immutable input: `yes`
- Rows/Features: `282047`

### Coverage

- cities: Firenze, Milano, Napoli, Roma, Venezia
- periods: Early Autumn, Early Spring, Early Summer, Early Winter
- snapshot_dates: 2024-03-15, 2024-06-15, 2024-09-15, 2024-12-15

### Candidate Keys

| Columns | Unique | Duplicate Keys |
| --- | --- | --- |
| Listings id, Date of scraping | yes | 0 |
| Listings id, Season | yes | 0 |

### Fields

| Field | Type | Nullable | Likely Categorical | Sample Values |
| --- | --- | --- | --- | --- |
| Listings id | integer | no | no | 31840, 222527, 32120, 224562, 32180 |
| Last year reviews | integer | no | no | 6, 0, 9, 11, 17 |
| Host since | date | no | no | 2011-02-07, 2011-07-11, 2010-03-26, 2011-09-16, 2014-04-05 |
| Host is superhost | string | no | yes | Host, Superhost |
| Host number of listings | float | no | no | 44.0, 3.0, 1.0, 2.0, 6.0 |
| Neighbourhood | string | no | no | Centro Storico, Rifredi, Gavinana Galluzzo, Campo di Marte, Isolotto Legnaia |
| Beds number | float | no | no | 1.0, 3.0, 4.0, 2.0, 6.0 |
| Bedrooms number | float | no | no | 1.0, 2.0, 3.0, 4.0, 5.0 |
| Property type | string | no | yes | Private room, Entire home, Hotel room, Shared room |
| Maximum allowed guests | integer | no | no | 2, 4, 1, 3, 10 |
| Price | float | no | no | 89.0, 300.0, 95.0, 60.0, 105.0 |
| Total reviews | integer | no | no | 128, 284, 26, 101, 34 |
| Rating score | float | no | no | 4.65, 4.85, 4.88, 4.66, 4.76 |
| Accuracy score | float | no | no | 4.73, 4.88, 4.75, 4.81, 5.0 |
| Cleanliness score | float | no | no | 4.86, 4.88, 4.71, 4.84, 5.0 |
| Checkin score | float | no | no | 4.85, 4.99, 4.84, 4.76, 4.81 |
| Communication score | float | no | no | 4.91, 4.96, 4.83, 4.71, 4.98 |
| Location score | float | no | no | 4.91, 4.6, 4.63, 4.93, 4.81 |
| Value for money score | float | no | no | 4.7, 4.86, 4.63, 4.64, 4.84 |
| Reviews per month | float | no | no | 0.78, 1.92, 0.16, 0.71, 0.21 |
| City | string | no | yes | Firenze, Milano, Napoli, Roma, Venezia |
| Season | string | no | yes | Early Winter, Early Spring, Early Summer, Early Autumn |
| Bathrooms number | integer | no | no | 1, 2, 0, 4, 3 |
| Bathrooms type | string | no | yes | private, shared |
| Coordinates | string | no | no | 43.77709, 11.25216, 43.82005, 11.22004, 43.76157, 11.27741, 43.772, 11.26142, 43.76832, 11.24348 |
| Date of scraping | date | no | no | 2024-12-15, 2024-03-15, 2024-06-15, 2024-09-15 |

### Known Limitations

- Listing identifiers repeat across multiple scrape dates by design.
- The `Coordinates` column stores latitude and longitude as a combined string.
- The `Property type` field behaves as a room-type style category in the observed source data.

## city_period_summary

City-period aggregate statistics derived from listing-level data. Intended for city-level benchmarking and contextual market summaries.

- Raw path: `data/raw/airbnb/city_period_summary.csv`
- Original filename: `airbnb_italian_city_grouped.csv`
- Format: `csv`
- Grain: `city_period_aggregate`
- Role: `city_level_benchmark_dataset`
- Source category: `project_derived_source`
- Steward: `project_team`
- Immutable input: `yes`
- Rows/Features: `17`

### Coverage

- cities: Firenze, Milano, Napoli, Roma, Venezia
- periods: Early Autumn, Early Spring, Early Summer, Early Winter

### Candidate Keys

| Columns | Unique | Duplicate Keys |
| --- | --- | --- |
| place, period | yes | 0 |

### Fields

| Field | Type | Nullable | Likely Categorical | Sample Values |
| --- | --- | --- | --- | --- |
| place | string | no | yes | Firenze, Milano, Napoli, Roma, Venezia |
| period | string | no | yes | Early Spring, Early Summer, Early Winter, Early Autumn |
| number_of_reviews_ltm_median | float | no | no | 14.0, 13.0, 11.0, 6.0, 5.0 |
| number_of_reviews_ltm_median_abs_deviation | float | no | no | 12.0, 11.0, 6.0, 5.0, 4.0 |
| host_total_listings_count_median | float | no | no | 4.0, 3.0 |
| host_total_listings_count_median_abs_deviation | float | no | no | 3.0, 2.0 |
| neighbourhood_mode | string | no | yes | Centro Storico, BUENOS AIRES - VENEZIA, San Lorenzo, I Centro Storico, Castello |
| neighbourhood_shannon_entropy | float | no | no | 1.2874, 1.3446, 1.3021, 5.5081, 5.5333 |
| room_type_mode | string | no | yes | Entire home/apt |
| room_type_shannon_entropy | float | no | no | 0.7001, 0.6972, 0.7552, 0.6032, 0.6139 |
| accommodates_median | float | no | no | 4.0, 3.0 |
| accommodates_median_abs_deviation | float | no | no | 1.0, 2.0 |
| price_median | float | no | no | 130.0, 145.0, 115.0, 100.0, 105.0 |
| price_median_abs_deviation | float | no | no | 43.0, 49.0, 35.0, 30.0, 31.0 |
| number_of_reviews_median | float | no | no | 34.0, 32.5, 30.5, 13.0, 12.0 |
| number_of_reviews_median_abs_deviation | float | no | no | 30.0, 28.5, 26.5, 11.0, 10.0 |
| review_scores_rating_median | float | no | no | 4.82, 4.83, 4.81, 4.84 |
| review_scores_rating_median_abs_deviation | float | no | no | 0.14, 0.15, 0.17, 0.16 |
| review_scores_accuracy_median | float | no | no | 4.88, 4.87, 4.86 |
| review_scores_accuracy_median_abs_deviation | float | no | no | 0.11, 0.12, 0.13, 0.1 |
| review_scores_cleanliness_median | float | no | no | 4.87, 4.86, 4.88, 4.89, 4.85 |
| review_scores_cleanliness_median_abs_deviation | float | no | no | 0.13, 0.14, 0.12, 0.11, 0.15 |
| review_scores_checkin_median | float | no | no | 4.91, 4.92, 4.88, 4.89 |
| review_scores_checkin_median_abs_deviation | float | no | no | 0.09, 0.08, 0.1 |
| review_scores_communication_median | float | no | no | 4.93, 4.92, 4.94, 4.95, 4.96 |
| review_scores_communication_median_abs_deviation | float | no | no | 0.07, 0.08, 0.06, 0.05, 0.04 |
| review_scores_location_median | float | no | no | 4.9, 4.89, 4.81, 4.8, 4.82 |
| review_scores_location_median_abs_deviation | float | no | no | 0.1, 0.11, 0.19, 0.2, 0.18 |
| review_scores_value_median | float | no | no | 4.76, 4.75, 4.71, 4.7, 4.78 |
| review_scores_value_median_abs_deviation | float | no | no | 0.14, 0.15, 0.21, 0.2, 0.17 |
| reviews_per_month_median | float | no | no | 1.33, 1.46, 1.25, 0.915, 0.94 |
| reviews_per_month_median_abs_deviation | float | no | no | 0.96, 1.08, 0.97, 0.735, 0.76 |
| latitude_median | float | no | no | 43.7724, 43.7726, 43.7725, 45.4716, 45.4717 |
| latitude_median_abs_deviation | float | no | no | 0.0043, 0.0045, 0.0044, 0.0158, 0.016 |
| longitude_median | float | no | no | 11.2542, 11.2543, 11.254, 9.1878, 9.1877 |
| longitude_median_abs_deviation | float | no | no | 0.0079, 0.0081, 0.0202, 0.0207, 0.0208 |

### Known Limitations

- This dataset is aggregated and cannot be used for property-level modeling by itself.
- City and period labels use different header names than the listing-level source dataset.

## neighbourhood_period_summary

Neighbourhood-period aggregate statistics used for local benchmark context.

- Raw path: `data/raw/airbnb/neighbourhood_period_summary.csv`
- Original filename: `airbnb_italian_neighbourhood_grouped.csv`
- Format: `csv`
- Grain: `city_neighbourhood_period_aggregate`
- Role: `neighbourhood_level_benchmark_dataset`
- Source category: `project_derived_source`
- Steward: `project_team`
- Immutable input: `yes`
- Rows/Features: `655`

### Coverage

- cities: Firenze, Milano, Napoli, Roma, Venezia
- periods: Early Autumn, Early Spring, Early Summer, Early Winter

### Candidate Keys

| Columns | Unique | Duplicate Keys |
| --- | --- | --- |
| place, neighbourhood, period | yes | 0 |

### Fields

| Field | Type | Nullable | Likely Categorical | Sample Values |
| --- | --- | --- | --- | --- |
| neighbourhood | string | no | yes | ADRIANO, AFFORI, Aeroporto, Alberoni, Altobello |
| period | string | no | yes | Early Spring, Early Summer, Early Winter, Early Autumn |
| number_of_reviews_ltm_median | float | no | no | 4.0, 3.0, 5.0, 6.0, 7.0 |
| number_of_reviews_ltm_median_abs_deviation | float | no | no | 3.0, 4.0, 7.0, 6.5, 2.5 |
| host_total_listings_count_median | float | no | no | 2.0, 4.0, 3.0, 9.0, 1.0 |
| host_total_listings_count_median_abs_deviation | float | no | no | 1.0, 3.0, 2.0, 0.0, 2.5 |
| room_type_mode | string | no | yes | Entire home/apt, Private room |
| room_type_shannon_entropy | float | no | no | 0.6499, 0.6718, 0.662, 0.7549, 0.7427 |
| accommodates_median | float | no | no | 4.0, 3.0, 2.5, 2.0, 6.0 |
| accommodates_median_abs_deviation | float | no | no | 1.0, 0.5, 0.0, 2.0, 2.5 |
| price_median | float | no | no | 80.0, 79.5, 75.0, 77.0, 129.0 |
| price_median_abs_deviation | float | no | no | 16.0, 15.0, 18.5, 18.0, 21.0 |
| number_of_reviews_median | float | no | no | 8.0, 9.0, 23.0, 127.0, 131.0 |
| number_of_reviews_median_abs_deviation | float | no | no | 7.0, 8.0, 22.0, 111.0, 112.0 |
| review_scores_rating_median | float | no | no | 4.87, 4.89, 4.82, 4.86, 4.8 |
| review_scores_rating_median_abs_deviation | float | no | no | 0.13, 0.11, 0.18, 0.14, 0.2 |
| review_scores_accuracy_median | float | no | no | 4.89, 4.845, 4.87, 4.83, 4.86 |
| review_scores_accuracy_median_abs_deviation | float | no | no | 0.11, 0.155, 0.13, 0.17, 0.14 |
| review_scores_cleanliness_median | float | no | no | 4.82, 4.815, 4.81, 4.88, 4.92 |
| review_scores_cleanliness_median_abs_deviation | float | no | no | 0.18, 0.185, 0.19, 0.12, 0.08 |
| review_scores_checkin_median | float | no | no | 4.94, 4.945, 4.91, 4.83, 4.8 |
| review_scores_checkin_median_abs_deviation | float | no | no | 0.06, 0.055, 0.09, 0.13, 0.05 |
| review_scores_communication_median | float | no | no | 5.0, 4.985, 4.935, 4.95, 4.94 |
| review_scores_communication_median_abs_deviation | float | no | no | 0.0, 0.015, 0.065, 0.05, 0.06 |
| review_scores_location_median | float | no | no | 4.5, 4.455, 4.7, 4.67, 4.69 |
| review_scores_location_median_abs_deviation | float | no | no | 0.27, 0.3, 0.255, 0.23, 0.05 |
| review_scores_value_median | float | no | no | 4.68, 4.74, 4.69, 4.7, 4.67 |
| review_scores_value_median_abs_deviation | float | no | no | 0.27, 0.25, 0.255, 0.23, 0.26 |
| reviews_per_month_median | float | no | no | 0.86, 0.61, 0.71, 0.73, 0.69 |
| reviews_per_month_median_abs_deviation | float | no | no | 0.6, 0.61, 0.53, 0.56, 0.69 |
| place | string | no | yes | Milano, Venezia, Napoli, Firenze, Roma |
| latitude_median | float | no | no | 45.5119, 45.512, 45.5126, 45.515, 45.5148 |
| latitude_median_abs_deviation | float | no | no | 0.003, 0.0031, 0.0023, 0.0043, 0.0014 |
| longitude_median | float | no | no | 9.2422, 9.2438, 9.1727, 9.1729, 12.3314 |
| longitude_median_abs_deviation | float | no | no | 0.0037, 0.0036, 0.0034, 0.003, 0.0028 |

### Known Limitations

- This dataset is aggregated and should be treated as benchmark context, not as listing-level evidence.

## neighbourhood_reference

Reference mapping between neighbourhoods, neighbourhood groups, and cities.

- Raw path: `data/raw/airbnb/neighbourhood_reference.csv`
- Original filename: `airbnb_italy_city_neighbourhoods.csv`
- Format: `csv`
- Grain: `city_neighbourhood_reference_row`
- Role: `reference_mapping_dataset`
- Source category: `reference_source`
- Steward: `project_team`
- Immutable input: `yes`
- Rows/Features: `252`

### Coverage

- cities: firenze, milano, napoli, roma, venezia

### Candidate Keys

| Columns | Unique | Duplicate Keys |
| --- | --- | --- |
| city, neighbourhood | yes | 0 |

### Fields

| Field | Type | Nullable | Likely Categorical | Sample Values |
| --- | --- | --- | --- | --- |
| neighbourhood_group | string | yes | yes | Isole, Terraferma |
| neighbourhood | string | no | yes | Campo di Marte, Centro Storico, Gavinana Galluzzo, Isolotto Legnaia, Rifredi |
| city | string | no | yes | firenze, milano, napoli, roma, venezia |

### Known Limitations

- Neighbourhood group values can be null and must be treated as optional reference data.

## neighbourhood_boundaries

GeoJSON neighbourhood boundaries used for mapping and spatial context.

- Raw path: `data/raw/airbnb/neighbourhood_boundaries.geojson`
- Original filename: `airbnb_italy_city_neighbourhoods_geojson.geojson`
- Format: `geojson`
- Grain: `boundary_feature`
- Role: `spatial_boundary_dataset`
- Source category: `spatial_source`
- Steward: `project_team`
- Immutable input: `yes`
- Rows/Features: `710`

### Fields

| Field | Type | Nullable | Likely Categorical | Sample Values |
| --- | --- | --- | --- | --- |
| city | string | no | yes | viz |
| neighbourhood | string | no | yes | Rifredi, Gavinana Galluzzo, Campo di Marte, Isolotto Legnaia, Centro Storico |
| neighbourhood_group | string | yes | yes | Isole, Terraferma |

### Known Limitations

- The GeoJSON features do not expose a city property directly.
- The boundary file contains multiple features for some logical neighbourhood entities.
- Some neighbourhood names require encoding normalization to align cleanly with the reference CSV.

## Dataset Relationships

| From | To | Relation Type | Join Columns | Notes |
| --- | --- | --- | --- | --- |
| airbnb_listing_snapshots | city_period_summary | many_to_one_after_normalization | city_name, period_label | Join requires header normalization because the listing dataset uses `City` and `Season`, while the aggregate dataset uses `place` and `period`. |
| airbnb_listing_snapshots | neighbourhood_reference | many_to_one_after_normalization | city_name, neighbourhood_name | Join uses normalized city and neighbourhood labels. |
| neighbourhood_period_summary | neighbourhood_reference | many_to_one_after_normalization | city_name, neighbourhood_name | Neighbourhood aggregates can be enriched through the reference mapping table. |
| neighbourhood_reference | neighbourhood_boundaries | one_to_many_with_encoding_and_spatial_normalization | neighbourhood_name, neighbourhood_group_name | The GeoJSON does not include city names and may expose multiple features per logical neighbourhood, so later cleaning must normalize encoding and potentially dissolve boundaries. |
