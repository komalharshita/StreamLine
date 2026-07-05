import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from google.api_core.exceptions import GoogleAPIError

from app.main import app
from app.upload.metadata_service import metadata_store
from app.upload.status_tracker import UploadStatusTracker


class TestUploadPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app, raise_server_exceptions=False)
        # Clear metadata store and status store before each test run
        metadata_store._store.clear()
        metadata_store._hash_index.clear()
        UploadStatusTracker.get_status("dummy") # Reset dummy trigger if any

    @patch("app.storage.gcs_service.gcs_storage_service.upload_bytes")
    @patch("app.bigquery.bigquery_service.bq_ingestion_service.load_dataframe")
    def test_successful_upload(self, mock_bq, mock_gcs):
        # 1. Mock GCS and BQ calls
        mock_gcs.return_value = "https://storage.googleapis.com/streamline-hackathon-uploads/test.csv"
        mock_bq.return_value = {
            "dataset": "streamline_analytics",
            "table": "sales_test",
            "job_id": "job-12345",
            "rows": 3,
            "columns": 3,
        }

        csv_content = b"Date,Product,Sales\n2023-01-01,ProdA,100\n2023-01-02,ProdB,200\n"
        response = self.client.post(
            "/api/v1/upload",
            files={"file": ("sales.csv", csv_content, "text/csv")},
            headers={"Authorization": "Bearer mock-token"},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["filename"], "sales.csv")
        self.assertEqual(data["rows"], 2)
        
        # Verify status tracker has marked it complete
        upload_id = data["upload_id"]
        status_info = UploadStatusTracker.get_status(upload_id)
        self.assertEqual(status_info["status"], "Completed")
        self.assertEqual(status_info["progress"], 100)

    @patch("app.storage.gcs_service.gcs_storage_service.upload_bytes")
    @patch("app.bigquery.bigquery_service.bq_ingestion_service.load_dataframe")
    def test_duplicate_upload(self, mock_bq, mock_gcs):
        mock_gcs.return_value = "https://storage.googleapis.com/test.csv"
        mock_bq.return_value = {"dataset": "ds", "table": "tb", "job_id": "job", "rows": 1, "columns": 1}
        csv_content = b"ColA,ColB\nVal1,Val2\n"

        # First upload
        resp1 = self.client.post(
            "/api/v1/upload",
            files={"file": ("data.csv", csv_content, "text/csv")},
            headers={"Authorization": "Bearer mock-token"},
        )
        self.assertEqual(resp1.status_code, 201)

        # Second upload (same content checksum)
        resp2 = self.client.post(
            "/api/v1/upload",
            files={"file": ("data.csv", csv_content, "text/csv")},
            headers={"Authorization": "Bearer mock-token"},
        )
        self.assertEqual(resp2.status_code, 409)
        self.assertIn("identical contents", resp2.json()["error"]["message"])

    def test_invalid_file_extension(self):
        # PDFs or media files are unsupported extensions
        response = self.client.post(
            "/api/v1/upload",
            files={"file": ("report.pdf", b"PDF_CONTENT_BYTES", "application/pdf")},
            headers={"Authorization": "Bearer mock-token"},
        )
        self.assertEqual(response.status_code, 415)

    def test_corrupted_file(self):
        # Uploading corrupted csv (invalid bytes) that fails parsing
        response = self.client.post(
            "/api/v1/upload",
            files={"file": ("sales.csv", b"\x00\xff\xfe\x00_corrupted_bytes", "text/csv")},
            headers={"Authorization": "Bearer mock-token"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("failed", response.json()["error"].lower())

    @patch("app.storage.gcs_service.gcs_storage_service.upload_bytes")
    def test_gcs_upload_failure(self, mock_gcs):
        # Throw API error on Cloud Storage upload
        mock_gcs.side_effect = GoogleAPIError("GCS Ingestion Failure")
        csv_content = b"Date,Sales\n2023-01-01,100\n"

        response = self.client.post(
            "/api/v1/upload",
            files={"file": ("sales.csv", csv_content, "text/csv")},
            headers={"Authorization": "Bearer mock-token"},
        )
        self.assertEqual(response.status_code, 500)

    @patch("app.storage.gcs_service.gcs_storage_service.upload_bytes")
    @patch("app.bigquery.bigquery_service.bq_ingestion_service.load_dataframe")
    def test_bigquery_ingestion_failure(self, mock_bq, mock_gcs):
        mock_gcs.return_value = "https://storage.googleapis.com/test.csv"
        # Mock BigQuery load_dataframe throwing exception
        mock_bq.side_effect = Exception("BigQuery write error")
        csv_content = b"Date,Sales\n2023-01-01,100\n"

        response = self.client.post(
            "/api/v1/upload",
            files={"file": ("sales.csv", csv_content, "text/csv")},
            headers={"Authorization": "Bearer mock-token"},
        )
        self.assertEqual(response.status_code, 500)

    def test_large_file_rejection(self):
        # Create bytes payload exceeding size limit (> 100MB)
        large_content = b"A" * (101 * 1024 * 1024)
        response = self.client.post(
            "/api/v1/upload",
            files={"file": ("sales.csv", large_content, "text/csv")},
            headers={"Authorization": "Bearer mock-token"},
        )
        self.assertEqual(response.status_code, 413)

    @patch("app.core.security.security_manager.verify_token")
    def test_missing_unauthorized_token(self, mock_verify):
        mock_verify.side_effect = HTTPException(status_code=401, detail="Unauthorized")
        csv_content = b"Date,Sales\n2023-01-01,100\n"
        
        response = self.client.post(
            "/api/v1/upload",
            files={"file": ("sales.csv", csv_content, "text/csv")},
            # Missing or invalid Authorization token
            headers={"Authorization": "Bearer invalid-token"},
        )
        self.assertEqual(response.status_code, 401)
