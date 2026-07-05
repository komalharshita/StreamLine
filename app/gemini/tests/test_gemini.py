import unittest
from datetime import datetime, timezone
from unittest.mock import patch
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.decision_engine.decision_service import decision_service
from app.decision_engine.schemas import Decision
from app.gemini.prompt_builder import PromptBuilder
from app.gemini.context_builder import ContextBuilder
from app.gemini.response_parser import ResponseParser
from app.gemini.gemini_service import gemini_service


class TestGeminiIntegration(unittest.TestCase):
    def setUp(self) -> None:
        # Clear database states
        decision_service._feed.clear()
        self.client = TestClient(app)

        # Mock the Gemini API client call to isolate tests from the network and quota limits
        self.api_patcher = patch("app.gemini.gemini_service.gemini_service._call_gemini_api")
        self.mock_api = self.api_patcher.start()
        
        # Dynamic mock response based on prompt text
        def dynamic_mock_api(prompt, system_instruction=None):
            if "JSON" in prompt or "summary" in prompt.lower():
                return (
                    '{"business_health_summary": "Mock business health summary", '
                    '"top_risks": ["Mock Risk"], "top_opportunities": ["Mock Opportunity"], '
                    '"recommended_actions": ["Mock Action"]}'
                )
            return "Mocked response from DecisionPilot."
            
        self.mock_api.side_effect = dynamic_mock_api

    def tearDown(self) -> None:
        self.api_patcher.stop()

    def test_prompt_builder(self):
        prompt = PromptBuilder.build_chat_prompt("test question", "test context")
        self.assertIn("SYSTEM INSTRUCTIONS", prompt)
        self.assertIn("test question", prompt)
        self.assertIn("test context", prompt)

    def test_response_parser(self):
        # 1. Plain text cleaning
        text = "  Hello business case!  "
        self.assertEqual(ResponseParser.parse_plain_text(text), "Hello business case!")

        # 2. JSON block extraction
        json_str = '```json\n{"business_health_summary": "Good"}\n```'
        data = ResponseParser.extract_json(json_str)
        self.assertEqual(data.get("business_health_summary"), "Good")

    def test_context_builder(self):
        # Setup mock active decisions
        d = Decision(
            decision_id="dec-111",
            priority_score=90.0,
            priority_level="Critical",
            category="Revenue Drop",
            title="Revenue Drop Alert",
            description="Revenue dropped",
            root_cause="None",
            evidence={},
            financial_impact=10000.0,
            confidence_score=95.0,
            recommendation="Actions",
            expected_roi=20.0,
            status="active",
            created_at=datetime.now(timezone.utc),
        )
        decision_service._feed[d.decision_id] = d
        
        ctx = ContextBuilder.build_system_context()
        self.assertEqual(ctx["critical_decisions_count"], 1)
        self.assertEqual(ctx["total_decisions_count"], 1)
        
        formatted = ContextBuilder.format_context_as_text(ctx)
        self.assertIn("Revenue Drop Alert", formatted)
        self.assertIn("Impact: $10,000.00", formatted)

    def test_gemini_service_fallbacks(self):
        # Setup mock active decisions
        d = Decision(
            decision_id="dec-111",
            priority_score=90.0,
            priority_level="Critical",
            category="Revenue Drop",
            title="Revenue Drop Alert",
            description="Revenue dropped",
            root_cause="None",
            evidence={},
            financial_impact=10000.0,
            confidence_score=95.0,
            recommendation="Actions",
            expected_roi=20.0,
            status="active",
            created_at=datetime.now(timezone.utc),
        )
        decision_service._feed[d.decision_id] = d

        explain_res = gemini_service.explain_decision(d)
        self.assertEqual(explain_res.decision_id, d.decision_id)
        self.assertIn("DecisionPilot", explain_res.explanation)

        # Executive Summary
        summary_res = gemini_service.generate_executive_summary()
        self.assertEqual(summary_res.business_health_summary, "Mock business health summary")
        self.assertEqual(summary_res.top_risks, ["Mock Risk"])

        # Trend explanation
        trend_res = gemini_service.explain_trend("revenue", {"average": 100})
        self.assertEqual(trend_res.trend_type, "revenue")
        self.assertIn("DecisionPilot", trend_res.explanation)

        # Chat response
        chat_res = gemini_service.generate_chat_response("What are my active risks?")
        self.assertIn("DecisionPilot", chat_res.response)

    def test_gemini_api_routes(self):
        # Setup mock active decisions
        d = Decision(
            decision_id="dec-111",
            priority_score=90.0,
            priority_level="Critical",
            category="Revenue Drop",
            title="Revenue Drop Alert",
            description="Revenue dropped",
            root_cause="None",
            evidence={},
            financial_impact=10000.0,
            confidence_score=95.0,
            recommendation="Actions",
            expected_roi=20.0,
            status="active",
            created_at=datetime.now(timezone.utc),
        )
        decision_service._feed[d.decision_id] = d

        # 1. POST /api/v1/chat
        chat_response = self.client.post("/api/v1/chat", json={"message": "What is the status?"})
        self.assertEqual(chat_response.status_code, 200)
        self.assertIn("response", chat_response.json())

        # 2. POST /api/v1/gemini/explain-decision
        explain_response = self.client.post(
            "/api/v1/gemini/explain-decision", json={"decision_id": "dec-111"}
        )
        self.assertEqual(explain_response.status_code, 200)
        self.assertEqual(explain_response.json()["decision_id"], "dec-111")

        # 3. POST /api/v1/gemini/executive-summary
        summary_response = self.client.post("/api/v1/gemini/executive-summary")
        self.assertEqual(summary_response.status_code, 200)
        self.assertIn("business_health_summary", summary_response.json())

        # 4. POST /api/v1/gemini/trends
        trends_response = self.client.post(
            "/api/v1/gemini/trends",
            json={"trend_type": "revenue", "raw_data_summary": {"avg": 500}},
        )
        self.assertEqual(trends_response.status_code, 200)
        self.assertEqual(trends_response.json()["trend_type"], "revenue")


if __name__ == "__main__":
    unittest.main()
