import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status

from app.core.security import get_current_user
from app.upload.schemas import (
    UploadConfirmRequest,
    UploadConfirmResponse,
    UploadDeleteResponse,
    UploadMetadataResponse,
    UploadPreviewResponse,
    UploadStatusResponse,
)
from app.upload.upload_service import UploadService

router = APIRouter()
logger = logging.getLogger("app.upload.upload_router")


@router.post(
    "/upload",
    response_model=UploadMetadataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload dataset file (Synchronous / Legacy)",
    description="Validates size, format extension, hashes content, parses columns, cleans and ingests synchronously.",
)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UploadMetadataResponse:
    contents = await file.read()
    filename = file.filename or "unnamed_dataset"
    content_type = file.content_type or "application/octet-stream"
    user_id = current_user.get("email") or current_user.get("uid") or "system"

    logger.info(f"User '{user_id}' requested synchronous legacy upload of file: '{filename}'")

    record = UploadService.process_upload(
        filename=filename,
        content_type=content_type,
        file_bytes=contents,
        uploaded_by=user_id,
    )
    return UploadMetadataResponse.model_validate(record)


@router.post(
    "/upload/preview",
    response_model=UploadPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload dataset for schema preview and quality audit",
    description="Validates formatting and returns the first 25 rows, schema types, and data quality metrics.",
)
async def upload_preview(
    file: UploadFile = File(...),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UploadPreviewResponse:
    contents = await file.read()
    filename = file.filename or "unnamed_dataset"
    content_type = file.content_type or "application/octet-stream"
    user_id = current_user.get("email") or current_user.get("uid") or "system"

    logger.info(f"User '{user_id}' requested preview for file: '{filename}'")

    preview_data = UploadService.generate_preview(
        filename=filename,
        content_type=content_type,
        file_bytes=contents,
        uploaded_by=user_id,
    )
    return UploadPreviewResponse.model_validate(preview_data)


@router.post(
    "/upload/confirm",
    response_model=UploadConfirmResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm import and start background processing pipeline",
    description="Triggers the GCS, BigQuery, and Decision Engine pipeline in a background worker thread.",
)
def confirm_upload(
    payload: UploadConfirmRequest,
    background_tasks: BackgroundTasks,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UploadConfirmResponse:
    user_id = current_user.get("email") or current_user.get("uid") or "system"
    logger.info(f"User '{user_id}' confirmed import for upload ID: '{payload.upload_id}'")

    result = UploadService.confirm_import(
        upload_id=payload.upload_id,
        background_tasks=background_tasks,
        uploaded_by=user_id,
    )
    return UploadConfirmResponse.model_validate(result)


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


@router.get(
    "/upload/{upload_id}/status",
    response_model=UploadStatusResponse,
    summary="Get real-time upload processing stage and status",
)
def get_upload_status(upload_id: str) -> UploadStatusResponse:
    """Returns the in-memory progress and active pipeline stage of a dataset upload."""
    from app.upload.status_tracker import UploadStatusTracker
    status_data = UploadStatusTracker.get_status(upload_id)
    return UploadStatusResponse.model_validate(status_data)
