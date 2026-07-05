import logging
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Sequence

from app.models.domain import DecisionRule
from app.repositories.bigquery_repository import DecisionRuleRepositoryInterface
from app.schemas.decision import DecisionEvaluationResponse, RuleCreate
from app.services.base import BaseService

logger = logging.getLogger("app.services.decision_engine")


class DecisionEngineServiceInterface(BaseService, ABC):
    """Interface for managing rules and evaluating decision logic."""

    @abstractmethod
    def create_rule(self, rule_in: RuleCreate, user_id: str) -> DecisionRule:
        """Registers a new rule in the decision store."""
        pass

    @abstractmethod
    def evaluate_context(self, context: dict[str, Any]) -> DecisionEvaluationResponse:
        """Evaluates active rules against the provided data context payload."""
        pass

    @abstractmethod
    def list_rules(self) -> Sequence[DecisionRule]:
        """Lists all registered rules."""
        pass


class DecisionEngineService(DecisionEngineServiceInterface):
    """Concrete implementation of the DecisionEngineService."""

    def __init__(self, rule_repo: DecisionRuleRepositoryInterface) -> None:
        self.rule_repo = rule_repo

    def create_rule(self, rule_in: RuleCreate, user_id: str) -> DecisionRule:
        logger.info(f"Creating new rule: {rule_in.name} by user: {user_id}")
        rule = DecisionRule(
            id=f"rule-{uuid.uuid4()}",
            name=rule_in.name,
            expression=rule_in.expression,
            action=rule_in.action,
            priority=rule_in.priority,
            is_active=True,
            created_by=user_id,
        )
        return self.rule_repo.save(rule)

    def evaluate_context(self, context: dict[str, Any]) -> DecisionEvaluationResponse:
        logger.info(f"Evaluating decision intelligence context: {context}")
        start_time = time.perf_counter()

        # Fetch active rules sorted by priority (precedence)
        active_rules = self.rule_repo.list_active()
        matched_rules = []
        recommended_actions = []

        # Simple condition engine parser stub
        for rule in active_rules:
            try:
                # Basic safe-eval fallback simulation
                # In production, this would use a secure AST evaluation library or dry-run parser
                # Here we simulate evaluating rule expression, e.g. "input_value > 10"
                # For safety and placeholder purposes:
                is_match = False
                # If rule expression is simple, check context keys
                for key, val in context.items():
                    if key in rule.expression:
                        # Simulated check: if we see 'high' in expression and val is True/high, or numbers checks
                        if ">" in rule.expression and isinstance(val, (int, float)):
                            limit = float(rule.expression.split(">")[-1].strip())
                            if val > limit:
                                is_match = True
                        elif "<" in rule.expression and isinstance(val, (int, float)):
                            limit = float(rule.expression.split("<")[-1].strip())
                            if val < limit:
                                is_match = True
                        else:
                            is_match = True

                if is_match or not context:  # Default/Mock match
                    matched_rules.append(rule.id)
                    recommended_actions.append(rule.action)

            except Exception as e:
                logger.error(f"Failed to evaluate rule {rule.id}: {str(e)}")

        # Deduplicate recommended actions while preserving priority order
        seen = set()
        deduped_actions = [
            x for x in recommended_actions if not (x in seen or seen.add(x))
        ]

        duration_ms = (time.perf_counter() - start_time) * 1000

        return DecisionEvaluationResponse(
            evaluated_rules_count=len(active_rules),
            matched_rules=matched_rules,
            recommended_actions=deduped_actions,
            execution_time_ms=round(duration_ms, 3),
        )

    def list_rules(self) -> Sequence[DecisionRule]:
        return self.rule_repo.list_all()
