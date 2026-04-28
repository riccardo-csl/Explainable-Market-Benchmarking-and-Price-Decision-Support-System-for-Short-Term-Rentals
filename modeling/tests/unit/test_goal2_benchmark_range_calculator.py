import pandas as pd

from benchmarking.benchmark_range_calculator import calculate_benchmark_range, classify_price_positioning


def test_calculate_benchmark_range_uses_quartiles_for_large_comparable_sets() -> None:
    comparables = pd.DataFrame({"nightly_price": list(range(100, 115))})
    neighbourhood_period_summary = pd.DataFrame()
    city_period_summary = pd.DataFrame()
    target_listing = pd.Series(
        {"city_name": "Roma", "neighbourhood_name": "Centro", "period_label": "Early Summer", "nightly_price": 110.0}
    )

    benchmark_range = calculate_benchmark_range(
        target_listing,
        comparables,
        neighbourhood_period_summary,
        city_period_summary,
    )

    assert benchmark_range.source == "comparable_iqr"
    assert benchmark_range.lower_bound == 103.5
    assert benchmark_range.upper_bound == 110.5


def test_calculate_benchmark_range_falls_back_to_neighbourhood_summary_when_comparables_are_sparse() -> None:
    comparables = pd.DataFrame({"nightly_price": [100.0, 102.0]})
    neighbourhood_period_summary = pd.DataFrame(
        [
            {
                "city_name": "Roma",
                "neighbourhood_name": "Centro",
                "period_label": "Early Summer",
                "nightly_price_median": 120.0,
                "nightly_price_median_abs_deviation": 10.0,
            }
        ]
    )
    city_period_summary = pd.DataFrame()
    target_listing = pd.Series(
        {"city_name": "Roma", "neighbourhood_name": "Centro", "period_label": "Early Summer", "nightly_price": 110.0}
    )

    benchmark_range = calculate_benchmark_range(
        target_listing,
        comparables,
        neighbourhood_period_summary,
        city_period_summary,
    )

    assert benchmark_range.source == "neighbourhood_period_summary"
    assert benchmark_range.fallback_used is True
    assert classify_price_positioning(110.0, benchmark_range) == "aligned"
