from typing import Any, Sequence

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_decision_engine_service
from app.schemas.decision import (
    DecisionEvaluationRequest,
    DecisionEvaluationResponse,
    RuleCreate,
    RuleResponse,
)
from app.services.decision_engine.service import DecisionEngineServiceInterface

router = APIRouter()


@router.post("/rule", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
def create_decision_rule(
    rule_in: RuleCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    decision_service: DecisionEngineServiceInterface = Depends(
        get_decision_engine_service
    ),
) -> RuleResponse:
    """Registers a new rule in the decision intelligence engine."""
    user_id = current_user.get("uid", "anonymous")
    rule = decision_service.create_rule(rule_in, user_id)
    return RuleResponse.model_validate(rule)


@router.get("/rules", response_model=list[RuleResponse])
def list_decision_rules(
    current_user: dict[str, Any] = Depends(get_current_user),
    decision_service: DecisionEngineServiceInterface = Depends(
        get_decision_engine_service
    ),
) -> Sequence[Any]:
    """Retrieves all registered active/inactive decision rules."""
    rules = decision_service.list_rules()
    return [RuleResponse.model_validate(r) for r in rules]


@router.post("/evaluate", response_model=DecisionEvaluationResponse)
def evaluate_decision_context(
    request: DecisionEvaluationRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    decision_service: DecisionEngineServiceInterface = Depends(
        get_decision_engine_service
    ),
) -> DecisionEvaluationResponse:
    """Runs a context check against active rules to calculate output labels and recommendations."""
    return decision_service.evaluate_context(request.context)
