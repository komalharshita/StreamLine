import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
import pandas as pd

from app.decision_engine.schemas import Decision
from app.decision_engine.business_rules import DEFAULT_THRESHOLDS
from app.decision_engine.priority_engine import PriorityEngine
from app.decision_engine.confidence_engine import ConfidenceEngine
from app.decision_engine.recommendation_engine import RecommendationEngine

logger = logging.getLogger("app.decision_engine.decision_detector")


class DecisionDetector:
    """Scans and evaluates cleaned business datasets to generate actionable Decision objects."""

    @staticmethod
    def _find_column(df: pd.DataFrame, keywords: list[str], default: str) -> str:
        """Helper to find column header matching semantic keywords."""
        for col in df.columns:
            col_str = str(col).lower()
            if any(kw in col_str for kw in keywords):
                return col
        return default

    @classmethod
    def detect_sales_decisions(cls, df: pd.DataFrame) -> list[Decision]:
        """Scans Sales data to check for Revenue Drops, Pricing Opportunities, and High Performers."""
        decisions = []
        if df.empty:
            return decisions

        # Resolve column headers dynamically
        rev_col = cls._find_column(df, ["revenue", "price", "amount", "sales"], "revenue")
        date_col = cls._find_column(df, ["date", "time", "purchase"], "date")
        prod_col = cls._find_column(df, ["product", "item", "sku"], "product_name")
        margin_col = cls._find_column(df, ["margin", "profit", "markup"], "margin")

        # 1. Evaluate Revenue Drop
        if date_col in df.columns and rev_col in df.columns:
            try:
                df_dates = df.copy()
                df_dates[date_col] = pd.to_datetime(df_dates[date_col], errors="coerce")
                df_dates = df_dates.dropna(subset=[date_col])
                
                # Sort and split into historical vs recent halves
                df_dates = df_dates.sort_values(by=date_col)
                mid_point = len(df_dates) // 2
                if mid_point > 0:
                    hist_rev = df_dates.iloc[:mid_point][rev_col].astype(float).sum()
                    recent_rev = df_dates.iloc[mid_point:][rev_col].astype(float).sum()
                    
                    if hist_rev > 0:
                        drop_pct = ((hist_rev - recent_rev) / hist_rev) * 100.0
                        if drop_pct >= DEFAULT_THRESHOLDS["revenue_drop_percentage"]:
                            evidence = {"historical_revenue": hist_rev, "recent_revenue": recent_rev, "drop_percentage": round(drop_pct, 2)}
                            financial_impact = hist_rev - recent_rev
                            
                            conf = ConfidenceEngine.calculate_confidence()
                            prio, level = PriorityEngine.calculate_priority(
                                financial_impact=financial_impact,
                                urgency=85.0,
                                confidence=conf,
                                criticality=90.0,
                            )
                            rec, roi = RecommendationEngine.generate_recommendation_and_roi("Revenue Drop", evidence)

                            decisions.append(
                                Decision(
                                    decision_id=str(uuid.uuid4()),
                                    priority_score=prio,
                                    priority_level=level,
                                    category="Revenue Drop",
                                    title="Significant Revenue Drop Identified",
                                    description=f"Overall revenue dropped by {drop_pct:.2f}% compared to the prior timeframe.",
                                    root_cause="Decline in transaction velocity and discount exposure.",
                                    evidence=evidence,
                                    financial_impact=round(financial_impact, 2),
                                    confidence_score=conf,
                                    recommendation=rec,
                                    expected_roi=roi,
                                    status="active",
                                    created_at=datetime.now(timezone.utc),
                                )
                            )
            except Exception as e:
                logger.error(f"Error evaluating Revenue Drop: {str(e)}")

        # 2. Evaluate Pricing Opportunities and High Performers
        if prod_col in df.columns and rev_col in df.columns:
            try:
                # Group by product
                prod_stats = df.groupby(prod_col).agg({
                    rev_col: "sum",
                    margin_col: "mean" if margin_col in df.columns else lambda x: 0.35  # default margin
                }).reset_index()

                for _, row in prod_stats.iterrows():
                    p_name = row[prod_col]
                    p_rev = float(row[rev_col])
                    p_margin = float(row[margin_col])

                    # Pricing Opportunity: Inelastic high margin check
                    if p_margin >= 0.40 and p_rev > 10000:
                        evidence = {"product_name": p_name, "current_revenue": p_rev, "margin": p_margin}
                        conf = ConfidenceEngine.calculate_confidence(rule_weight=90.0)
                        prio, level = PriorityEngine.calculate_priority(
                            financial_impact=p_rev * 0.05,  # 5% price raise estimate
                            urgency=40.0,
                            confidence=conf,
                            criticality=50.0,
                        )
                        rec, roi = RecommendationEngine.generate_recommendation_and_roi("Pricing Opportunity", evidence)

                        decisions.append(
                            Decision(
                                decision_id=str(uuid.uuid4()),
                                priority_score=prio,
                                priority_level=level,
                                category="Pricing Opportunity",
                                title=f"Pricing Opportunity for {p_name}",
                                description=f"Product '{p_name}' operates with high profit margins ({p_margin:.1%}) and stable revenues. Suggesting minor pricing optimization.",
                                root_cause="Inelastic market demand layout.",
                                evidence=evidence,
                                financial_impact=round(p_rev * 0.05, 2),
                                confidence_score=conf,
                                recommendation=rec,
                                expected_roi=roi,
                                status="active",
                                created_at=datetime.now(timezone.utc),
                            )
                        )

                    # High Performing Product check
                    if p_rev > 20000:
                        evidence = {"product_name": p_name, "sales_revenue": p_rev}
                        conf = ConfidenceEngine.calculate_confidence(rule_weight=95.0)
                        prio, level = PriorityEngine.calculate_priority(
                            financial_impact=p_rev * 0.10,
                            urgency=50.0,
                            confidence=conf,
                            criticality=70.0,
                        )
                        rec, roi = RecommendationEngine.generate_recommendation_and_roi("High Performing Products", evidence)

                        decisions.append(
                            Decision(
                                decision_id=str(uuid.uuid4()),
                                priority_score=prio,
                                priority_level=level,
                                category="High Performing Products",
                                title=f"Promote High-Performing SKU: {p_name}",
                                description=f"Product '{p_name}' accounts for substantial sales revenue (${p_rev:,.2f}). Target for campaign prioritization.",
                                root_cause="High customer alignment and strong market fit.",
                                evidence=evidence,
                                financial_impact=round(p_rev * 0.10, 2),
                                confidence_score=conf,
                                recommendation=rec,
                                expected_roi=roi,
                                status="active",
                                created_at=datetime.now(timezone.utc),
                            )
                        )
            except Exception as e:
                logger.error(f"Error evaluating product decisions: {str(e)}")

        return decisions

    @classmethod
    def detect_inventory_decisions(cls, df: pd.DataFrame) -> list[Decision]:
        """Scans Inventory data to flag Shortages, Overstocks, and Slow Moving items."""
        decisions = []
        if df.empty:
            return decisions

        # Resolve headers
        prod_col = cls._find_column(df, ["product", "item", "sku"], "product_name")
        stock_col = cls._find_column(df, ["stock_level", "stock", "quantity", "qty"], "stock_level")
        safety_col = cls._find_column(df, ["safety", "threshold", "minimum"], "safety_stock")
        vel_col = cls._find_column(df, ["velocity", "sales_velocity", "demand"], "sales_velocity")

        for _, row in df.iterrows():
            try:
                p_name = str(row[prod_col]) if prod_col in df.columns else "Unknown SKU"
                stock = float(row[stock_col]) if stock_col in df.columns else 0.0
                safety = float(row[safety_col]) if safety_col in df.columns else 10.0
                velocity = float(row[vel_col]) if vel_col in df.columns else 1.0

                # 1. Inventory Shortage Check
                if stock < safety or (velocity > 0 and (stock / velocity) < DEFAULT_THRESHOLDS["inventory_shortage_weeks"]):
                    evidence = {"product_name": p_name, "stock_level": stock, "safety_stock": safety, "weekly_velocity": velocity}
                    financial_impact = (safety - stock) * 50.0  # approximate cost penalty
                    conf = ConfidenceEngine.calculate_confidence()
                    prio, level = PriorityEngine.calculate_priority(
                        financial_impact=financial_impact,
                        urgency=90.0,
                        confidence=conf,
                        criticality=80.0,
                    )
                    rec, roi = RecommendationEngine.generate_recommendation_and_roi("Inventory Shortage", evidence)

                    decisions.append(
                        Decision(
                            decision_id=str(uuid.uuid4()),
                            priority_score=prio,
                            priority_level=level,
                            category="Inventory Shortage",
                            title=f"Stock Shortage Alert: {p_name}",
                            description=f"Current inventory level ({stock}) is below safety threshold ({safety}) or safety week velocity limits.",
                            root_cause="Supply chain delay or unexpected demand spike.",
                            evidence=evidence,
                            financial_impact=round(financial_impact, 2),
                            confidence_score=conf,
                            recommendation=rec,
                            expected_roi=roi,
                            status="active",
                            created_at=datetime.now(timezone.utc),
                        )
                    )

                # 2. Inventory Overstock Check
                if velocity > 0 and (stock / velocity) >= DEFAULT_THRESHOLDS["inventory_overstock_weeks"]:
                    evidence = {"product_name": p_name, "stock_level": stock, "weekly_velocity": velocity}
                    financial_impact = stock * 10.0  # storage carrying cost estimate
                    conf = ConfidenceEngine.calculate_confidence()
                    prio, level = PriorityEngine.calculate_priority(
                        financial_impact=financial_impact,
                        urgency=45.0,
                        confidence=conf,
                        criticality=40.0,
                    )
                    rec, roi = RecommendationEngine.generate_recommendation_and_roi("Inventory Overstock", evidence)

                    decisions.append(
                        Decision(
                            decision_id=str(uuid.uuid4()),
                            priority_score=prio,
                            priority_level=level,
                            category="Inventory Overstock",
                            title=f"Excess Inventory Identified: {p_name}",
                            description=f"Warehouse carries excessive inventory ({stock} units) representing > {stock/velocity:.1f} weeks of demand.",
                            root_cause="Over-ordering or slower sales velocity.",
                            evidence=evidence,
                            financial_impact=round(financial_impact, 2),
                            confidence_score=conf,
                            recommendation=rec,
                            expected_roi=roi,
                            status="active",
                            created_at=datetime.now(timezone.utc),
                        )
                    )

                # 3. Slow Moving Products Check
                if velocity == 0 and stock > 50:
                    evidence = {"product_name": p_name, "stock_level": stock}
                    financial_impact = stock * 15.0
                    conf = ConfidenceEngine.calculate_confidence(rule_weight=80.0)
                    prio, level = PriorityEngine.calculate_priority(
                        financial_impact=financial_impact,
                        urgency=55.0,
                        confidence=conf,
                        criticality=50.0,
                    )
                    rec, roi = RecommendationEngine.generate_recommendation_and_roi("Slow Moving Products", evidence)

                    decisions.append(
                        Decision(
                            decision_id=str(uuid.uuid4()),
                            priority_score=prio,
                            priority_level=level,
                            category="Slow Moving Products",
                            title=f"Liquidate Slow Moving Product: {p_name}",
                            description=f"Product '{p_name}' has zero registered weekly sales velocity, binding capital in {stock} units.",
                            root_cause="Decline in product interest or market saturation.",
                            evidence=evidence,
                            financial_impact=round(financial_impact, 2),
                            confidence_score=conf,
                            recommendation=rec,
                            expected_roi=roi,
                            status="active",
                            created_at=datetime.now(timezone.utc),
                        )
                    )

            except Exception as e:
                logger.error(f"Error processing inventory decision row: {str(e)}")

        return decisions

    @classmethod
    def detect_financial_decisions(cls, df: pd.DataFrame) -> list[Decision]:
        """Scans Financial Transactions data to flag Expense Spikes."""
        decisions = []
        if df.empty:
            return decisions

        # Resolve headers
        cat_col = cls._find_column(df, ["category", "type", "expense"], "category")
        amt_col = cls._find_column(df, ["amount", "value", "cost"], "amount")

        if cat_col in df.columns and amt_col in df.columns:
            try:
                # Group expenses by category
                cat_expenses = df.groupby(cat_col)[amt_col].sum().reset_index()
                overall_avg = df[amt_col].mean()

                for _, row in cat_expenses.iterrows():
                    c_name = row[cat_col]
                    c_amt = float(row[amt_col])

                    # Trigger decision if expense category exceeds average by > 20%
                    if c_amt > (overall_avg * 1.20):
                        evidence = {"expense_category": c_name, "category_spend": c_amt, "system_average": overall_avg}
                        financial_impact = c_amt - overall_avg
                        conf = ConfidenceEngine.calculate_confidence()
                        prio, level = PriorityEngine.calculate_priority(
                            financial_impact=financial_impact,
                            urgency=70.0,
                            confidence=conf,
                            criticality=65.0,
                        )
                        rec, roi = RecommendationEngine.generate_recommendation_and_roi("Expense Spike", evidence)

                        decisions.append(
                            Decision(
                                decision_id=str(uuid.uuid4()),
                                priority_score=prio,
                                priority_level=level,
                                category="Expense Spike",
                                title=f"Expense Spike in category '{c_name}'",
                                description=f"Total category expense reached ${c_amt:,.2f}, significantly outperforming the normal spending baseline.",
                                root_cause="Procurement price adjustment or lack of budgetary constraints.",
                                evidence=evidence,
                                financial_impact=round(financial_impact, 2),
                                confidence_score=conf,
                                recommendation=rec,
                                expected_roi=roi,
                                status="active",
                                created_at=datetime.now(timezone.utc),
                            )
                        )
            except Exception as e:
                logger.error(f"Error evaluating Financial Spikes: {str(e)}")

        return decisions
