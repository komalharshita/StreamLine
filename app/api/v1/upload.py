from typing import Any, Sequence
from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.deps import get_current_user, get_upload_service
from app.schemas.upload import FileMetadataResponse, IngestionRequest, IngestionResponse
from app.services.upload.service import UploadServiceInterface

router = APIRouter()


@router.post(
    "/file", response_model=FileMetadataResponse, status_code=status.HTTP_201_CREATED
)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: dict[str, Any] = Depends(get_current_user),
    upload_service: UploadServiceInterface = Depends(get_upload_service),
) -> FileMetadataResponse:
    """Receives a file upload, transfers it to Cloud Storage, and logs metadata."""
    contents = await file.read()
    filename = file.filename or "raw_dataset.csv"
    content_type = file.content_type or "text/csv"
    user_id = current_user.get("uid", "anonymous")

    file_metadata = upload_service.handle_upload(
        filename=filename, content_type=content_type, data=contents, user_id=user_id
    )
    return FileMetadataResponse.model_validate(file_metadata)


@router.post("/ingest", response_model=IngestionResponse)
def trigger_data_ingestion(
    request: IngestionRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    upload_service: UploadServiceInterface = Depends(get_upload_service),
) -> IngestionResponse:
    """Triggers the loading pipeline of an uploaded file into BigQuery analytical tables."""
    return upload_service.trigger_ingestion(
        file_id=request.file_id, target_table=request.target_table
    )


@router.get("/files", response_model=list[FileMetadataResponse])
def list_uploaded_files(
    current_user: dict[str, Any] = Depends(get_current_user),
    upload_service: UploadServiceInterface = Depends(get_upload_service),
) -> Sequence[Any]:
    """Retrieves metadata of all files uploaded to the workspace."""
    files = upload_service.list_user_files()
    return [FileMetadataResponse.model_validate(f) for f in files]
