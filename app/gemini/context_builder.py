import logging
from typing import Any
from app.decision_engine.decision_service import decision_service
from app.upload.metadata_service import metadata_store

logger = logging.getLogger("app.gemini.context_builder")


class ContextBuilder:
    """Aggregates Decision Feed metadata and active file states into structured context objects."""

    @staticmethod
    def build_system_context(workspace: str = "default") -> dict[str, Any]:
        """Gathers dashboard metrics, active decisions, and recent file uploads as prompt context."""
        logger.info(f"Assembling system prompt context for workspace: '{workspace}'")
        
        # 1. Fetch active decisions from feed
        decisions = decision_service.get_feed()
        critical_count = sum(1 for d in decisions if d.priority_level == "Critical")
        high_count = sum(1 for d in decisions if d.priority_level == "High")
        medium_count = sum(1 for d in decisions if d.priority_level == "Medium")
        
        # 2. Extract recent uploads
        uploads = list(metadata_store._store.values())
        recent_files = [
            {"filename": u["filename"], "rows": u["rows"], "quality_score": u.get("quality_score")}
            for u in uploads[:5]
        ]

        return {
            "workspace": workspace,
            "critical_decisions_count": critical_count,
            "high_decisions_count": high_count,
            "medium_decisions_count": medium_count,
            "total_decisions_count": len(decisions),
            "recent_decisions": [
                {
                    "title": d.title,
                    "category": d.category,
                    "priority_level": d.priority_level,
                    "financial_impact": d.financial_impact,
                }
                for d in decisions[:5]
            ],
            "recent_uploads": recent_files,
        }

    @staticmethod
    def format_context_as_text(context: dict[str, Any]) -> str:
        """Formats the context dictionary into a clean Markdown block for prompt templates."""
        lines = [
            "### PLATFORM OPERATIONAL CONTEXT",
            f"* **Workspace Scope**: {context.get('workspace', 'default')}",
            f"* **Total Active Decisions**: {context.get('total_decisions_count', 0)}",
            f"  - Critical Priority: {context.get('critical_decisions_count', 0)}",
            f"  - High Priority: {context.get('high_decisions_count', 0)}",
            f"  - Medium Priority: {context.get('medium_decisions_count', 0)}",
            "\n### ACTIVE DECISION DETAILS:",
        ]
        
        decisions = context.get("recent_decisions", [])
        if not decisions:
            lines.append("  - No active decisions identified at this time.")
        for idx, d in enumerate(decisions, 1):
            lines.append(
                f"  {idx}. [{d.get('priority_level')}] {d.get('title')} "
                f"(Category: {d.get('category')}, Impact: ${d.get('financial_impact'):,.2f})"
            )

        lines.append("\n### RECENTLY UPLOADED DATASETS:")
        uploads = context.get("recent_uploads", [])
        if not uploads:
            lines.append("  - No files uploaded in this session.")
        for u in uploads:
            lines.append(
                f"  - {u.get('filename')} (Rows: {u.get('rows')}, "
                f"Quality: {u.get('quality_score', 'N/A')}/100)"
            )

        return "\n".join(lines)
