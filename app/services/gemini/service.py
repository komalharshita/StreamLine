import logging
from abc import ABC, abstractmethod
from typing import Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.core.config import settings
from app.schemas.chat import ChatMessage, ChatResponse
from app.services.base import BaseService

logger = logging.getLogger("app.services.gemini")


class GeminiServiceInterface(BaseService, ABC):
    """Interface for sending prompts and executing conversational queries using Gemini."""

    @abstractmethod
    def generate_chat_response(
        self, prompt: str, history: list[ChatMessage], dataset_context: Optional[str] = None
    ) -> ChatResponse:
        """Sends chat request to Gemini model, optionally grounding on database context."""
        pass


class GeminiService(GeminiServiceInterface):
    """Concrete implementation of the GeminiService using the new google-genai SDK."""

    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        self.model_name = model_name
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> Optional[genai.Client]:
        if self._client is not None:
            return self._client
        if settings.GEMINI_API_KEY:
            try:
                self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
                return self._client
            except Exception as e:
                logger.error(f"Failed to configure Gemini Client: {str(e)}")
        return None

    def generate_chat_response(
        self, prompt: str, history: list[ChatMessage], dataset_context: Optional[str] = None
    ) -> ChatResponse:
        logger.info(f"Generating Gemini response for prompt length: {len(prompt)}")
        
        client = self._get_client()
        if not client:
            logger.warning("Gemini Client or API Key is missing. Falling back to mock assistant response.")
            return self._generate_mock_response(prompt, dataset_context)

        try:
            # Grounding prompt augmentation if table reference is specified
            context_prefix = ""
            if dataset_context:
                context_prefix = (
                    f"[System Context: Ground your answer using the data fields of BigQuery table: {dataset_context}]\n"
                )

            # Build history list for google-genai Content list
            contents = []
            for msg in history:
                role = "user" if msg.role == "user" else "model"
                contents.append(
                    types.Content(role=role, parts=[types.Part.from_text(text=msg.content)])
                )

            full_prompt = f"{context_prefix}{prompt}"
            contents.append(
                types.Content(role="user", parts=[types.Part.from_text(text=full_prompt)])
            )

            # Generate content
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents,
            )
            
            return ChatResponse(
                response=response.text or "",
                sources=[dataset_context] if dataset_context else [],
                token_usage=response.usage_metadata.total_token_count if response.usage_metadata else 0,
            )
        except Exception as e:
            logger.error(f"Gemini API invocation failed: {str(e)}")
            return self._generate_mock_response(prompt, dataset_context, error_msg=str(e))

    def _generate_mock_response(
        self, prompt: str, dataset_context: Optional[str], error_msg: Optional[str] = None
    ) -> ChatResponse:
        """Generates placeholder response for local runs and fallbacks."""
        grounding_msg = f" (grounded on schema '{dataset_context}')" if dataset_context else ""
        text = (
            f"### StreamLine Assistant\n\n"
            f"I received your query: *\"{prompt}\"*{grounding_msg}.\n\n"
            f"This is a placeholder response. In production, this module connects to "
            f"the **{self.model_name}** endpoint to analyze data tables."
        )
        if error_msg:
            text += f"\n\n> **API Notice**: Gemini call failed with error: `{error_msg}`. Defaulted to mock payload."

        return ChatResponse(
            response=text,
            sources=[dataset_context] if dataset_context else [],
            token_usage=len(prompt) // 4,
        )
