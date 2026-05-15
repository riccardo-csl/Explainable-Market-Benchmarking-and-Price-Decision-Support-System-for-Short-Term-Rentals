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
    model_estimate_interval_calibration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the product-facing Goal 2 payload for one listing."""

    model_estimate_interval = build_model_estimate_interval(
        estimated_market_price=estimated_market_price,
        calibration=model_estimate_interval_calibration,
    )
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
    model_benchmark_agreement = classify_model_benchmark_agreement(
        estimated_market_price=float(estimated_market_price),
        benchmark_lower_bound=float(benchmark_range.lower_bound),
        benchmark_upper_bound=float(benchmark_range.upper_bound),
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
        **model_estimate_interval,
        "model_estimate_role": "supporting_signal",
        **model_benchmark_agreement,
        "champion_model_name": champion_model_name,
        "fallback_model_name": fallback_model_name,
        "selected_comparables": comparable_payload,
        "local_explanation": local_explanation,
        "fallback_used": bool(benchmark_range.fallback_used),
    }


def build_model_estimate_interval(
    *,
    estimated_market_price: float,
    calibration: dict[str, Any] | None,
) -> dict[str, float | str | None]:
    """Return a conservative model estimate interval from residual calibration."""

    if not calibration:
        return {
            "model_estimate_lower_bound": float(estimated_market_price),
            "model_estimate_upper_bound": float(estimated_market_price),
            "model_estimate_interval_confidence_level": None,
            "model_estimate_interval_source": "unavailable",
        }

    lower_residual = float(calibration["lower_residual_quantile"])
    upper_residual = float(calibration["upper_residual_quantile"])
    raw_lower = float(estimated_market_price) + lower_residual
    raw_upper = float(estimated_market_price) + upper_residual
    lower_bound = max(0.0, min(raw_lower, raw_upper, float(estimated_market_price)))
    upper_bound = max(raw_lower, raw_upper, float(estimated_market_price))
    return {
        "model_estimate_lower_bound": float(lower_bound),
        "model_estimate_upper_bound": float(upper_bound),
        "model_estimate_interval_confidence_level": float(calibration["confidence_level"]),
        "model_estimate_interval_source": str(calibration["source"]),
    }


def classify_model_benchmark_agreement(
    *,
    estimated_market_price: float,
    benchmark_lower_bound: float,
    benchmark_upper_bound: float,
) -> dict[str, float | str]:
    """Classify whether the model point estimate supports the benchmark range."""

    if benchmark_lower_bound <= estimated_market_price <= benchmark_upper_bound:
        return {
            "model_benchmark_agreement_label": "strong",
            "model_benchmark_gap_amount": 0.0,
            "model_benchmark_gap_ratio": 0.0,
            "model_benchmark_agreement_summary": "Model estimate sits inside the benchmark range.",
        }

    if estimated_market_price < benchmark_lower_bound:
        gap_amount = benchmark_lower_bound - estimated_market_price
        direction = "below"
    else:
        gap_amount = estimated_market_price - benchmark_upper_bound
        direction = "above"

    benchmark_width = max(benchmark_upper_bound - benchmark_lower_bound, 1.0)
    gap_ratio = gap_amount / benchmark_width
    label = "medium" if gap_ratio <= 0.25 else "weak"
    distance_note = "close to" if label == "medium" else "far from"

    return {
        "model_benchmark_agreement_label": label,
        "model_benchmark_gap_amount": float(gap_amount),
        "model_benchmark_gap_ratio": float(gap_ratio),
        "model_benchmark_agreement_summary": (
            f"Model estimate is {distance_note} the benchmark range and sits {direction} it."
        ),
    }
