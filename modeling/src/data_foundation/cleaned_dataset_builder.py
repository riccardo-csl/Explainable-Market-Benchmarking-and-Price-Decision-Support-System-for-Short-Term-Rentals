"""Build cleaned datasets from canonical raw inputs."""

from __future__ import annotations

from typing import Any

import pandas as pd

from .contracts import TargetDatasetContract
from .normalization import (
    geometry_to_json_text,
    normalize_city_label,
    normalize_period_label,
    normalize_superhost_flag,
    normalize_text,
    parse_coordinates,
    slugify_text,
)


def build_cleaned_datasets(
    raw_datasets: dict[str, pd.DataFrame],
    target_contracts: list[TargetDatasetContract],
) -> dict[str, pd.DataFrame]:
    contract_map = {contract.name: contract for contract in target_contracts}

    cleaned_reference = build_neighbourhood_reference(
        raw_datasets["neighbourhood_reference"],
        contract_map["neighbourhood_reference"],
    )
    cleaned_boundaries = build_neighbourhood_boundary(
        raw_datasets["neighbourhood_boundaries"],
        cleaned_reference,
        contract_map["neighbourhood_boundary"],
    )

    return {
        "listing_snapshot": build_listing_snapshot(
            raw_datasets["airbnb_listing_snapshots"],
            contract_map["listing_snapshot"],
        ),
        "city_period_summary": build_grouped_summary(
            raw_datasets["city_period_summary"],
            contract_map["city_period_summary"],
        ),
        "neighbourhood_period_summary": build_grouped_summary(
            raw_datasets["neighbourhood_period_summary"],
            contract_map["neighbourhood_period_summary"],
        ),
        "neighbourhood_reference": cleaned_reference,
        "neighbourhood_boundary": cleaned_boundaries,
    }


def build_listing_snapshot(raw_df: pd.DataFrame, contract: TargetDatasetContract) -> pd.DataFrame:
    dataframe = raw_df.copy()

    rename_map = {
        "Listings id": "listing_id",
        "Last year reviews": "reviews_last_twelve_months",
        "Host since": "host_since",
        "Host number of listings": "host_listing_count",
        "Neighbourhood": "neighbourhood_name",
        "Beds number": "beds_count",
        "Bedrooms number": "bedrooms_count",
        "Property type": "room_type",
        "Maximum allowed guests": "accommodates_count",
        "Price": "nightly_price",
        "Total reviews": "total_reviews",
        "Rating score": "rating_score",
        "Accuracy score": "accuracy_score",
        "Cleanliness score": "cleanliness_score",
        "Checkin score": "checkin_score",
        "Communication score": "communication_score",
        "Location score": "location_score",
        "Value for money score": "value_score",
        "Reviews per month": "reviews_per_month",
        "City": "city_name",
        "Season": "period_label",
        "Bathrooms number": "bathrooms_count",
        "Bathrooms type": "bathroom_type",
        "Date of scraping": "snapshot_date",
    }
    dataframe = dataframe.rename(columns=rename_map)

    coordinates = dataframe["Coordinates"].apply(parse_coordinates)
    dataframe["latitude"] = coordinates.apply(lambda item: item[0])
    dataframe["longitude"] = coordinates.apply(lambda item: item[1])
    dataframe["is_superhost"] = dataframe["Host is superhost"].apply(normalize_superhost_flag)

    for column in ["city_name", "neighbourhood_name", "room_type", "bathroom_type"]:
        dataframe[column] = dataframe[column].apply(normalize_text)
    dataframe["city_name"] = dataframe["city_name"].apply(normalize_city_label)
    dataframe["period_label"] = dataframe["period_label"].apply(normalize_period_label)

    integer_columns = [
        "listing_id",
        "reviews_last_twelve_months",
        "host_listing_count",
        "beds_count",
        "bedrooms_count",
        "accommodates_count",
        "total_reviews",
    ]
    float_columns = [
        "nightly_price",
        "rating_score",
        "accuracy_score",
        "cleanliness_score",
        "checkin_score",
        "communication_score",
        "location_score",
        "value_score",
        "reviews_per_month",
        "bathrooms_count",
        "latitude",
        "longitude",
    ]

    for column in integer_columns:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce").round().astype("Int64")
    for column in float_columns:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce").astype("Float64")

    dataframe["snapshot_date"] = pd.to_datetime(dataframe["snapshot_date"], errors="coerce")
    dataframe["host_since"] = pd.to_datetime(dataframe["host_since"], errors="coerce")
    dataframe["is_superhost"] = dataframe["is_superhost"].astype("boolean")

    dataframe = dataframe.drop(columns=["Coordinates", "Host is superhost"])
    dataframe = _reorder_columns_to_contract(dataframe, contract)
    return dataframe


