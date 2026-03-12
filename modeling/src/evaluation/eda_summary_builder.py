"""Summary builders for repeatable EDA chart generation."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


PERIOD_ORDER = [
    "Early Spring",
    "Early Summer",
    "Early Autumn",
    "Early Winter",
]

ROOM_TYPE_ORDER = [
    "Entire home",
    "Private room",
    "Hotel room",
    "Shared room",
]

ACCOMMODATES_BAND_ORDER = [
    "1-2 guests",
    "3-4 guests",
    "5-6 guests",
    "7+ guests",
]


@dataclass(frozen=True)
class NeighbourhoodPriceExtremes:
    """Selected high-price and low-price neighbourhood summaries."""

    top_segment: pd.DataFrame
    bottom_segment: pd.DataFrame

    def combined(self) -> pd.DataFrame:
        return pd.concat([self.top_segment, self.bottom_segment], ignore_index=True)


def build_rows_by_city(listing_snapshot: pd.DataFrame) -> pd.Series:
    """Return listing snapshot row counts by city."""

    return listing_snapshot.groupby("city_name").size().sort_values(ascending=False)


def build_rows_by_city_and_period(listing_snapshot: pd.DataFrame) -> pd.DataFrame:
    """Return listing snapshot row counts by city and seasonal period."""

    grouped = listing_snapshot.groupby(["city_name", "period_label"]).size().unstack(fill_value=0)
    available_periods = [period for period in PERIOD_ORDER if period in grouped.columns]
    remaining_periods = [period for period in grouped.columns if period not in available_periods]
    return grouped.reindex(columns=[*available_periods, *remaining_periods])


def build_room_type_share(listing_snapshot: pd.DataFrame) -> pd.Series:
    """Return overall room type share as fractions between zero and one."""

    counts = listing_snapshot["room_type"].value_counts(normalize=True)
    available_room_types = [room_type for room_type in ROOM_TYPE_ORDER if room_type in counts.index]
    remaining_room_types = [room_type for room_type in counts.index if room_type not in available_room_types]
    return counts.reindex([*available_room_types, *remaining_room_types])


def build_nightly_price_distribution(listing_snapshot: pd.DataFrame) -> pd.Series:
    """Return the nightly price series used for distribution charts."""

    return listing_snapshot["nightly_price"].astype(float)


def build_median_price_by_city(listing_snapshot: pd.DataFrame) -> pd.Series:
    """Return median nightly price by city."""

    return listing_snapshot.groupby("city_name")["nightly_price"].median().sort_values(ascending=False)


def build_median_price_by_city_and_period(listing_snapshot: pd.DataFrame) -> pd.DataFrame:
    """Return median nightly price by city and period."""

    pivot = listing_snapshot.pivot_table(
        index="city_name",
        columns="period_label",
        values="nightly_price",
        aggfunc="median",
    )
    city_order = list(build_median_price_by_city(listing_snapshot).index)
    available_periods = [period for period in PERIOD_ORDER if period in pivot.columns]
    remaining_periods = [period for period in pivot.columns if period not in available_periods]
    return pivot.reindex(index=city_order, columns=[*available_periods, *remaining_periods])


def build_median_price_by_room_type(listing_snapshot: pd.DataFrame) -> pd.Series:
    """Return median nightly price by room type."""

    medians = listing_snapshot.groupby("room_type")["nightly_price"].median()
    available_room_types = [room_type for room_type in ROOM_TYPE_ORDER if room_type in medians.index]
    remaining_room_types = [room_type for room_type in medians.index if room_type not in available_room_types]
    return medians.reindex([*available_room_types, *remaining_room_types])


def build_accommodates_band_median_prices(listing_snapshot: pd.DataFrame) -> pd.Series:
    """Return median nightly price by guest-capacity band."""

    accommodates_band = pd.cut(
        listing_snapshot["accommodates_count"],
        bins=[0, 2, 4, 6, float("inf")],
        labels=ACCOMMODATES_BAND_ORDER,
        include_lowest=True,
    )
    medians = listing_snapshot.assign(accommodates_band=accommodates_band).groupby(
        "accommodates_band", observed=True
    )["nightly_price"].median()
    return medians.reindex(ACCOMMODATES_BAND_ORDER).dropna()


def build_neighbourhood_price_extremes(
    listing_snapshot: pd.DataFrame,
    *,
    min_listing_rows: int = 200,
    top_n: int = 5,
    bottom_n: int = 5,
) -> NeighbourhoodPriceExtremes:
    """Return neighbourhood price extremes filtered by minimum listing volume."""

    grouped = (
        listing_snapshot.groupby(["city_name", "neighbourhood_name"])
        .agg(
            listing_rows=("listing_id", "count"),
            median_nightly_price=("nightly_price", "median"),
        )
        .reset_index()
    )
    filtered = grouped[grouped["listing_rows"] >= min_listing_rows].copy()
    filtered["label"] = filtered["city_name"] + "\n" + filtered["neighbourhood_name"]

    top_segment = filtered.nlargest(top_n, "median_nightly_price").copy()
    top_segment["segment"] = "Top priced"

    bottom_segment = filtered.nsmallest(bottom_n, "median_nightly_price").copy()
    bottom_segment["segment"] = "Lower priced"

    return NeighbourhoodPriceExtremes(
        top_segment=top_segment,
        bottom_segment=bottom_segment,
    )

