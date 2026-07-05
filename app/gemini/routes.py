import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.gemini.schemas import (
    ChatRequest,
    ChatResponse,
    ExplainDecisionRequest,
    ExplainDecisionResponse,
    ExecutiveSummaryResponse,
    TrendExplanationRequest,
    TrendExplanationResponse,
)
from app.gemini.gemini_service import gemini_service
from app.decision_engine.decision_service import decision_service

logger = logging.getLogger("app.gemini.routes")

router = APIRouter(tags=["Gemini AI Integration"])


@router.post("/api/v1/chat", response_model=ChatResponse)
def chat_with_decision_pilot(request: ChatRequest):
    """Interactive DecisionPilot chatbot answering business questions with dataset context."""
    logger.info("Handling POST request for DecisionPilot chat assistant.")
    return gemini_service.generate_chat_response(request.message, request.workspace)


@router.post("/api/v1/gemini/explain-decision", response_model=ExplainDecisionResponse)
def explain_decision_detail(request: ExplainDecisionRequest):
    """Generates an executive-level explanation and action plan for a specific Decision."""
    logger.info(f"Handling POST request to explain decision: {request.decision_id}")
    # Retrieve the decision from the engine
    decision = decision_service.get_decision(request.decision_id)
    return gemini_service.explain_decision(decision)


@router.post("/api/v1/gemini/executive-summary", response_model=ExecutiveSummaryResponse)
def get_executive_summary():
    """Generates a structured executive performance summary and strategic tasks checklist."""
    logger.info("Handling POST request for platform executive summary.")
    return gemini_service.generate_executive_summary()


@router.post("/api/v1/gemini/trends", response_model=TrendExplanationResponse)
def explain_metrics_trends(request: TrendExplanationRequest):
    """Explains revenue, inventory, or expense timelines in plain language."""
    logger.info(f"Handling POST request to explain trends of type: {request.trend_type}")
    return gemini_service.explain_trend(request.trend_type, request.raw_data_summary)
