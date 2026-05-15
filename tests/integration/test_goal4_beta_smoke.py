from fastapi.testclient import TestClient

from main import app


def test_goal4_beta_serves_dashboard_payload_for_real_listing() -> None:
    client = TestClient(app)

    metadata_response = client.get("/api/model/metadata")
    assert metadata_response.status_code == 200
    metadata = metadata_response.json()
    assert metadata["artifact_version"] == "goal2_v10_diagnostics"
    assert metadata["champion_model_name"] == "catboost_challenger"

    listings_response = client.get(
        "/api/listings",
        params={"city_name": "Roma", "period_label": "Early Spring", "limit": 1},
    )
    assert listings_response.status_code == 200
    listing = listings_response.json()[0]

    decision_response = client.get(
        "/api/price-decisions",
        params={
            "listing_id": listing["listing_id"],
            "snapshot_date": listing["snapshot_date"],
        },
    )
    assert decision_response.status_code == 200
    payload = decision_response.json()

    assert payload["primary_decision_signal"] == "benchmark_range"
    assert payload["model_estimate_role"] == "supporting_signal"
    assert payload["model_estimate_lower_bound"] <= payload["estimated_market_price"]
    assert payload["model_estimate_upper_bound"] >= payload["estimated_market_price"]
    assert payload["model_benchmark_agreement_label"] in {"strong", "medium", "weak"}
    assert payload["model_benchmark_agreement_summary"]
    assert payload["benchmark_lower_bound"] <= payload["benchmark_upper_bound"]
    assert payload["selected_comparables"]
    assert payload["local_explanation"]["top_upward_drivers"] or payload["local_explanation"]["top_downward_drivers"]
