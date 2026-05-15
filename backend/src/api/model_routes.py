"""HTTP routes for the Goal 4 local beta."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from services.goal2_artifact_loader import ArtifactConfigurationError
from services.price_decision_service import (
    ListingNotFoundError,
    PriceDecisionService,
    get_default_price_decision_service,
)


router = APIRouter()


def get_price_decision_service() -> PriceDecisionService:
    return get_default_price_decision_service()


@router.get("/health")
def health() -> dict[str, object]:
    try:
        metadata = get_default_price_decision_service().get_metadata()
    except ArtifactConfigurationError as exc:
        return {"status": "error", "artifacts_available": False, "detail": str(exc)}
    return {
        "status": "ok",
        "artifacts_available": True,
        "artifact_version": metadata["artifact_version"],
    }


@router.get("/api/model/metadata")
def model_metadata(
    service: PriceDecisionService = Depends(get_price_decision_service),
) -> dict[str, object]:
    return service.get_metadata()


@router.get("/api/listings")
def listings(
    city_name: str | None = Query(default=None, min_length=1),
    period_label: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=25, ge=1, le=100),
    service: PriceDecisionService = Depends(get_price_decision_service),
) -> list[dict[str, object]]:
    return service.list_listings(
        city_name=city_name,
        period_label=period_label,
        limit=limit,
    )


@router.get("/api/price-decisions")
def price_decisions(
    listing_id: int = Query(..., gt=0),
    snapshot_date: date | None = Query(default=None),
    service: PriceDecisionService = Depends(get_price_decision_service),
) -> dict[str, object]:
    try:
        return service.build_price_decision(
            listing_id=listing_id,
            snapshot_date=snapshot_date,
        )
    except ListingNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
