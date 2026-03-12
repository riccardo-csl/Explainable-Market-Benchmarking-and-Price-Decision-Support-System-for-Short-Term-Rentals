import pandas as pd

from evaluation.eda_summary_builder import (
    build_accommodates_band_median_prices,
    build_median_price_by_city,
    build_median_price_by_city_and_period,
    build_neighbourhood_price_extremes,
    build_room_type_share,
    build_rows_by_city,
    build_rows_by_city_and_period,
)


def _sample_listing_snapshot() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "listing_id": 1,
                "city_name": "Roma",
                "period_label": "Early Summer",
                "room_type": "Entire home",
                "nightly_price": 200.0,
                "accommodates_count": 4,
                "neighbourhood_name": "Centro",
            },
            {
                "listing_id": 2,
                "city_name": "Roma",
                "period_label": "Early Winter",
                "room_type": "Private room",
                "nightly_price": 80.0,
                "accommodates_count": 2,
                "neighbourhood_name": "Centro",
            },
            {
                "listing_id": 3,
                "city_name": "Milano",
                "period_label": "Early Summer",
                "room_type": "Entire home",
                "nightly_price": 150.0,
                "accommodates_count": 3,
                "neighbourhood_name": "Duomo",
            },
            {
                "listing_id": 4,
                "city_name": "Milano",
                "period_label": "Early Spring",
                "room_type": "Hotel room",
                "nightly_price": 140.0,
                "accommodates_count": 1,
                "neighbourhood_name": "Duomo",
            },
            {
                "listing_id": 5,
                "city_name": "Napoli",
                "period_label": "Early Autumn",
                "room_type": "Shared room",
                "nightly_price": 40.0,
                "accommodates_count": 1,
                "neighbourhood_name": "Mercato",
            },
            {
                "listing_id": 6,
                "city_name": "Napoli",
                "period_label": "Early Summer",
                "room_type": "Private room",
                "nightly_price": 60.0,
                "accommodates_count": 6,
                "neighbourhood_name": "Mercato",
            },
            {
                "listing_id": 7,
                "city_name": "Roma",
                "period_label": "Early Autumn",
                "room_type": "Entire home",
                "nightly_price": 220.0,
                "accommodates_count": 8,
                "neighbourhood_name": "Centro",
            },
        ]
    )


def test_rows_by_city_and_room_type_share_use_expected_ordering() -> None:
    listing_snapshot = _sample_listing_snapshot()

    rows_by_city = build_rows_by_city(listing_snapshot)
    rows_by_city_and_period = build_rows_by_city_and_period(listing_snapshot)
    room_type_share = build_room_type_share(listing_snapshot)

    assert rows_by_city.to_dict() == {"Roma": 3, "Milano": 2, "Napoli": 2}
    assert list(rows_by_city_and_period.columns) == [
        "Early Spring",
        "Early Summer",
        "Early Autumn",
        "Early Winter",
    ]
    assert round(float(room_type_share["Entire home"]), 3) == 0.429


def test_price_summaries_and_capacity_bands_return_expected_medians() -> None:
    listing_snapshot = _sample_listing_snapshot()

    city_medians = build_median_price_by_city(listing_snapshot)
    city_period_medians = build_median_price_by_city_and_period(listing_snapshot)
    accommodates_bands = build_accommodates_band_median_prices(listing_snapshot)

    assert city_medians.to_dict() == {"Roma": 200.0, "Milano": 145.0, "Napoli": 50.0}
    assert city_period_medians.loc["Roma", "Early Summer"] == 200.0
    assert accommodates_bands.to_dict() == {
        "1-2 guests": 80.0,
        "3-4 guests": 175.0,
        "5-6 guests": 60.0,
        "7+ guests": 220.0,
    }


def test_neighbourhood_price_extremes_split_top_and_lower_segments() -> None:
    listing_snapshot = _sample_listing_snapshot()

    extremes = build_neighbourhood_price_extremes(
        listing_snapshot,
        min_listing_rows=1,
        top_n=1,
        bottom_n=1,
    )

    assert len(extremes.top_segment) == 1
    assert len(extremes.bottom_segment) == 1
    assert extremes.top_segment.iloc[0]["segment"] == "Top priced"
    assert extremes.bottom_segment.iloc[0]["segment"] == "Lower priced"
    assert extremes.top_segment.iloc[0]["label"] == "Roma\nCentro"
