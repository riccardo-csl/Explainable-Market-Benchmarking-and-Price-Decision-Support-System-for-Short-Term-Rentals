"""Practical local explanations for Goal 2 payloads."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def build_linear_explanation_context(
    linear_pipeline: Any,
    raw_feature_frame: pd.DataFrame,
    *,
    feature_columns: list[str],
) -> dict[str, Any]:
    """Return reusable explanation metadata from the linear model."""

    preprocessor = linear_pipeline.named_steps["preprocess"]
    transformed = preprocessor.transform(raw_feature_frame[feature_columns])
    feature_names = list(preprocessor.get_feature_names_out())
    coefficients = linear_pipeline.named_steps["model"].coef_
    return {
        "linear_pipeline": linear_pipeline,
        "feature_names": feature_names,
        "coefficients": np.asarray(coefficients, dtype=float),
        "feature_columns": feature_columns,
    }


def build_local_explanation_payload(
    *,
    target_listing: pd.Series,
    comparables: pd.DataFrame,
    explanation_context: dict[str, Any],
) -> dict[str, Any]:
    """Build a simple local explanation payload using linear contributions."""

    linear_pipeline = explanation_context["linear_pipeline"]
    feature_names = explanation_context["feature_names"]
    coefficients = explanation_context["coefficients"]
    feature_columns = explanation_context["feature_columns"]

    target_frame = pd.DataFrame([target_listing[feature_columns].to_dict()])
    transformed = linear_pipeline.named_steps["preprocess"].transform(target_frame)
    transformed_row = np.asarray(transformed[0], dtype=float)
    contributions = transformed_row * coefficients

    aggregated: dict[str, float] = {}
    for feature_name, transformed_value, contribution in zip(feature_names, transformed_row, contributions):
        display_name = _display_name_for_contribution(
            feature_name=feature_name,
            transformed_value=float(transformed_value),
            target_listing=target_listing,
        )
        if display_name is None:
            continue
        aggregated[display_name] = aggregated.get(display_name, 0.0) + float(contribution)

    upward = sorted(
        (
            {"feature": feature_name, "contribution": value}
            for feature_name, value in aggregated.items()
            if value > 0
        ),
        key=lambda item: item["contribution"],
        reverse=True,
    )[:3]
    downward = sorted(
        (
            {"feature": feature_name, "contribution": value}
            for feature_name, value in aggregated.items()
            if value < 0
        ),
        key=lambda item: item["contribution"],
    )[:3]

    comparable_median_price = (
        float(comparables["nightly_price"].median()) if not comparables.empty else float(target_listing["nightly_price"])
    )
    return {
        "source_model_name": "linear_baseline",
        "top_upward_drivers": upward,
        "top_downward_drivers": downward,
        "comparable_median_price": comparable_median_price,
    }


def _display_name_for_contribution(
    *,
    feature_name: str,
    transformed_value: float,
    target_listing: pd.Series,
) -> str | None:
    _, _, remainder = feature_name.partition("__")
    if remainder.startswith(
        (
            "latitude",
            "longitude",
            "distance_to_city_center_km",
            "distance_to_neighbourhood_center_km",
        )
    ):
        return "location"

    if remainder.startswith("room_type_"):
        return f"room_type={remainder.removeprefix('room_type_')}" if transformed_value > 0 else None
    if remainder.startswith("bathroom_type_"):
        return (
            f"bathroom_type={remainder.removeprefix('bathroom_type_')}"
            if transformed_value > 0
            else None
        )
    if remainder.startswith("is_superhost_"):
        return "superhost_status" if remainder.endswith("_True") and transformed_value > 0 else None
    if remainder.startswith("season_peak_flag_"):
        return "peak_season" if remainder.endswith("_True") and transformed_value > 0 else None
    if remainder.startswith("season_shoulder_flag_"):
        return "shoulder_season" if remainder.endswith("_True") and transformed_value > 0 else None
    if remainder.startswith("venezia_group_name_"):
        if target_listing.get("city_name") != "Venezia":
            return None
        return (
            f"venezia_zone={remainder.removeprefix('venezia_group_name_')}"
            if transformed_value > 0
            else None
        )

    return _strip_preprocessor_prefix(feature_name)


def _strip_preprocessor_prefix(feature_name: str) -> str:
    _, _, remainder = feature_name.partition("__")
    for base_name in (
        "distance_to_neighbourhood_center_km",
        "distance_to_city_center_km",
        "reviews_last_twelve_months",
        "host_listing_count",
        "accommodates_count",
        "bedrooms_count",
        "bathrooms_count",
        "reviews_per_month",
        "communication_score",
        "cleanliness_score",
        "accuracy_score",
        "location_score",
        "season_peak_flag",
        "season_shoulder_flag",
        "venezia_group_name",
        "bathroom_type",
        "is_superhost",
        "room_type",
        "beds_count",
        "rating_score",
        "value_score",
        "checkin_score",
        "longitude",
        "latitude",
        "total_reviews",
        "host_tenure_days",
    ):
        if remainder == base_name or remainder.startswith(f"{base_name}_"):
            return base_name
    return remainder
