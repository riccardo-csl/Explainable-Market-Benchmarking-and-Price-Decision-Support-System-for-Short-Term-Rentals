# Cleaned Dataset Dictionary

This document is a short operational reference for the cleaned datasets produced by Goal 1.

Unlike the contract YAMLs, it is written for fast human reading. Use it when you need to know what each cleaned dataset is for, how to join it, and which fields matter most for Goal 2.

## `listing_snapshot`

Purpose:

The main listing-level analytical dataset. This is the base table for price estimation, feature engineering, comparable listing logic, and most exploratory analysis.

Grain:

One row per `(listing_id, snapshot_date)`.

Primary key:

- `listing_id`
- `snapshot_date`

Most important fields for Goal 2:

- `nightly_price`
- `city_name`
- `neighbourhood_name`
- `period_label`
- `room_type`
- `accommodates_count`
- `beds_count`
- `bedrooms_count`
- `bathrooms_count`
- `host_listing_count`
- `is_superhost`
- `total_reviews`
- `reviews_last_twelve_months`
- review score fields
- `latitude`
- `longitude`

Derived fields:

- `is_superhost`
- `latitude`
- `longitude`

Important limitations:

- this is a snapshot dataset, not a daily booking history
- `nightly_price` is an observed listing price, not realized revenue
- there is no occupancy or booking outcome field

## `city_period_summary`

Purpose:

City-level benchmark context table. It provides seasonal market aggregates that can be used for benchmarking and contextual comparison.

Grain:

One row per `(city_name, period_label)`.

Primary key:

- `city_name`
- `period_label`

Most important fields for Goal 2:

- `nightly_price_median`
- `nightly_price_median_abs_deviation`
- `accommodates_count_median`
- `host_listing_count_median`
- `rating_score_median`
- `dominant_neighbourhood`
- `dominant_room_type`

Derived fields:

- none in the strong sense; this table is mostly normalized and renamed from an already aggregated source

Important limitations:

- aggregated dataset only
- cannot be used as property-level evidence by itself
- should be treated as market context, not as direct training labels for listings

## `neighbourhood_period_summary`

Purpose:

Neighbourhood-level benchmark context table. This is the local market view used to compare listings against the surrounding micro-market.

Grain:

One row per `(city_name, neighbourhood_name, period_label)`.

Primary key:

- `city_name`
- `neighbourhood_name`
- `period_label`

Most important fields for Goal 2:

- `nightly_price_median`
- `nightly_price_median_abs_deviation`
- `accommodates_count_median`
- `host_listing_count_median`
- `rating_score_median`
- `dominant_room_type`
- `room_type_entropy`

Derived fields:

- none in the strong sense; this table is also a normalized aggregate dataset

Important limitations:

- aggregated dataset only
- should be used as benchmark context, not as a replacement for listing-level modeling data

## `neighbourhood_reference`

Purpose:

Reference vocabulary for cleaned city and neighbourhood labels. It supports consistent joins between listing, grouped, and boundary datasets.

Grain:

One row per `(city_name, neighbourhood_name)`.

Primary key:

- `city_name`
- `neighbourhood_name`

Most important fields for Goal 2:

- `city_name`
- `neighbourhood_name`
- `neighbourhood_group_name`

Derived fields:

- none

Important limitations:

- `neighbourhood_group_name` is optional
- in practice this field is meaningful mainly for Venezia

## `neighbourhood_boundary`

Purpose:

Spatial boundary layer for maps and location-aware benchmark interfaces.

Grain:

One row per `boundary_id`.

Primary key:

- `boundary_id`

Most important fields for Goal 2:

- `city_name`
- `neighbourhood_name`
- `neighbourhood_group_name`
- `geometry_type`
- `geometry`

Derived fields:

- `boundary_id`
- `city_name` enriched from the reference table

Important limitations:

- this dataset is for spatial context, not direct price prediction
- one logical neighbourhood may have multiple boundary rows
- geometry is stored as a GeoJSON-compatible serialized payload

## Fast Join Guide

Use these joins by default:

- `listing_snapshot` -> `city_period_summary` on `city_name`, `period_label`
- `listing_snapshot` -> `neighbourhood_period_summary` on `city_name`, `neighbourhood_name`, `period_label`
- `listing_snapshot` -> `neighbourhood_reference` on `city_name`, `neighbourhood_name`
- `neighbourhood_boundary` -> `neighbourhood_reference` on cleaned neighbourhood vocabulary

## Modeling Advice

For the first Goal 2 model:

- start from `listing_snapshot`
- use grouped summary tables as benchmark context only
- use `neighbourhood_boundary` only if spatial features or maps are needed
- treat `neighbourhood_group_name` as a city-conditional feature, not a universal one
