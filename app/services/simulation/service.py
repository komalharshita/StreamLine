import logging
import uuid
from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.models.domain import SimulationScenario
from app.repositories.bigquery_repository import SimulationScenarioRepositoryInterface
from app.schemas.simulation import SimulationCreate
from app.services.base import BaseService

logger = logging.getLogger("app.services.simulation")


class SimulationServiceInterface(BaseService, ABC):
    """Interface for launching and managing what-if scenario simulations."""

    @abstractmethod
    def run_simulation(
        self, scenario_in: SimulationCreate, user_id: str
    ) -> SimulationScenario:
        """Configures and runs a simulation run."""
        pass

    @abstractmethod
    def get_scenario(self, scenario_id: str) -> Optional[SimulationScenario]:
        """Fetches a specific scenario run."""
        pass

    @abstractmethod
    def list_scenarios(self) -> Sequence[SimulationScenario]:
        """Lists all simulations."""
        pass


class SimulationService(SimulationServiceInterface):
    """Concrete implementation of SimulationService."""

    def __init__(self, scenario_repo: SimulationScenarioRepositoryInterface) -> None:
        self.scenario_repo = scenario_repo

    def run_simulation(
        self, scenario_in: SimulationCreate, user_id: str
    ) -> SimulationScenario:
        logger.info(
            f"Running scenario simulation: {scenario_in.name} by user: {user_id}"
        )
        scenario_id = f"sim-{uuid.uuid4()}"

        # Initialize pending scenario model
        scenario = SimulationScenario(
            id=scenario_id,
            name=scenario_in.name,
            parameters=scenario_in.parameters,
            base_dataset_id=scenario_in.base_dataset_id,
            status="pending",
            created_by=user_id,
        )
        saved_scenario = self.scenario_repo.save(scenario)

        # Simulate execution pipeline (in production, this would trigger an async celery/PubSub task)
        logger.info(
            f"Simulating asynchronous run execution for scenario: {scenario_id}"
        )

        # Fast-forward to completed state for boilerplate placeholder response
        saved_scenario.status = "completed"
        saved_scenario.results_url = f"https://storage.googleapis.com/streamline-data-ingestion/simulations/{scenario_id}_results.csv"
        self.scenario_repo.save(saved_scenario)

        return saved_scenario

    def get_scenario(self, scenario_id: str) -> Optional[SimulationScenario]:
        return self.scenario_repo.get_by_id(scenario_id)

    def list_scenarios(self) -> Sequence[SimulationScenario]:
        return self.scenario_repo.list_all()
