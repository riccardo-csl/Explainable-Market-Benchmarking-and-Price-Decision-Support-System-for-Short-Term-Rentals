from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_model_metadata_endpoint() -> None:
    response = client.get("/api/model/metadata")

    assert response.status_code == 200
    payload = response.json()
    assert payload["artifact_version"] == "goal2_v10_diagnostics"
    assert payload["champion_model_name"] == "catboost_challenger"
    assert payload["model_estimate_role"] if "model_estimate_role" in payload else True


def test_listings_endpoint_supports_filters() -> None:
    response = client.get("/api/listings", params={"city_name": "Roma", "period_label": "Early Spring", "limit": 2})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert {row["city_name"] for row in payload} == {"Roma"}
    assert {row["period_label"] for row in payload} == {"Early Spring"}


def test_price_decision_endpoint_returns_goal2_payload() -> None:
    listing = client.get("/api/listings", params={"city_name": "Roma", "period_label": "Early Spring", "limit": 1}).json()[0]
    response = client.get(
        "/api/price-decisions",
        params={"listing_id": listing["listing_id"], "snapshot_date": listing["snapshot_date"]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["listing_id"] == listing["listing_id"]
    assert payload["primary_decision_signal"] == "benchmark_range"
    assert payload["model_estimate_lower_bound"] <= payload["estimated_market_price"]
    assert payload["model_estimate_upper_bound"] >= payload["estimated_market_price"]
    assert payload["model_benchmark_agreement_label"] in {"strong", "medium", "weak"}
    assert payload["selected_comparables"]


def test_price_decision_missing_listing_returns_404() -> None:
    response = client.get("/api/price-decisions", params={"listing_id": 999_999_999_999})

    assert response.status_code == 404


def test_invalid_query_params_return_422() -> None:
    response = client.get("/api/listings", params={"limit": 0})

    assert response.status_code == 422
