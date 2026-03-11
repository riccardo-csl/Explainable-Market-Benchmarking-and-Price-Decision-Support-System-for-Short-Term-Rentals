# Cleaned Data Contracts

This document describes the canonical cleaned analytical tables that later stages must produce. The target contracts are defined early so that cleaning, validation, modeling, and backend integration work against a stable interface.

## listing_snapshot

Canonical cleaned listing-level snapshot table used by modeling and downstream APIs.

- Grain: `listing_snapshot_per_scrape_date`
- Primary key: `listing_id, snapshot_date`
- Source datasets: `airbnb_listing_snapshots`

| Field | Type | Nullable | Source Columns | Description |
| --- | --- | --- | --- | --- |
| listing_id | integer | no | Listings id | Stable listing identifier. |
| reviews_last_twelve_months | integer | yes | Last year reviews | Review count observed in the last twelve months. |
| host_since | date | yes | Host since | Host onboarding date. |
| is_superhost | boolean | yes | Host is superhost | Whether the host is marked as a superhost after normalization. |
| host_listing_count | integer | yes | Host number of listings | Number of listings managed by the host. |
| neighbourhood_name | string | yes | Neighbourhood | Normalized neighbourhood label. |
| beds_count | integer | yes | Beds number | Number of beds. |
| bedrooms_count | integer | yes | Bedrooms number | Number of bedrooms. |
| room_type | string | yes | Property type | Normalized room or property type label. |
| accommodates_count | integer | yes | Maximum allowed guests | Maximum allowed guests. |
| nightly_price | float | yes | Price | Observed nightly listing price. |
| total_reviews | integer | yes | Total reviews | Total number of reviews. |
| rating_score | float | yes | Rating score | Overall rating score. |
| accuracy_score | float | yes | Accuracy score | Accuracy review score. |
| cleanliness_score | float | yes | Cleanliness score | Cleanliness review score. |
| checkin_score | float | yes | Checkin score | Check-in review score. |
| communication_score | float | yes | Communication score | Communication review score. |
| location_score | float | yes | Location score | Location review score. |
| value_score | float | yes | Value for money score | Value-for-money review score. |
| reviews_per_month | float | yes | Reviews per month | Reviews per month. |
| city_name | string | no | City | Normalized city label. |
| period_label | string | no | Season | Normalized seasonal label shared across datasets. |
| bathrooms_count | float | yes | Bathrooms number | Bathroom count. |
| bathroom_type | string | yes | Bathrooms type | Bathroom type classification. |
| latitude | float | yes | Coordinates | Latitude parsed from the coordinates field. |
| longitude | float | yes | Coordinates | Longitude parsed from the coordinates field. |
| snapshot_date | date | no | Date of scraping | Source scrape date. |

Notes:
- Coordinates are parsed into latitude and longitude during cleaning.
- The superhost field is normalized into a boolean.

## city_period_summary

Canonical city-level benchmark table derived from the grouped city-period source dataset.

- Grain: `city_period_aggregate`
- Primary key: `city_name, period_label`
- Source datasets: `city_period_summary`

