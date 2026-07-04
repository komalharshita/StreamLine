from typing import Any
from fastapi import Depends

from app.core.config import settings
from app.core.security import get_current_user
from app.database.bigquery import BigQueryManager
from app.database.storage import StorageManager
from app.repositories.bigquery_repository import (
    BigQueryAnalyticsReportRepository,
    BigQueryDecisionRuleRepository,
    BigQuerySimulationScenarioRepository,
)
from app.repositories.storage_repository import (
    BigQueryFileMetadataRepository,
    GCSStorageRepository,
)
from app.services.decision_engine.service import (
    DecisionEngineService,
    DecisionEngineServiceInterface,
)
from app.services.forecast.service import ForecastService, ForecastServiceInterface
from app.services.gemini.service import GeminiService, GeminiServiceInterface
from app.services.notifications.service import (
    NotificationsService,
    NotificationsServiceInterface,
)
from app.services.recommendation.service import (
    RecommendationService,
    RecommendationServiceInterface,
)
from app.services.reports.service import ReportsService, ReportsServiceInterface
from app.services.simulation.service import (
    SimulationService,
    SimulationServiceInterface,
)
from app.services.upload.service import UploadService, UploadServiceInterface


# Database & Manager Dependencies
def get_bq_manager() -> BigQueryManager:
    return BigQueryManager()


def get_storage_manager() -> StorageManager:
    return StorageManager()


# Repository Dependencies
def get_decision_rule_repo(
    bq_manager: BigQueryManager = Depends(get_bq_manager),
) -> BigQueryDecisionRuleRepository:
    return BigQueryDecisionRuleRepository(bq_manager)


def get_simulation_scenario_repo(
    bq_manager: BigQueryManager = Depends(get_bq_manager),
) -> BigQuerySimulationScenarioRepository:
    return BigQuerySimulationScenarioRepository(bq_manager)


def get_analytics_report_repo(
    bq_manager: BigQueryManager = Depends(get_bq_manager),
) -> BigQueryAnalyticsReportRepository:
    return BigQueryAnalyticsReportRepository(bq_manager)


def get_file_metadata_repo(
    bq_manager: BigQueryManager = Depends(get_bq_manager),
) -> BigQueryFileMetadataRepository:
    return BigQueryFileMetadataRepository(bq_manager)


def get_storage_repo(
    storage_manager: StorageManager = Depends(get_storage_manager),
) -> GCSStorageRepository:
    return GCSStorageRepository(storage_manager, settings.GCS_BUCKET_NAME)


# Service Dependencies
def get_upload_service(
    metadata_repo: BigQueryFileMetadataRepository = Depends(get_file_metadata_repo),
    storage_repo: GCSStorageRepository = Depends(get_storage_repo),
) -> UploadServiceInterface:
    return UploadService(metadata_repo, storage_repo)


def get_decision_engine_service(
    rule_repo: BigQueryDecisionRuleRepository = Depends(get_decision_rule_repo),
) -> DecisionEngineServiceInterface:
    return DecisionEngineService(rule_repo)


def get_forecast_service(
    bq_manager: BigQueryManager = Depends(get_bq_manager),
) -> ForecastServiceInterface:
    return ForecastService(bq_manager)


def get_recommendation_service(
    bq_manager: BigQueryManager = Depends(get_bq_manager),
) -> RecommendationServiceInterface:
    return RecommendationService(bq_manager)


def get_simulation_service(
    scenario_repo: BigQuerySimulationScenarioRepository = Depends(
        get_simulation_scenario_repo
    ),
) -> SimulationServiceInterface:
    return SimulationService(scenario_repo)


def get_gemini_service() -> GeminiServiceInterface:
    return GeminiService()


# Shared singleton notification service instance
_notifications_service = NotificationsService()


def get_notifications_service() -> NotificationsServiceInterface:
    return _notifications_service


def get_reports_service(
    report_repo: BigQueryAnalyticsReportRepository = Depends(get_analytics_report_repo),
    storage_repo: GCSStorageRepository = Depends(get_storage_repo),
) -> ReportsServiceInterface:
    return ReportsService(report_repo, storage_repo)
