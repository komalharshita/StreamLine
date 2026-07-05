from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_gemini_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gemini.service import GeminiServiceInterface

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
def query_gemini_assistant(
    request: ChatRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    gemini_service: GeminiServiceInterface = Depends(get_gemini_service),
) -> ChatResponse:
    """Invokes Gemini generative text models to prompt the virtual assistant.

    Optionally grounds the response using dataset schemas from BigQuery.
    """
    return gemini_service.generate_chat_response(
        prompt=request.message,
        history=request.history,
        dataset_context=request.context_dataset_id,
    )