| Field | Type | Nullable | Source Columns | Description |
| --- | --- | --- | --- | --- |
| city_name | string | no | place | Normalized city label. |
| period_label | string | no | period | Normalized seasonal label. |
| dominant_neighbourhood | string | yes | neighbourhood_mode | Most common neighbourhood label within the city-period slice. |
| neighbourhood_entropy | float | yes | neighbourhood_shannon_entropy | Shannon entropy of neighbourhood distribution. |
| dominant_room_type | string | yes | room_type_mode | Most common room type within the city-period slice. |
| room_type_entropy | float | yes | room_type_shannon_entropy | Shannon entropy of room type distribution. |
| reviews_last_twelve_months_median | float | yes | number_of_reviews_ltm_median | Median number of reviews observed in the last twelve months. |
| reviews_last_twelve_months_median_abs_deviation | float | yes | number_of_reviews_ltm_median_abs_deviation | Absolute deviation around the median for median number of reviews observed in the last twelve months. |
| host_listing_count_median | float | yes | host_total_listings_count_median | Median number of listings managed by the host. |
| host_listing_count_median_abs_deviation | float | yes | host_total_listings_count_median_abs_deviation | Absolute deviation around the median for median number of listings managed by the host. |
| accommodates_count_median | float | yes | accommodates_median | Median guest capacity. |
| accommodates_count_median_abs_deviation | float | yes | accommodates_median_abs_deviation | Absolute deviation around the median for median guest capacity. |
| nightly_price_median | float | yes | price_median | Median observed nightly price. |
| nightly_price_median_abs_deviation | float | yes | price_median_abs_deviation | Absolute deviation around the median for median observed nightly price. |
| total_reviews_median | float | yes | number_of_reviews_median | Median total review count. |
| total_reviews_median_abs_deviation | float | yes | number_of_reviews_median_abs_deviation | Absolute deviation around the median for median total review count. |
| rating_score_median | float | yes | review_scores_rating_median | Median overall rating score. |
| rating_score_median_abs_deviation | float | yes | review_scores_rating_median_abs_deviation | Absolute deviation around the median for median overall rating score. |
| accuracy_score_median | float | yes | review_scores_accuracy_median | Median accuracy score. |
| accuracy_score_median_abs_deviation | float | yes | review_scores_accuracy_median_abs_deviation | Absolute deviation around the median for median accuracy score. |
| cleanliness_score_median | float | yes | review_scores_cleanliness_median | Median cleanliness score. |
| cleanliness_score_median_abs_deviation | float | yes | review_scores_cleanliness_median_abs_deviation | Absolute deviation around the median for median cleanliness score. |
| checkin_score_median | float | yes | review_scores_checkin_median | Median check-in score. |
| checkin_score_median_abs_deviation | float | yes | review_scores_checkin_median_abs_deviation | Absolute deviation around the median for median check-in score. |
| communication_score_median | float | yes | review_scores_communication_median | Median communication score. |
| communication_score_median_abs_deviation | float | yes | review_scores_communication_median_abs_deviation | Absolute deviation around the median for median communication score. |
| location_score_median | float | yes | review_scores_location_median | Median location score. |
| location_score_median_abs_deviation | float | yes | review_scores_location_median_abs_deviation | Absolute deviation around the median for median location score. |
| value_score_median | float | yes | review_scores_value_median | Median value score. |
| value_score_median_abs_deviation | float | yes | review_scores_value_median_abs_deviation | Absolute deviation around the median for median value score. |
| reviews_per_month_median | float | yes | reviews_per_month_median | Median reviews per month. |
| reviews_per_month_median_abs_deviation | float | yes | reviews_per_month_median_abs_deviation | Absolute deviation around the median for median reviews per month. |
| latitude_median | float | yes | latitude_median | Median latitude. |
| latitude_median_abs_deviation | float | yes | latitude_median_abs_deviation | Absolute deviation around the median for median latitude. |
| longitude_median | float | yes | longitude_median | Median longitude. |
| longitude_median_abs_deviation | float | yes | longitude_median_abs_deviation | Absolute deviation around the median for median longitude. |

Notes:
- Field names are normalized into snake_case while preserving the original aggregate semantics.

## neighbourhood_period_summary

Canonical neighbourhood-level benchmark table for localized market context.

- Grain: `city_neighbourhood_period_aggregate`
- Primary key: `city_name, neighbourhood_name, period_label`
- Source datasets: `neighbourhood_period_summary`

