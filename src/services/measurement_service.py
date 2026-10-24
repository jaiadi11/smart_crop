"""Measurement orchestration service coordinating manual inputs and hardware sensors."""
from typing import Dict, List, Optional, Tuple, Any

from src.config import CATEGORIES, PARAMETERS
from src.models import (
    ComparisonResult,
    MeasurementSource,
    SensorPayload,
)
from src.data.dataset_loader import DatasetLoader
from src.services.comparison_service import ComparisonService
from src.services.recommendation_service import RecommendationService
from src.hardware.http_receiver import HttpSensorReceiver
from src.hardware.mock_sensor import MockSensorSimulator


class MeasurementService:
    """Coordinates data acquisition, validation, comparison, and recommendation generation."""

    def __init__(
        self,
        dataset_loader: Optional[DatasetLoader] = None,
        comparison_service: Optional[ComparisonService] = None,
        live_receiver: Optional[HttpSensorReceiver] = None,
        mock_simulator: Optional[MockSensorSimulator] = None,
    ):
        self.dataset_loader = dataset_loader or DatasetLoader()
        self.comparison_service = comparison_service or ComparisonService(self.dataset_loader)
        self.live_receiver = live_receiver or HttpSensorReceiver()
        self.mock_simulator = mock_simulator or MockSensorSimulator()

    def process_manual_entry(
        self,
        crop_id: str,
        stage_id: str,
        category_id: str,
        inputs: Dict[str, Tuple[Any, str]],
    ) -> Tuple[List[ComparisonResult], List[Dict[str, Any]]]:
        """
        Process manual user inputs for a selected category.
        inputs is a dict: {parameter_id: (value, unit)}
        Returns: (results, recommendations)
        """
        results = self.comparison_service.compare_category(
            crop_id=crop_id,
            stage_id=stage_id,
            category_id=category_id,
            measurements=inputs,
            source=MeasurementSource.MANUAL.value,
        )

        recommendations = [RecommendationService.get_recommendation(r) for r in results]
        return results, recommendations

    def fetch_live_sensor(
        self,
        endpoint_url: Optional[str] = None,
    ) -> SensorPayload:
        """Query physical Wi-Fi hardware adapter."""
        if endpoint_url:
            self.live_receiver.endpoint_url = endpoint_url
        return self.live_receiver.fetch_measurements()

    def fetch_mock_sensor(
        self,
        category_id: str,
        crop_id: str,
        stage_id: str,
        sim_mode: str = "within_range",
    ) -> SensorPayload:
        """Query mock sensor simulator."""
        self.mock_simulator.mode = sim_mode
        return self.mock_simulator.fetch_measurements(
            category_id=category_id,
            crop_id=crop_id,
            stage_id=stage_id,
        )

    def process_sensor_payload(
        self,
        crop_id: str,
        stage_id: str,
        category_id: str,
        payload: SensorPayload,
    ) -> Tuple[List[ComparisonResult], List[Dict[str, Any]]]:
        """
        Process telemetry received from sensor interface (Live or Mock).
        """
        source_label = MeasurementSource.LIVE_SENSOR.value if payload.is_live else MeasurementSource.MOCK_SENSOR.value

        measurements: Dict[str, Tuple[Any, str]] = {}
        for pid, pdata in payload.readings.items():
            if isinstance(pdata, dict):
                measurements[pid] = (pdata.get("value"), pdata.get("unit", ""))
            else:
                measurements[pid] = (pdata, PARAMETERS.get(pid, {}).get("standard_unit", ""))

        results = self.comparison_service.compare_category(
            crop_id=crop_id,
            stage_id=stage_id,
            category_id=category_id,
            measurements=measurements,
            source=source_label,
            timestamp=payload.timestamp,
        )

        recommendations = [RecommendationService.get_recommendation(r) for r in results]
        return results, recommendations
