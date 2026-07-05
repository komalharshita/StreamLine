import logging
from typing import Any

logger = logging.getLogger("app.gemini.prompt_builder")


class PromptBuilder:
    """Compiles modular prompt strings containing system directives, environment contexts, and queries."""

    # Reusable System Instructions
    DECISION_PILOT_SYSTEM = (
        "You are DecisionPilot, the advanced Autonomous Business Analyst for the StreamLine Platform.\n"
        "Your task is to analyze business operational context, recent dataset uploads, and prioritized decisions "
        "to answer natural language queries. Provide concise, professional, and data-backed business insights.\n"
        "Ensure your advice is specific and avoids generic consulting jargon."
    )

    EXPLAINER_SYSTEM = (
        "You are a Senior Executive Business Advisor.\n"
        "Provide clear, professional, and actionable business explanations summarizing the root cause, financial "
        "consequences, and expected ROI of decisions. Present your advice as a structured business case."
    )

    SUMMARY_SYSTEM = (
        "You are the Chief Strategy Officer.\n"
        "Generate a structured Executive Summary outlining the business health, primary risk exposures, top performance "
        "opportunities, and urgent recommended strategic tasks based on the active decision feed."
    )

    @classmethod
    def build_chat_prompt(cls, message: str, context_text: str) -> str:
        """Assembles chat prompts for the Gemini model."""
        return (
            f"=== SYSTEM INSTRUCTIONS ===\n{cls.DECISION_PILOT_SYSTEM}\n\n"
            f"=== DATA CONTEXT ===\n{context_text}\n\n"
            f"=== USER QUERY ===\n{message}\n"
        )

    @classmethod
    def build_explain_prompt(cls, decision_dict: dict[str, Any]) -> str:
        """Assembles decision explanation prompts for the Gemini model."""
        return (
            f"=== SYSTEM INSTRUCTIONS ===\n{cls.EXPLAINER_SYSTEM}\n\n"
            f"=== DECISION FINDING ===\n"
            f"* Category: {decision_dict.get('category')}\n"
            f"* Title: {decision_dict.get('title')}\n"
            f"* Description: {decision_dict.get('description')}\n"
            f"* Root Cause: {decision_dict.get('root_cause')}\n"
            f"* Financial Impact: ${decision_dict.get('financial_impact'):,.2f}\n"
            f"* Evidence: {decision_dict.get('evidence')}\n"
            f"* Primary Recommendation: {decision_dict.get('recommendation')}\n\n"
            f"=== TASK ===\n"
            f"Write a thorough explanation detailing why this issue occurred, its potential business consequences, "
            f"and construct a step-by-step Action Plan based on the recommendation."
        )

    @classmethod
    def build_executive_summary_prompt(cls, context_text: str) -> str:
        """Assembles executive summary prompts for the Gemini model."""
        return (
            f"=== SYSTEM INSTRUCTIONS ===\n{cls.SUMMARY_SYSTEM}\n\n"
            f"=== ACTIVE FEED CONTEXT ===\n{context_text}\n\n"
            f"=== TASK ===\n"
            f"Generate a Business Health Summary covering overall health metrics, followed by list segments for: "
            f"1. Top Risks (Critical/High threats)\n"
            f"2. Top Opportunities (value-add/pricing spots)\n"
            f"3. Recommended Actions (specific immediate operational steps)\n"
            f"Format the output strictly as JSON with keys: "
            f"'business_health_summary', 'top_risks', 'top_opportunities', and 'recommended_actions'."
        )

    @classmethod
    def build_trend_prompt(cls, trend_type: str, raw_data: dict[str, Any]) -> str:
        """Assembles trend explanation prompts for the Gemini model."""
        return (
            f"=== SYSTEM INSTRUCTIONS ===\n{cls.DECISION_PILOT_SYSTEM}\n\n"
            f"=== TREND RAW DATA ({trend_type.upper()}) ===\n"
            f"{raw_data}\n\n"
            f"=== TASK ===\n"
            f"Explain this {trend_type} trend in plain, strategic business language. "
            f"Detail what the numbers show (upward/downward trajectories) and outline the core operational implications."
        )