def build_grouped_summary(raw_df: pd.DataFrame, contract: TargetDatasetContract) -> pd.DataFrame:
    dataframe = raw_df.copy()
    rename_map = {}
    for field in contract.fields:
        if len(field.source_columns) == 1 and field.source_columns[0] in dataframe.columns:
            rename_map[field.source_columns[0]] = field.name
    dataframe = dataframe.rename(columns=rename_map)

    if "city_name" in dataframe.columns:
        dataframe["city_name"] = dataframe["city_name"].apply(normalize_city_label)
    if "period_label" in dataframe.columns:
        dataframe["period_label"] = dataframe["period_label"].apply(normalize_period_label)
    for column in dataframe.columns:
        if column not in {"city_name", "period_label"} and dataframe[column].dtype == object:
            dataframe[column] = dataframe[column].apply(normalize_text)
    for column in dataframe.columns:
        if column not in {"city_name", "period_label", "dominant_neighbourhood", "dominant_room_type", "neighbourhood_name"}:
            if column.endswith("_median") or column.endswith("_median_abs_deviation") or column.endswith("_entropy"):
                dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce").astype("Float64")

    dataframe = _reorder_columns_to_contract(dataframe, contract)
    return dataframe


def build_neighbourhood_reference(raw_df: pd.DataFrame, contract: TargetDatasetContract) -> pd.DataFrame:
    dataframe = raw_df.copy().rename(
        columns={
            "city": "city_name",
            "neighbourhood": "neighbourhood_name",
            "neighbourhood_group": "neighbourhood_group_name",
        }
    )
    dataframe["city_name"] = dataframe["city_name"].apply(normalize_city_label)
    dataframe["neighbourhood_name"] = dataframe["neighbourhood_name"].apply(normalize_text)
    dataframe["neighbourhood_group_name"] = dataframe["neighbourhood_group_name"].apply(normalize_text)
    dataframe = _reorder_columns_to_contract(dataframe, contract)
    return dataframe


def build_neighbourhood_boundary(
    raw_df: pd.DataFrame,
    cleaned_reference: pd.DataFrame,
    contract: TargetDatasetContract,
) -> pd.DataFrame:
    dataframe = raw_df.copy()
    dataframe["neighbourhood_name"] = dataframe["neighbourhood"].apply(normalize_text)
    dataframe["neighbourhood_group_name"] = dataframe["neighbourhood_group"].apply(normalize_text)
    dataframe["geometry"] = dataframe["geometry"].apply(geometry_to_json_text)

    reference_columns = ["city_name", "neighbourhood_name", "neighbourhood_group_name"]
    reference = cleaned_reference[reference_columns].drop_duplicates(subset=["neighbourhood_name"])
    dataframe = dataframe.merge(
        reference,
        on="neighbourhood_name",
        how="left",
        suffixes=("", "_reference"),
    )
    dataframe["neighbourhood_group_name"] = dataframe["neighbourhood_group_name"].combine_first(
        dataframe["neighbourhood_group_name_reference"]
    )
    dataframe = dataframe.drop(columns=["neighbourhood", "neighbourhood_group", "neighbourhood_group_name_reference"])

    dataframe = _assign_boundary_ids(dataframe)
    dataframe = _reorder_columns_to_contract(dataframe, contract)
    return dataframe


def _assign_boundary_ids(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.copy()
    dataframe["_boundary_base_slug"] = dataframe.apply(_boundary_base_slug, axis=1)
    dataframe = dataframe.sort_values(["_boundary_base_slug", "raw_feature_index"], kind="stable").reset_index(drop=True)
    dataframe["_boundary_suffix"] = (
        dataframe.groupby("_boundary_base_slug").cumcount() + 1
    ).astype(str).str.zfill(3)
    dataframe["boundary_id"] = dataframe["_boundary_base_slug"] + "_" + dataframe["_boundary_suffix"]
    dataframe = dataframe.sort_values("raw_feature_index", kind="stable").reset_index(drop=True)
    dataframe = dataframe.drop(columns=["_boundary_base_slug", "_boundary_suffix", "raw_feature_index"])
    return dataframe


def _boundary_base_slug(row: pd.Series) -> str:
    parts = [
        slugify_text(row.get("city_name")),
        slugify_text(row.get("neighbourhood_name")),
    ]
    neighbourhood_group_name = row.get("neighbourhood_group_name")
    if neighbourhood_group_name is not None and not pd.isna(neighbourhood_group_name):
        parts.append(slugify_text(neighbourhood_group_name))
    return "_".join(parts)


def _reorder_columns_to_contract(dataframe: pd.DataFrame, contract: TargetDatasetContract) -> pd.DataFrame:
    ordered_columns = [field.name for field in contract.fields]
    missing_columns = [column for column in ordered_columns if column not in dataframe.columns]
    for column in missing_columns:
        dataframe[column] = pd.NA
    return dataframe[ordered_columns]
