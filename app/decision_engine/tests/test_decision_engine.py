import unittest

import pandas as pd
from fastapi.testclient import TestClient

from app.decision_engine.confidence_engine import ConfidenceEngine
from app.decision_engine.decision_detector import DecisionDetector
from app.decision_engine.decision_service import decision_service
from app.decision_engine.priority_engine import PriorityEngine
from app.decision_engine.recommendation_engine import RecommendationEngine
from app.main import app


class TestDecisionIntelligenceEngine(unittest.TestCase):
    def setUp(self) -> None:
        # Clear the in-memory decision feed before each test
        decision_service._feed.clear()
        self.client = TestClient(app)

    def test_priority_score_calculation(self):
        # 1. Critical test case (Financial Impact = $50,000 -> normalized as 100)
        prio, level = PriorityEngine.calculate_priority(
            financial_impact=50000.0,
            urgency=100.0,
            confidence=100.0,
            criticality=100.0,
        )
        self.assertEqual(prio, 100.0)
        self.assertEqual(level, "Critical")

        # 2. Low priority case
        prio, level = PriorityEngine.calculate_priority(
            financial_impact=1000.0,
            urgency=10.0,
            confidence=50.0,
            criticality=20.0,
        )
        self.assertTrue(prio < 40.0)
        self.assertEqual(level, "Low")

    def test_confidence_score_calculation(self):
        score = ConfidenceEngine.calculate_confidence(
            completeness=90.0,
            consistency=90.0,
            freshness=90.0,
            rule_weight=90.0,
        )
        self.assertEqual(score, 90.0)

    def test_recommendation_and_roi_mapping(self):
        rec, roi = RecommendationEngine.generate_recommendation_and_roi(
            "Inventory Shortage", {"product_name": "Product X"}
        )
        self.assertIn("replenishment order", rec.lower())
        self.assertEqual(roi, 25.0)

    def test_sales_anomalies_detector(self):
        # Setup mock sales data: historical sales (high) vs recent (low) -> drops
        data = {
            "Product": ["Product A", "Product B", "Product A", "Product B"],
            "Revenue": [10000.0, 5000.0, 100.0, 50.0],
            "Date": ["2026-01-01", "2026-01-02", "2026-06-01", "2026-06-02"],
            "Margin": [0.45, 0.20, 0.45, 0.20],
        }
        df = pd.DataFrame(data)
        decisions = DecisionDetector.detect_sales_decisions(df)

        # Verify a revenue drop decision is triggered
        categories = [d.category for d in decisions]
        self.assertIn("Revenue Drop", categories)

        # Verify pricing opportunity decision is triggered (Product A margin >= 0.40 and total revenue > 10,000)
        self.assertIn("Pricing Opportunity", categories)

    def test_inventory_anomalies_detector(self):
        # Stock: 5 (below safety threshold 20)
        # Sales Velocity: 0 -> Slow moving
        data = {
            "Product": ["Product X", "Product Y"],
            "Stock Level": [5.0, 120.0],
            "Safety Stock": [20.0, 10.0],
            "Velocity": [5.0, 0.0],
        }
        df = pd.DataFrame(data)
        decisions = DecisionDetector.detect_inventory_decisions(df)
        categories = [d.category for d in decisions]

        self.assertIn("Inventory Shortage", categories)
        self.assertIn("Slow Moving Products", categories)

    def test_financial_anomalies_detector(self):
        # normal average amount: 1000. category amount: 5000 (exceeds average * 1.20)
        data = {
            "category": ["Marketing", "Travel", "Marketing", "Travel"],
            "amount": [5000.0, 100.0, 5000.0, 100.0],
        }
        df = pd.DataFrame(data)
        decisions = DecisionDetector.detect_financial_decisions(df)
        categories = [d.category for d in decisions]

        self.assertIn("Expense Spike", categories)

    def test_decision_service_and_endpoints(self):
        # 1. Trigger service refresh
        sales_data = {
            "Product": ["Product A"],
            "Revenue": [15000.0],
            "Date": ["2026-01-01"],
            "Margin": [0.50],
        }
        df = pd.DataFrame(sales_data)
        decision_service.refresh_feed_from_dataframe(df, "Sales")

        # Assert feed is populated
        feed = decision_service.get_feed()
        self.assertTrue(len(feed) > 0)

        # 2. Test GET API /api/v1/decision-feed
        response = self.client.get("/api/v1/decision-feed")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_count"], len(feed))

        # 3. Test GET Detail /api/v1/decision-feed/{id}
        decision_id = feed[0].decision_id
        detail_response = self.client.get(f"/api/v1/decision-feed/{decision_id}")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["decision_id"], decision_id)

        # 4. Test POST refresh endpoint
        refresh_response = self.client.post(
            "/api/v1/decision-feed/refresh", json={"workspace": "analytics"}
        )
        self.assertEqual(refresh_response.status_code, 201)


if __name__ == "__main__":
    unittest.main()
