import json
import logging
import re
from typing import Any

logger = logging.getLogger("app.gemini.response_parser")


class ResponseParser:
    """Parses raw text outputs and extracts structured JSON elements from model responses."""

    @staticmethod
    def parse_plain_text(text: str) -> str:
        """Cleans up markdown formatting or leading whitespaces from plain text responses."""
        if not text:
            return ""
        return text.strip()

    @staticmethod
    def extract_json(text: str) -> dict[str, Any]:
        """Finds and parses the first JSON block contained in a raw text response.

        Returns a dictionary representation, falling back to empty fields if extraction fails.
        """
        if not text:
            return {}

        # Strip markdown json block tags if present
        cleaned_text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
        cleaned_text = cleaned_text.strip()

        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            # Fallback search using regex for bracketed structures
            match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            logger.warning(
                "Failed to extract JSON format from Gemini response. Returning empty dictionary."
            )
            return {}