| Field | Type | Nullable | Source Columns | Description |
| --- | --- | --- | --- | --- |
| city_name | string | no | place | Normalized city label. |
| neighbourhood_name | string | no | neighbourhood | Normalized neighbourhood label. |
| period_label | string | no | period | Normalized seasonal label. |
| dominant_room_type | string | yes | room_type_mode | Most common room type within the neighbourhood-period slice. |
| room_type_entropy | float | yes | room_type_shannon_entropy | Shannon entropy of room type distribution. |
| reviews_last_twelve_months_median | float | yes | number_of_reviews_ltm_median | Median number of reviews observed in the last twelve months. |
| reviews_last_twelve_months_median_abs_deviation | float | yes | number_of_reviews_ltm_median_abs_deviation | Absolute deviation around the median for median number of reviews observed in the last twelve months. |
| host_listing_count_median | float | yes | host_total_listings_count_median | Median number of listings managed by the host. |
| host_listing_count_median_abs_deviation | float | yes | host_total_listings_count_median_abs_deviation | Absolute deviation around the median for median number of listings managed by the host. |
| accommodates_count_median | float | yes | accommodates_median | Median guest capacity. |
| accommodates_count_median_abs_deviation | float | yes | accommodates_median_abs_deviation | Absolute deviation around the median for median guest capacity. |
| nightly_price_median | float | yes | price_median | Median observed nightly price. |
| nightly_price_median_abs_deviation | float | yes | price_median_abs_deviation | Absolute deviation around the median for median observed nightly price. |
| total_reviews_median | float | yes | number_of_reviews_median | Median total review count. |
| total_reviews_median_abs_deviation | float | yes | number_of_reviews_median_abs_deviation | Absolute deviation around the median for median total review count. |
| rating_score_median | float | yes | review_scores_rating_median | Median overall rating score. |
| rating_score_median_abs_deviation | float | yes | review_scores_rating_median_abs_deviation | Absolute deviation around the median for median overall rating score. |
| accuracy_score_median | float | yes | review_scores_accuracy_median | Median accuracy score. |
| accuracy_score_median_abs_deviation | float | yes | review_scores_accuracy_median_abs_deviation | Absolute deviation around the median for median accuracy score. |
| cleanliness_score_median | float | yes | review_scores_cleanliness_median | Median cleanliness score. |
| cleanliness_score_median_abs_deviation | float | yes | review_scores_cleanliness_median_abs_deviation | Absolute deviation around the median for median cleanliness score. |
| checkin_score_median | float | yes | review_scores_checkin_median | Median check-in score. |
| checkin_score_median_abs_deviation | float | yes | review_scores_checkin_median_abs_deviation | Absolute deviation around the median for median check-in score. |
| communication_score_median | float | yes | review_scores_communication_median | Median communication score. |
| communication_score_median_abs_deviation | float | yes | review_scores_communication_median_abs_deviation | Absolute deviation around the median for median communication score. |
| location_score_median | float | yes | review_scores_location_median | Median location score. |
| location_score_median_abs_deviation | float | yes | review_scores_location_median_abs_deviation | Absolute deviation around the median for median location score. |
| value_score_median | float | yes | review_scores_value_median | Median value score. |
| value_score_median_abs_deviation | float | yes | review_scores_value_median_abs_deviation | Absolute deviation around the median for median value score. |
| reviews_per_month_median | float | yes | reviews_per_month_median | Median reviews per month. |
| reviews_per_month_median_abs_deviation | float | yes | reviews_per_month_median_abs_deviation | Absolute deviation around the median for median reviews per month. |
| latitude_median | float | yes | latitude_median | Median latitude. |
| latitude_median_abs_deviation | float | yes | latitude_median_abs_deviation | Absolute deviation around the median for median latitude. |
| longitude_median | float | yes | longitude_median | Median longitude. |
| longitude_median_abs_deviation | float | yes | longitude_median_abs_deviation | Absolute deviation around the median for median longitude. |

Notes:
- This dataset is aggregate context and not a substitute for listing-level observations.

## neighbourhood_reference

Canonical reference mapping between cities, neighbourhoods, and neighbourhood groups.

- Grain: `city_neighbourhood_reference_row`
- Primary key: `city_name, neighbourhood_name`
- Source datasets: `neighbourhood_reference`

| Field | Type | Nullable | Source Columns | Description |
| --- | --- | --- | --- | --- |
| city_name | string | no | city | Normalized city label. |
| neighbourhood_name | string | no | neighbourhood | Normalized neighbourhood label. |
| neighbourhood_group_name | string | yes | neighbourhood_group | Neighbourhood group label if available. |

Notes:
- Neighbourhood group values remain nullable because the source mapping includes nulls.

## neighbourhood_boundary

Canonical boundary dataset for maps and spatial benchmarking after reference enrichment.

- Grain: `cleaned_boundary_row`
- Primary key: `boundary_id`
- Source datasets: `neighbourhood_boundaries, neighbourhood_reference`

| Field | Type | Nullable | Source Columns | Description |
| --- | --- | --- | --- | --- |
| boundary_id | string | no | - | Generated stable identifier for the cleaned neighbourhood boundary row. |
| city_name | string | no | neighbourhood, neighbourhood_group | City label derived during cleaning by joining boundary data with the reference mapping. |
| neighbourhood_name | string | no | neighbourhood | Normalized neighbourhood label. |
| neighbourhood_group_name | string | yes | neighbourhood_group | Neighbourhood group label if available. |
| geometry_type | string | no | geometry.type | GeoJSON geometry type. |
| geometry | geojson | no | geometry | GeoJSON geometry payload. |

Notes:
- City names are expected to be enriched during cleaning because the raw GeoJSON does not expose them.
- Boundary rows may require dissolve logic if multiple raw features map to one logical neighbourhood.
