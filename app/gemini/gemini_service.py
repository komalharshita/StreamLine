import logging
import os
import time
from typing import Any, Optional

from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.core.config import settings
from app.decision_engine.schemas import Decision
from app.gemini.context_builder import ContextBuilder
from app.gemini.prompt_builder import PromptBuilder
from app.gemini.response_parser import ResponseParser
from app.gemini.schemas import (
    ChatResponse,
    ExecutiveSummaryResponse,
    ExplainDecisionResponse,
    TrendExplanationResponse,
)

logger = logging.getLogger("app.gemini.gemini_service")


class GeminiService:
    """Official Gemini SDK Service wrapper implementing prompt management and endpoint callbacks."""

    def __init__(self) -> None:
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        self._client: Optional[genai.Client] = None
        self.model_name = (
            "gemini-2.5-flash"  # Standard low-latency business assistant model
        )

    def _ensure_client(self) -> bool:
        """Configures the official google.genai Client."""
        if self._client is not None:
            return True

        if not self.api_key:
            logger.warning(
                "GEMINI_API_KEY environment variable is not configured. "
                "Running in Mock/Fallback simulation mode."
            )
            return False

        try:
            self._client = genai.Client(api_key=self.api_key)
            logger.info("Successfully configured official Google Gen AI Client.")
            return True
        except Exception as e:
            logger.error(f"Failed to configure Gemini client: {str(e)}")
            return False

    def _call_gemini_api(
        self, prompt: str, system_instruction: Optional[str] = None
    ) -> Optional[str]:
        """Calls Gemini API with retries and a timeout check."""
        if not self._ensure_client():
            return None

        # Standard retry loop for transient API timeouts (up to 3 attempts)
        for attempt in range(1, 4):
            try:
                logger.info(
                    f"Submitting prompt to Gemini ({self.model_name}) - Attempt {attempt}"
                )

                # Execute content generation using the new SDK
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                )
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                )

                if response and response.text:
                    return response.text

                logger.warning("Empty response received from Gemini API.")

            except APIError as api_err:
                logger.warning(f"Google API Error on attempt {attempt}: {str(api_err)}")
                time.sleep(1.0 * attempt)
            except Exception as ex:
                logger.warning(
                    f"Unexpected error calling Gemini API on attempt {attempt}: {str(ex)}"
                )
                time.sleep(1.0 * attempt)

        logger.error("Failed to generate content from Gemini API after retries.")
        return None

    def explain_decision(self, decision: Decision) -> ExplainDecisionResponse:
        """Explains a Decision object, falling back to deterministic templates if offline."""
        logger.info(f"Generating explanation for decision: {decision.decision_id}")
        prompt = PromptBuilder.build_explain_prompt(decision.dict())

        raw_response = self._call_gemini_api(
            prompt, system_instruction=PromptBuilder.EXPLAINER_SYSTEM
        )

        if raw_response:
            explanation_text = ResponseParser.parse_plain_text(raw_response)
            action_text = f"Action Checklist: {decision.recommendation}"
        else:
            # Fallback representation
            logger.info("Executing mock explainer fallback.")
            explanation_text = (
                f"Strategic analysis of decision '{decision.title}'. The issue is categorized under "
                f"'{decision.category}' due to root cause: '{decision.root_cause}'. This event carries a projected "
                f"financial impact of ${decision.financial_impact:,.2f}. To mitigate this risk, immediate "
                f"reordering or operational budget adjustments should be applied."
            )
            action_text = (
                f"1. Implement Recommendation: '{decision.recommendation}'\n"
                f"2. Audit related SKU inventories and cost accounts\n"
                f"3. Verify projected financial savings ROI: {decision.expected_roi}%"
            )

        return ExplainDecisionResponse(
            decision_id=decision.decision_id,
            explanation=explanation_text,
            action_plan=action_text,
        )

    def generate_executive_summary(self) -> ExecutiveSummaryResponse:
        """Generates a structured Business Health Summary including top risks/opportunities."""
        start_time = time.perf_counter()
        logger.info("Generating platform executive summary.")

        # Build context from Decision feed
        system_ctx = ContextBuilder.build_system_context()
        context_text = ContextBuilder.format_context_as_text(system_ctx)
        prompt = PromptBuilder.build_executive_summary_prompt(context_text)

        raw_response = self._call_gemini_api(
            prompt, system_instruction=PromptBuilder.SUMMARY_SYSTEM
        )

        structured_data = {}
        if raw_response:
            structured_data = ResponseParser.extract_json(raw_response)

            # Dynamically normalize list of dicts to list of strings
            for key in ["top_risks", "top_opportunities"]:
                if key in structured_data and isinstance(structured_data[key], list):
                    normalized = []
                    for item in structured_data[key]:
                        if isinstance(item, dict):
                            name_val = (
                                item.get("name")
                                or item.get("title")
                                or item.get("label")
                                or str(item)
                            )
                            desc_val = item.get("description") or item.get("details")
                            if name_val and desc_val:
                                normalized.append(f"{name_val}: {desc_val}")
                            else:
                                normalized.append(str(name_val))
                        else:
                            normalized.append(str(item))
                    structured_data[key] = normalized

            # Normalize recommended_actions
            if "recommended_actions" in structured_data and isinstance(
                structured_data["recommended_actions"], list
            ):
                normalized = []
                for item in structured_data["recommended_actions"]:
                    if isinstance(item, dict):
                        task_val = (
                            item.get("task")
                            or item.get("action")
                            or item.get("title")
                            or str(item)
                        )
                        desc_val = item.get("description") or item.get("details")
                        if task_val and desc_val:
                            normalized.append(f"{task_val}: {desc_val}")
                        else:
                            normalized.append(str(task_val))
                    else:
                        normalized.append(str(item))
                structured_data["recommended_actions"] = normalized

        # Apply fallback if extraction is empty
        if not structured_data:
            logger.info("Executing mock summary fallback.")
            risks = []
            opps = []
            for d in system_ctx.get("recent_decisions", []):
                if d["priority_level"] in {"Critical", "High"}:
                    risks.append(
                        f"Risk: {d['title']} (${d['financial_impact']:,.2f} impact)"
                    )
                else:
                    opps.append(f"Opportunity: Optimizing {d['title']}")

            structured_data = {
                "business_health_summary": (
                    f"Overall operational health is stable with {system_ctx.get('total_decisions_count', 0)} active decisions flagged. "
                    f"Action should focus on addressing {system_ctx.get('critical_decisions_count', 0)} critical priority events."
                ),
                "top_risks": risks
                or ["No immediate critical risk exposures cataloged."],
                "top_opportunities": opps
                or ["Expand advertising placements for inelastic product categories."],
                "recommended_actions": [
                    "Replenish inventory shortages on critical SKUs",
                    "Audit category expense spikes exceeding budget boundaries",
                ],
            }

        processing_time = round((time.perf_counter() - start_time) * 1000, 3)

        return ExecutiveSummaryResponse(
            business_health_summary=structured_data.get("business_health_summary", ""),
            top_risks=structured_data.get("top_risks", []),
            top_opportunities=structured_data.get("top_opportunities", []),
            recommended_actions=structured_data.get("recommended_actions", []),
            generation_time_ms=processing_time,
        )

    def explain_trend(
        self, trend_type: str, raw_data_summary: dict[str, Any]
    ) -> TrendExplanationResponse:
        """Explains revenue, inventory, or expense trends in plain business terms."""
        logger.info(f"Generating trend explanation for: '{trend_type}'")
        prompt = PromptBuilder.build_trend_prompt(trend_type, raw_data_summary)

        raw_response = self._call_gemini_api(
            prompt, system_instruction=PromptBuilder.DECISION_PILOT_SYSTEM
        )

        if raw_response:
            explanation_text = ResponseParser.parse_plain_text(raw_response)
            implications_text = (
                "Operational implications derived from the timeline curves."
            )
        else:
            logger.info("Executing mock trend fallback.")
            explanation_text = (
                f"Trend analysis of raw data summary shows fluctuations in overall {trend_type}. "
                f"Normal averages remain within expected operational threshold parameters."
            )
            implications_text = f"Evaluate monthly procurement settings to ensure alignment with active {trend_type} directions."

        return TrendExplanationResponse(
            trend_type=trend_type,
            explanation=explanation_text,
            implications=implications_text,
        )

    def generate_chat_response(
        self, message: str, workspace: str = "default"
    ) -> ChatResponse:
        """Feeds the uploader's context and question to Gemini for DecisionPilot Chat."""
        logger.info(f"Handling DecisionPilot chat message for workspace '{workspace}'")

        # Build context
        system_ctx = ContextBuilder.build_system_context(workspace)
        context_text = ContextBuilder.format_context_as_text(system_ctx)
        prompt = PromptBuilder.build_chat_prompt(message, context_text)

        raw_response = self._call_gemini_api(
            prompt, system_instruction=PromptBuilder.DECISION_PILOT_SYSTEM
        )

        if raw_response:
            response_text = ResponseParser.parse_plain_text(raw_response)
        else:
            logger.info("Executing mock chat assistant fallback.")
            response_text = (
                f"Hello! I am DecisionPilot. I see that you are asking about '{message}' in workspace '{workspace}'. "
                f"Currently, there are {system_ctx.get('total_decisions_count', 0)} active decisions identified. "
                f"Let me know if you would like me to explain any specific inventory shortages or expense spikes!"
            )

        return ChatResponse(
            response=response_text,
            confidence=95.0,
            context_used=system_ctx,
        )


# Singleton service instance
gemini_service = GeminiService()
