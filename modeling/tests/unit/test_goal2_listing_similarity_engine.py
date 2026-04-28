import pandas as pd

from benchmarking.listing_similarity_engine import select_comparable_listings


def test_select_comparable_listings_prefers_same_neighbourhood_pool() -> None:
    feature_frame = pd.DataFrame(
        [
            {
                "listing_id": 1,
                "snapshot_date": "2024-06-15",
                "city_name": "Roma",
                "period_label": "Early Summer",
                "neighbourhood_name": "Centro",
                "room_type": "Entire home",
                "nightly_price": 150.0,
                "latitude": 41.9,
                "longitude": 12.49,
                "accommodates_count": 2,
                "beds_count": 1,
                "bedrooms_count": 1,
                "rating_score": 95.0,
            },
            {
                "listing_id": 2,
                "snapshot_date": "2024-06-15",
                "city_name": "Roma",
                "period_label": "Early Summer",
                "neighbourhood_name": "Centro",
                "room_type": "Entire home",
                "nightly_price": 148.0,
                "latitude": 41.901,
                "longitude": 12.491,
                "accommodates_count": 2,
                "beds_count": 1,
                "bedrooms_count": 1,
                "rating_score": 94.0,
            },
            {
                "listing_id": 3,
                "snapshot_date": "2024-06-15",
                "city_name": "Roma",
                "period_label": "Early Summer",
                "neighbourhood_name": "Centro",
                "room_type": "Entire home",
                "nightly_price": 151.0,
                "latitude": 41.902,
                "longitude": 12.492,
                "accommodates_count": 2,
                "beds_count": 1,
                "bedrooms_count": 1,
                "rating_score": 96.0,
            },
            {
                "listing_id": 4,
                "snapshot_date": "2024-06-15",
                "city_name": "Roma",
                "period_label": "Early Summer",
                "neighbourhood_name": "Centro",
                "room_type": "Entire home",
                "nightly_price": 155.0,
                "latitude": 41.903,
                "longitude": 12.493,
                "accommodates_count": 2,
                "beds_count": 2,
                "bedrooms_count": 1,
                "rating_score": 95.0,
            },
            {
                "listing_id": 5,
                "snapshot_date": "2024-06-15",
                "city_name": "Roma",
                "period_label": "Early Summer",
                "neighbourhood_name": "Centro",
                "room_type": "Entire home",
                "nightly_price": 157.0,
                "latitude": 41.904,
                "longitude": 12.494,
                "accommodates_count": 3,
                "beds_count": 2,
                "bedrooms_count": 1,
                "rating_score": 95.0,
            },
            {
                "listing_id": 6,
                "snapshot_date": "2024-06-15",
                "city_name": "Roma",
                "period_label": "Early Summer",
                "neighbourhood_name": "Trastevere",
                "room_type": "Entire home",
                "nightly_price": 180.0,
                "latitude": 41.89,
                "longitude": 12.47,
                "accommodates_count": 2,
                "beds_count": 1,
                "bedrooms_count": 1,
                "rating_score": 98.0,
            },
        ]
    )

    target_listing = feature_frame.iloc[0]
    result = select_comparable_listings(feature_frame, target_listing, top_n=3)

    assert result.used_city_fallback is False
    assert len(result.comparables) == 3
    assert (result.comparables["neighbourhood_name"] == "Centro").all()


def test_select_comparable_listings_widens_to_city_pool_when_local_pool_is_sparse() -> None:
    feature_frame = pd.DataFrame(
        [
            {
                "listing_id": 1,
                "snapshot_date": "2024-06-15",
                "city_name": "Napoli",
                "period_label": "Early Summer",
                "neighbourhood_name": "Chiaia",
                "room_type": "Entire home",
                "nightly_price": 120.0,
                "latitude": 40.84,
                "longitude": 14.24,
                "accommodates_count": 2,
                "beds_count": 1,
                "bedrooms_count": 1,
                "rating_score": 95.0,
            },
            {
                "listing_id": 2,
                "snapshot_date": "2024-06-15",
                "city_name": "Napoli",
                "period_label": "Early Summer",
                "neighbourhood_name": "Vomero",
                "room_type": "Entire home",
                "nightly_price": 110.0,
                "latitude": 40.85,
                "longitude": 14.25,
                "accommodates_count": 2,
                "beds_count": 1,
                "bedrooms_count": 1,
                "rating_score": 94.0,
            },
        ]
    )

    result = select_comparable_listings(feature_frame, feature_frame.iloc[0], top_n=1, min_local_pool=2)

    assert result.used_city_fallback is True
    assert result.comparables.iloc[0]["listing_id"] == 2
