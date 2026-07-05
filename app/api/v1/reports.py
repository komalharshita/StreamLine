from typing import Any, Sequence

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_reports_service
from app.schemas.reports import ReportCreate, ReportResponse
from app.services.reports.service import ReportsServiceInterface

router = APIRouter()


@router.post(
    "/generate",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_analytical_report(
    request: ReportCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    reports_service: ReportsServiceInterface = Depends(get_reports_service),
) -> ReportResponse:
    """Submits a database query compilation request and writes output to Google Cloud Storage."""
    user_id = current_user.get("uid", "anonymous")
    report = reports_service.generate_report(request, user_id)

    # Map GCS URI to HTTP Download URL
    download_url = (
        f"https://storage.googleapis.com/{reports_service.storage_repo.bucket_name}/"
        if hasattr(reports_service.storage_repo, "bucket_name")
        else "https://storage.googleapis.com/streamline-data-ingestion/"
    )
    if report.gcs_uri:
        blob_path = report.gcs_uri.split("gs://")[-1].split("/", 1)[-1]
        download_url += blob_path

    response = ReportResponse.model_validate(report)
    response.download_url = download_url
    return response


@router.get("/list", response_model=list[ReportResponse])
def list_generated_reports(
    current_user: dict[str, Any] = Depends(get_current_user),
    reports_service: ReportsServiceInterface = Depends(get_reports_service),
) -> Sequence[Any]:
    """Retrieves all reports compiled by the requesting user."""
    user_id = current_user.get("uid", "anonymous")
    reports = reports_service.list_reports(user_id)

    responses = []
    for rep in reports:
        res = ReportResponse.model_validate(rep)
        download_url = (
            f"https://storage.googleapis.com/{reports_service.storage_repo.bucket_name}/"
            if hasattr(reports_service.storage_repo, "bucket_name")
            else "https://storage.googleapis.com/streamline-data-ingestion/"
        )
        if rep.gcs_uri:
            blob_path = rep.gcs_uri.split("gs://")[-1].split("/", 1)[-1]
            download_url += blob_path
        res.download_url = download_url
        responses.append(res)

    return responses


@router.get("/report/{id}", response_model=ReportResponse)
def get_report_details(
    id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    reports_service: ReportsServiceInterface = Depends(get_reports_service),
) -> ReportResponse:
    """Fetches details, execution queries, and download links for a specific report."""
    report = reports_service.get_report(id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{id}' not found.",
        )

    res = ReportResponse.model_validate(report)
    download_url = (
        f"https://storage.googleapis.com/{reports_service.storage_repo.bucket_name}/"
        if hasattr(reports_service.storage_repo, "bucket_name")
        else "https://storage.googleapis.com/streamline-data-ingestion/"
    )
    if report.gcs_uri:
        blob_path = report.gcs_uri.split("gs://")[-1].split("/", 1)[-1]
        download_url += blob_path
    res.download_url = download_url
    return res
