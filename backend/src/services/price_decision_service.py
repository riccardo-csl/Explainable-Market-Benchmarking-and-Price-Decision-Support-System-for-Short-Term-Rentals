"""Application service for Goal 2 price decisions."""

from __future__ import annotations

from datetime import date
from functools import lru_cache
from typing import Any

import pandas as pd

from benchmarking.price_positioning_service import build_price_decision_payload
from config.artifact_settings import Goal2ArtifactSettings
from services.goal2_artifact_loader import Goal2Artifacts, load_goal2_artifacts


class ListingNotFoundError(LookupError):
    """Raised when a listing/snapshot pair is not present in the feature matrix."""


class PriceDecisionService:
    """Serve listing summaries and benchmark-led price decisions from Goal 2 artifacts."""

    def __init__(self, artifacts: Goal2Artifacts, settings: Goal2ArtifactSettings):
        self._artifacts = artifacts
        self._settings = settings

    def get_metadata(self) -> dict[str, Any]:
        metadata = dict(self._artifacts.metadata)
        metadata["artifact_version"] = self._settings.artifact_version
        metadata["artifact_root"] = str(self._settings.artifact_root)
        metadata["row_count"] = int(len(self._artifacts.feature_frame))
        metadata["available_cities"] = sorted(
            str(value)
            for value in self._artifacts.feature_frame["city_name"].dropna().unique()
        )
        metadata["available_periods"] = sorted(
            str(value)
            for value in self._artifacts.feature_frame["period_label"].dropna().unique()
        )
        return _json_safe(metadata)

    def list_listings(
        self,
        *,
        city_name: str | None,
        period_label: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        frame = self._artifacts.feature_frame
        if city_name is not None:
            frame = frame[frame["city_name"] == city_name]
        if period_label is not None:
            frame = frame[frame["period_label"] == period_label]

        ordered = frame.sort_values(["city_name", "period_label", "listing_id", "snapshot_date"], kind="stable")
        columns = [
            "listing_id",
            "snapshot_date",
            "city_name",
            "period_label",
            "neighbourhood_name",
            "room_type",
            "nightly_price",
            "accommodates_count",
            "beds_count",
            "bedrooms_count",
            "bathrooms_count",
            "bathroom_type",
            "host_listing_count",
            "total_reviews",
            "reviews_last_twelve_months",
            "reviews_per_month",
            "rating_score",
            "accuracy_score",
            "cleanliness_score",
            "checkin_score",
            "communication_score",
            "location_score",
            "value_score",
            "latitude",
            "longitude",
            "host_tenure_days",
            "distance_to_city_center_km",
            "distance_to_neighbourhood_center_km",
            "is_superhost",
            "season_peak_flag",
            "season_shoulder_flag",
            "venezia_group_name",
        ]
        return [_json_safe(record) for record in ordered.head(limit)[columns].to_dict(orient="records")]

    def build_price_decision(
        self,
        *,
        listing_id: int,
        snapshot_date: date | None,
    ) -> dict[str, Any]:
        target_listing = self._find_listing(listing_id=listing_id, snapshot_date=snapshot_date)
        bundle = self._artifacts.bundle
        feature_columns = list(bundle["feature_columns"])
        champion_pipeline = bundle["champion_pipeline"]
        estimated_market_price = float(
            champion_pipeline.predict(pd.DataFrame([target_listing[feature_columns].to_dict()]))[0]
        )
        payload = build_price_decision_payload(
            feature_frame=self._artifacts.feature_frame,
            target_listing=target_listing,
            estimated_market_price=estimated_market_price,
            champion_model_name=str(bundle["champion_model_name"]),
            fallback_model_name=str(bundle["fallback_model_name"]),
            linear_explanation_context=bundle["linear_explanation_context"],
            neighbourhood_period_summary=self._artifacts.neighbourhood_period_summary,
            city_period_summary=self._artifacts.city_period_summary,
            model_estimate_interval_calibration=bundle.get("model_estimate_interval_calibration"),
        )
        return _json_safe(payload)

    def _find_listing(self, *, listing_id: int, snapshot_date: date | None) -> pd.Series:
        matches = self._artifacts.feature_frame[self._artifacts.feature_frame["listing_id"] == listing_id]
        if snapshot_date is not None:
            matches = matches[
                pd.to_datetime(matches["snapshot_date"]).dt.date == snapshot_date
            ]
        if matches.empty:
            raise ListingNotFoundError("Listing not found for the requested snapshot.")
        return matches.sort_values("snapshot_date", ascending=False, kind="stable").iloc[0]


@lru_cache(maxsize=1)
def get_default_price_decision_service() -> PriceDecisionService:
    settings = Goal2ArtifactSettings.from_environment()
    return PriceDecisionService(
        artifacts=load_goal2_artifacts(settings),
        settings=settings,
    )


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value
