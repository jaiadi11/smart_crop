"""Pytest fixtures and test configurations."""
import pytest
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.dataset_loader import DatasetLoader
from src.services.comparison_service import ComparisonService
from src.services.measurement_service import MeasurementService
from src.hardware.mock_sensor import MockSensorSimulator
from src.hardware.http_receiver import HttpSensorReceiver


@pytest.fixture(scope="session")
def dataset_loader() -> DatasetLoader:
    return DatasetLoader()


@pytest.fixture(scope="session")
def comparison_service(dataset_loader: DatasetLoader) -> ComparisonService:
    return ComparisonService(dataset_loader=dataset_loader)


@pytest.fixture(scope="session")
def measurement_service(dataset_loader: DatasetLoader, comparison_service: ComparisonService) -> MeasurementService:
    return MeasurementService(
        dataset_loader=dataset_loader,
        comparison_service=comparison_service,
        live_receiver=HttpSensorReceiver(),
        mock_simulator=MockSensorSimulator(),
    )
