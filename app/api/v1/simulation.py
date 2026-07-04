from typing import Any, Optional, Sequence
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_forecast_service, get_simulation_service
from app.schemas.simulation import SimulationCreate, SimulationResponse
from app.services.forecast.service import ForecastServiceInterface
from app.services.simulation.service import SimulationServiceInterface

router = APIRouter()


@router.post(
    "/run",
    response_model=SimulationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_scenario_simulation(
    request: SimulationCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    simulation_service: SimulationServiceInterface = Depends(get_simulation_service),
) -> SimulationResponse:
    """Configures and runs an analytical scenario simulation in the workspace."""
    user_id = current_user.get("uid", "anonymous")
    scenario = simulation_service.run_simulation(request, user_id)
    return SimulationResponse.model_validate(scenario)


@router.get("/scenarios", response_model=list[SimulationResponse])
def list_scenario_simulations(
    current_user: dict[str, Any] = Depends(get_current_user),
    simulation_service: SimulationServiceInterface = Depends(get_simulation_service),
) -> Sequence[Any]:
    """Retrieves all previous simulation runs."""
    scenarios = simulation_service.list_scenarios()
    return [SimulationResponse.model_validate(s) for s in scenarios]


@router.get("/scenario/{id}", response_model=SimulationResponse)
def get_scenario_simulation(
    id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    simulation_service: SimulationServiceInterface = Depends(get_simulation_service),
) -> SimulationResponse:
    """Retrieves the parameter settings and results location for a specific scenario."""
    scenario = simulation_service.get_scenario(id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation run '{id}' not found.",
        )
    return SimulationResponse.model_validate(scenario)


@router.get("/forecast")
def run_timeseries_forecast(
    dataset_id: str,
    target_column: str,
    periods: Optional[int] = 30,
    current_user: dict[str, Any] = Depends(get_current_user),
    forecast_service: ForecastServiceInterface = Depends(get_forecast_service),
) -> dict[str, Any]:
    """Triggers GPU-accelerated (RAPIDS cuDF/cuML) linear forecasting projections on BigQuery data."""
    return forecast_service.generate_forecast(
        dataset_id=dataset_id, target_column=target_column, periods=periods or 30
    )

