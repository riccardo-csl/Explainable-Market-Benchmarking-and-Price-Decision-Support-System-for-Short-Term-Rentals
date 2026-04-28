"""Data profiling helpers for Goal 2."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass(frozen=True)
class DataProfileReport:
    """Compact profile summary for the Goal 2 modeling dataset."""

    row_count: int
    unique_listing_count: int
    target_median: float
    target_mean: float
    target_q1: float
    target_q3: float
    city_counts: dict[str, int]
    period_counts: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_data_profile_report(dataframe: pd.DataFrame) -> DataProfileReport:
    """Return a compact profile for the modeling dataset."""

    return DataProfileReport(
        row_count=int(len(dataframe)),
        unique_listing_count=int(dataframe["listing_id"].nunique()),
        target_median=float(dataframe["nightly_price"].median()),
        target_mean=float(dataframe["nightly_price"].mean()),
        target_q1=float(dataframe["nightly_price"].quantile(0.25)),
        target_q3=float(dataframe["nightly_price"].quantile(0.75)),
        city_counts={key: int(value) for key, value in dataframe["city_name"].value_counts().sort_index().items()},
        period_counts={key: int(value) for key, value in dataframe["period_label"].value_counts().sort_index().items()},
    )
