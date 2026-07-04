import logging
from typing import Any
from fastapi import APIRouter, Depends, File, UploadFile, status

from app.core.security import get_current_user
from app.upload.schemas import UploadDeleteResponse, UploadMetadataResponse
from app.upload.upload_service import UploadService

router = APIRouter()
logger = logging.getLogger("app.upload.upload_router")


@router.post(
    "/upload",
    response_model=UploadMetadataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload dataset file",
    description="Validates size, format extension, hashes content, parses columns, and logs metadata.",
)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UploadMetadataResponse:
    # Read file content stream
    contents = await file.read()
    filename = file.filename or "unnamed_dataset"
    content_type = file.content_type or "application/octet-stream"
    # Get author UID/email from authentication token
    user_id = current_user.get("email") or current_user.get("uid") or "system"

    logger.info(f"User '{user_id}' requested upload of file: '{filename}'")

    record = UploadService.process_upload(
        filename=filename,
        content_type=content_type,
        file_bytes=contents,
        uploaded_by=user_id,
    )
    return UploadMetadataResponse.model_validate(record)


@router.get(
    "/upload/{id}",
    response_model=UploadMetadataResponse,
    summary="Get upload metadata by ID",
)
def get_upload_metadata(
    id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UploadMetadataResponse:
    record = UploadService.get_upload(id)
    return UploadMetadataResponse.model_validate(record)


@router.get(
    "/uploads",
    response_model=list[UploadMetadataResponse],
    summary="List all uploaded dataset records",
)
def list_uploads(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[UploadMetadataResponse]:
    records = UploadService.list_uploads()
    return [UploadMetadataResponse.model_validate(rec) for rec in records]


@router.delete(
    "/upload/{id}",
    response_model=UploadDeleteResponse,
    summary="Delete upload record by ID",
)
def delete_upload(
    id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UploadDeleteResponse:
    logger.info(f"User requested deletion of upload metadata record: '{id}'")
    UploadService.delete_upload(id)
    return UploadDeleteResponse(
        success=True,
        message=f"File metadata record with ID '{id}' was successfully deleted.",
        upload_id=id,
    )
