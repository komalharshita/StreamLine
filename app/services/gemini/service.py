import logging
from abc import ABC, abstractmethod
from typing import Optional

try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False

from app.core.config import settings
from app.schemas.chat import ChatMessage, ChatResponse
from app.services.base import BaseService

logger = logging.getLogger("app.services.gemini")

# Initialize Gemini SDK client if API key is provided and library is installed
if HAS_GEMINI_SDK and settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini AI SDK configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure Gemini AI SDK: {str(e)}")


class GeminiServiceInterface(BaseService, ABC):
    """Interface for sending prompts and executing conversational queries using Gemini."""

    @abstractmethod
    def generate_chat_response(
        self, prompt: str, history: list[ChatMessage], dataset_context: Optional[str] = None
    ) -> ChatResponse:
        """Sends chat request to Gemini model, optionally grounding on database context."""
        pass


class GeminiService(GeminiServiceInterface):
    """Concrete implementation of the GeminiService."""

    def __init__(self, model_name: str = "gemini-1.5-pro") -> None:
        self.model_name = model_name

    def generate_chat_response(
        self, prompt: str, history: list[ChatMessage], dataset_context: Optional[str] = None
    ) -> ChatResponse:
        logger.info(f"Generating Gemini response for prompt length: {len(prompt)}")
        
        # Check if API Key and SDK are available, otherwise return mock response
        if not HAS_GEMINI_SDK or not settings.GEMINI_API_KEY:
            logger.warning("Gemini SDK or API Key is missing. Falling back to mock assistant response.")
            return self._generate_mock_response(prompt, dataset_context)

        try:
            # Setup conversational model
            model = genai.GenerativeModel(self.model_name)
            
            # Grounding prompt augmentation if table reference is specified
            context_prefix = ""
            if dataset_context:
                context_prefix = (
                    f"[System Context: Ground your answer using the data fields of BigQuery table: {dataset_context}]\n"
                )

            # Build history list for Gemini format
            gemini_history = []
            for msg in history:
                role = "user" if msg.role == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg.content]})

            # Start chat session
            chat = model.start_chat(history=gemini_history)
            full_prompt = f"{context_prefix}{prompt}"
            
            response = chat.send_message(full_prompt)
            
            return ChatResponse(
                response=response.text,
                sources=[dataset_context] if dataset_context else [],
                token_usage=response.usage_metadata.total_token_count if hasattr(response, "usage_metadata") else 0,
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
