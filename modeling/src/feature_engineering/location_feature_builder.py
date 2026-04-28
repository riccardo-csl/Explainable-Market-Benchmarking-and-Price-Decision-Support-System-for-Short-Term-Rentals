"""Location feature helpers for Goal 2."""

from __future__ import annotations

import math

import pandas as pd


EARTH_RADIUS_KM = 6371.0088


def haversine_distance_km(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    """Return the haversine distance between two lat/lon pairs in kilometers."""

    lat_a = math.radians(latitude_a)
    lon_a = math.radians(longitude_a)
    lat_b = math.radians(latitude_b)
    lon_b = math.radians(longitude_b)
    delta_lat = lat_b - lat_a
    delta_lon = lon_b - lon_a
    haversine = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat_a) * math.cos(lat_b) * math.sin(delta_lon / 2) ** 2
    )
    central_angle = 2 * math.asin(math.sqrt(haversine))
    return EARTH_RADIUS_KM * central_angle


def compute_centroid_lookup(
    dataframe: pd.DataFrame,
    group_columns: list[str],
) -> pd.DataFrame:
    """Return centroid coordinates for each requested group."""

    centroid = (
        dataframe.groupby(group_columns, observed=True)[["latitude", "longitude"]]
        .median()
        .rename(columns={"latitude": "centroid_latitude", "longitude": "centroid_longitude"})
        .reset_index()
    )
    return centroid


def attach_distance_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Add city and neighbourhood distance features."""

    city_centroids = compute_centroid_lookup(dataframe, ["city_name"])
    neighbourhood_centroids = compute_centroid_lookup(
        dataframe,
        ["city_name", "neighbourhood_name"],
    )

    enriched = dataframe.merge(city_centroids, on="city_name", how="left")
    enriched = enriched.merge(
        neighbourhood_centroids,
        on=["city_name", "neighbourhood_name"],
        how="left",
        suffixes=("_city", "_neighbourhood"),
    )
    enriched["distance_to_city_center_km"] = enriched.apply(
        lambda row: haversine_distance_km(
            row["latitude"],
            row["longitude"],
            row["centroid_latitude_city"],
            row["centroid_longitude_city"],
        ),
        axis=1,
    )
    enriched["distance_to_neighbourhood_center_km"] = enriched.apply(
        lambda row: haversine_distance_km(
            row["latitude"],
            row["longitude"],
            row["centroid_latitude_neighbourhood"],
            row["centroid_longitude_neighbourhood"],
        ),
        axis=1,
    )
    return enriched.drop(
        columns=[
            "centroid_latitude_city",
            "centroid_longitude_city",
            "centroid_latitude_neighbourhood",
            "centroid_longitude_neighbourhood",
        ]
    )
