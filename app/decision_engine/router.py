import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.decision_engine.schemas import Decision, DecisionFeedResponse, DecisionRefreshRequest
from app.decision_engine.decision_service import decision_service

logger = logging.getLogger("app.decision_engine.router")

router = APIRouter(prefix="/api/v1/decision-feed", tags=["Decision Intelligence"])


@router.get("", response_model=DecisionFeedResponse)
def get_decision_feed(
    category: Optional[str] = Query(None, description="Filter decisions by category"),
    priority_level: Optional[str] = Query(None, description="Filter decisions by priority: Critical, High, Medium, Low"),
):
    """Retrieves the list of active Decisions sorted by priority score."""
    logger.info("Handling GET request for decision feed.")
    decisions = decision_service.get_feed(category=category, priority_level=priority_level)
    
    # Calculate metadata summary
    critical_count = sum(1 for d in decisions if d.priority_level == "Critical")
    high_count = sum(1 for d in decisions if d.priority_level == "High")

    return DecisionFeedResponse(
        decisions=decisions,
        total_count=len(decisions),
        critical_count=critical_count,
        high_count=high_count,
    )


@router.get("/{decision_id}", response_model=Decision)
def get_decision_detail(decision_id: str):
    """Retrieves detailed properties of a single Decision by its ID."""
    logger.info(f"Handling GET request for decision details: {decision_id}")
    return decision_service.get_decision(decision_id)


@router.post("/refresh", response_model=list[Decision], status_code=status.HTTP_201_CREATED)
def refresh_decision_feed(request: DecisionRefreshRequest):
    """Manually triggers evaluation rules over recently ingested datasets."""
    logger.info(f"Handling POST request to refresh feed. Workspace: {request.workspace}")
    # Under a production runtime, we would read the latest parsed dataframes from BigQuery or local cache.
    # We return the active list.
    return decision_service.get_feed()
