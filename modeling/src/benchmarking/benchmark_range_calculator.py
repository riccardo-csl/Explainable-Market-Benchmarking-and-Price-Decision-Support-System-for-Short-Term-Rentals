"""Benchmark range calculation for Goal 2."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass(frozen=True)
class BenchmarkRange:
    """Benchmark range plus provenance metadata."""

    lower_bound: float
    upper_bound: float
    source: str
    comparable_count: int
    fallback_used: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def calculate_benchmark_range(
    target_listing: pd.Series,
    comparables: pd.DataFrame,
    neighbourhood_period_summary: pd.DataFrame,
    city_period_summary: pd.DataFrame,
) -> BenchmarkRange:
    """Calculate the benchmark range using comparables first, then aggregate fallbacks."""

    comparable_count = len(comparables)
    if comparable_count >= 15:
        return _quartile_range(comparables["nightly_price"], comparable_count=comparable_count)
    if comparable_count >= 5:
        return _mad_range(
            comparables["nightly_price"],
            source="comparable_mad",
            comparable_count=comparable_count,
            fallback_used=False,
        )

    neighbourhood_match = neighbourhood_period_summary[
        (neighbourhood_period_summary["city_name"] == target_listing["city_name"])
        & (neighbourhood_period_summary["neighbourhood_name"] == target_listing["neighbourhood_name"])
        & (neighbourhood_period_summary["period_label"] == target_listing["period_label"])
    ]
    if not neighbourhood_match.empty:
        row = neighbourhood_match.iloc[0]
        return _summary_range(
            median=float(row["nightly_price_median"]),
            mad=float(row["nightly_price_median_abs_deviation"]),
            source="neighbourhood_period_summary",
        )

    city_match = city_period_summary[
        (city_period_summary["city_name"] == target_listing["city_name"])
        & (city_period_summary["period_label"] == target_listing["period_label"])
    ]
    if city_match.empty:
        median_price = float(target_listing["nightly_price"])
        return BenchmarkRange(
            lower_bound=max(median_price * 0.9, 1.0),
            upper_bound=median_price * 1.1,
            source="listing_price_fallback",
            comparable_count=comparable_count,
            fallback_used=True,
        )

    row = city_match.iloc[0]
    return _summary_range(
        median=float(row["nightly_price_median"]),
        mad=float(row["nightly_price_median_abs_deviation"]),
        source="city_period_summary",
    )


def classify_price_positioning(
    observed_price: float,
    benchmark_range: BenchmarkRange,
) -> str:
    """Classify the observed price relative to the benchmark range."""

    if observed_price < benchmark_range.lower_bound:
        return "underpriced"
    if observed_price > benchmark_range.upper_bound:
        return "overpriced"
    return "aligned"


def _quartile_range(prices: pd.Series, *, comparable_count: int) -> BenchmarkRange:
    q1 = float(prices.quantile(0.25))
    q3 = float(prices.quantile(0.75))
    return BenchmarkRange(
        lower_bound=max(q1, 1.0),
        upper_bound=max(q3, q1),
        source="comparable_iqr",
        comparable_count=comparable_count,
        fallback_used=False,
    )


def _mad_range(
    prices: pd.Series,
    *,
    source: str,
    comparable_count: int,
    fallback_used: bool,
) -> BenchmarkRange:
    median = float(prices.median())
    mad = float((prices - median).abs().median())
    width = 1.4826 * mad
    return BenchmarkRange(
        lower_bound=max(median - width, 1.0),
        upper_bound=max(median + width, median),
        source=source,
        comparable_count=comparable_count,
        fallback_used=fallback_used,
    )


def _summary_range(median: float, mad: float, *, source: str) -> BenchmarkRange:
    width = 1.4826 * mad
    return BenchmarkRange(
        lower_bound=max(median - width, 1.0),
        upper_bound=max(median + width, median),
        source=source,
        comparable_count=0,
        fallback_used=True,
    )
