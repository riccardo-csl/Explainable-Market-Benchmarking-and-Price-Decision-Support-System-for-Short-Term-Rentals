"""Comparable listing selection and similarity scoring for Goal 2."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from feature_engineering.location_feature_builder import haversine_distance_km


@dataclass(frozen=True)
class ComparableSearchResult:
    """Comparable selection result plus fallback metadata."""

    comparables: pd.DataFrame
    used_city_fallback: bool


def select_comparable_listings(
    feature_frame: pd.DataFrame,
    target_listing: pd.Series,
    *,
    top_n: int = 10,
    min_local_pool: int = 5,
) -> ComparableSearchResult:
    """Select the top comparable listings for a target row."""

    candidate_frame = feature_frame.copy()
    candidate_frame = candidate_frame[
        (candidate_frame["listing_id"] != target_listing["listing_id"])
        | (candidate_frame["snapshot_date"] != target_listing["snapshot_date"])
    ]
    strict_pool = candidate_frame[
        (candidate_frame["city_name"] == target_listing["city_name"])
        & (candidate_frame["period_label"] == target_listing["period_label"])
        & (candidate_frame["room_type"] == target_listing["room_type"])
        & (candidate_frame["neighbourhood_name"] == target_listing["neighbourhood_name"])
    ]

    required_local_pool = min(top_n, min_local_pool)
    if len(strict_pool) >= required_local_pool:
        pool = strict_pool
        used_city_fallback = False
    else:
        pool = candidate_frame[
            (candidate_frame["city_name"] == target_listing["city_name"])
            & (candidate_frame["period_label"] == target_listing["period_label"])
            & (candidate_frame["room_type"] == target_listing["room_type"])
        ]
        used_city_fallback = True

    if pool.empty:
        return ComparableSearchResult(comparables=pool.copy(), used_city_fallback=used_city_fallback)

    scored = pool.copy()
    scored["distance_km"] = scored.apply(
        lambda row: haversine_distance_km(
            float(target_listing["latitude"]),
            float(target_listing["longitude"]),
            float(row["latitude"]),
            float(row["longitude"]),
        ),
        axis=1,
    )
    scored["similarity_score"] = scored.apply(
        lambda row: _similarity_score(target_listing, row, used_city_fallback=used_city_fallback),
        axis=1,
    )
    scored["used_city_fallback"] = used_city_fallback
    comparable_columns = [
        "listing_id",
        "snapshot_date",
        "city_name",
        "neighbourhood_name",
        "room_type",
        "nightly_price",
        "distance_km",
        "similarity_score",
        "used_city_fallback",
    ]
    ranked = scored.sort_values(
        ["similarity_score", "nightly_price"],
        ascending=[False, True],
        kind="stable",
    ).head(top_n)
    return ComparableSearchResult(
        comparables=ranked[comparable_columns].reset_index(drop=True),
        used_city_fallback=used_city_fallback,
    )


def _similarity_score(
    target_listing: pd.Series,
    candidate_listing: pd.Series,
    *,
    used_city_fallback: bool,
) -> float:
    neighbourhood_bonus = 0.0 if used_city_fallback else 3.0
    capacity_closeness = _bounded_closeness(
        float(target_listing["accommodates_count"]),
        float(candidate_listing["accommodates_count"]),
        tolerance=2.0,
    )
    beds_closeness = _bounded_closeness(
        float(target_listing["beds_count"]),
        float(candidate_listing["beds_count"]),
        tolerance=2.0,
    )
    bedrooms_closeness = _bounded_closeness(
        float(target_listing["bedrooms_count"]),
        float(candidate_listing["bedrooms_count"]),
        tolerance=2.0,
    )
    rating_closeness = _bounded_closeness(
        float(target_listing["rating_score"]),
        float(candidate_listing["rating_score"]),
        tolerance=10.0,
    )
    distance_score = float(np.exp(-float(candidate_listing["distance_km"]) / 3.0))
    return (
        2.0
        + neighbourhood_bonus
        + 2.0 * capacity_closeness
        + 1.0 * beds_closeness
        + 1.0 * bedrooms_closeness
        + 0.75 * rating_closeness
        + 1.25 * distance_score
    )


def _bounded_closeness(reference: float, observed: float, *, tolerance: float) -> float:
    gap = abs(reference - observed)
    closeness = 1.0 - min(gap / tolerance, 1.0)
    return float(max(closeness, 0.0))
