from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from config.artifact_settings import Goal2ArtifactSettings
from services.goal2_artifact_loader import load_goal2_artifacts
from services.price_decision_service import ListingNotFoundError, PriceDecisionService


@pytest.fixture(scope="module")
def service() -> PriceDecisionService:
    settings = Goal2ArtifactSettings.from_environment()
    return PriceDecisionService(load_goal2_artifacts(settings), settings)


def test_listing_filters_return_json_safe_rows(service: PriceDecisionService) -> None:
    rows = service.list_listings(city_name="Roma", period_label="Early Spring", limit=3)

    assert len(rows) == 3
    assert rows[0]["city_name"] == "Roma"
    assert rows[0]["period_label"] == "Early Spring"
    assert isinstance(rows[0]["snapshot_date"], str)
    assert "beds_count" in rows[0]
    assert "bathrooms_count" in rows[0]
    assert "distance_to_city_center_km" in rows[0]
    assert "latitude" in rows[0]


def test_price_decision_reuses_benchmark_led_goal2_payload(service: PriceDecisionService) -> None:
    rows = service.list_listings(city_name="Roma", period_label="Early Spring", limit=1)
    payload = service.build_price_decision(
        listing_id=int(rows[0]["listing_id"]),
        snapshot_date=date.fromisoformat(str(rows[0]["snapshot_date"])),
    )

    assert payload["primary_decision_signal"] == "benchmark_range"
    assert payload["decision_policy"] == "benchmark_led_positioning"
    assert payload["model_estimate_role"] == "supporting_signal"
    assert payload["model_estimate_lower_bound"] <= payload["estimated_market_price"]
    assert payload["model_estimate_upper_bound"] >= payload["estimated_market_price"]
    assert payload["model_estimate_interval_source"] == "heldout_residual_quantiles"
    assert payload["model_benchmark_agreement_label"] in {"strong", "medium", "weak"}
    assert payload["model_benchmark_gap_amount"] >= 0.0
    assert payload["benchmark_lower_bound"] <= payload["benchmark_upper_bound"]
    assert payload["selected_comparables"]
    assert payload["local_explanation"]["top_upward_drivers"] or payload["local_explanation"]["top_downward_drivers"]


def test_missing_listing_raises_not_found(service: PriceDecisionService) -> None:
    with pytest.raises(ListingNotFoundError):
        service.build_price_decision(listing_id=999_999_999_999_999, snapshot_date=None)


def test_metadata_exposes_real_model_context(service: PriceDecisionService) -> None:
    metadata = service.get_metadata()

    assert metadata["artifact_version"] == "goal2_v10_diagnostics"
    assert metadata["row_count"] > 0
    assert "Roma" in metadata["available_cities"]
    assert metadata["champion_model_name"] == "catboost_challenger"
    assert "linear_baseline" in metadata["metrics"]
