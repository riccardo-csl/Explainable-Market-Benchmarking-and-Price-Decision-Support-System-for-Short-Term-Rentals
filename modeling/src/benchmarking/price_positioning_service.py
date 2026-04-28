"""End-to-end Goal 2 decision payload builder."""

from __future__ import annotations

from typing import Any

import pandas as pd

from benchmarking.benchmark_range_calculator import calculate_benchmark_range, classify_price_positioning
from benchmarking.listing_similarity_engine import select_comparable_listings
from explainability.local_explanation_builder import build_local_explanation_payload


def build_price_decision_payload(
    feature_frame: pd.DataFrame,
    target_listing: pd.Series,
    estimated_market_price: float,
    champion_model_name: str,
    fallback_model_name: str,
    linear_explanation_context: dict[str, Any],
    neighbourhood_period_summary: pd.DataFrame,
    city_period_summary: pd.DataFrame,
) -> dict[str, Any]:
    """Return the product-facing Goal 2 payload for one listing."""

    comparable_result = select_comparable_listings(feature_frame, target_listing)
    benchmark_range = calculate_benchmark_range(
        target_listing,
        comparable_result.comparables,
        neighbourhood_period_summary,
        city_period_summary,
    )
    price_positioning_label = classify_price_positioning(
        float(target_listing["nightly_price"]),
        benchmark_range,
    )
    local_explanation = build_local_explanation_payload(
        target_listing=target_listing,
        comparables=comparable_result.comparables,
        explanation_context=linear_explanation_context,
    )
    comparable_payload = []
    for record in comparable_result.comparables.to_dict(orient="records"):
        normalized_record = dict(record)
        if "snapshot_date" in normalized_record:
            normalized_record["snapshot_date"] = pd.Timestamp(normalized_record["snapshot_date"]).date().isoformat()
        comparable_payload.append(normalized_record)
    return {
        "listing_id": int(target_listing["listing_id"]),
        "snapshot_date": pd.Timestamp(target_listing["snapshot_date"]).date().isoformat(),
        "city_name": target_listing["city_name"],
        "period_label": target_listing["period_label"],
        "primary_decision_signal": "benchmark_range",
        "decision_policy": "benchmark_led_positioning",
        "decision_signal_summary": (
            "The benchmark range is the primary decision signal. "
            "The model price estimate is retained as a supporting signal."
        ),
        "benchmark_lower_bound": float(benchmark_range.lower_bound),
        "benchmark_upper_bound": float(benchmark_range.upper_bound),
        "price_positioning_label": price_positioning_label,
        "benchmark_source": benchmark_range.source,
        "estimated_market_price": float(estimated_market_price),
        "model_estimate_role": "supporting_signal",
        "champion_model_name": champion_model_name,
        "fallback_model_name": fallback_model_name,
        "selected_comparables": comparable_payload,
        "local_explanation": local_explanation,
        "fallback_used": bool(benchmark_range.fallback_used),
    }
