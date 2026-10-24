"""Explicit Mock Sensor Simulator for testing and hardware-free demonstration."""
import random
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from src.config import PARAMETERS, CATEGORIES
from src.models import SensorPayload
from src.hardware.sensor_interface import SensorInterface
from src.data.dataset_loader import DatasetLoader


class MockSensorSimulator(SensorInterface):
    """
    Simulated sensor device strictly separated from live hardware.
    Never reports as live hardware.
    """

    def __init__(self, mode: str = "within_range"):
        """
        mode: 'within_range', 'below_range', 'above_range', or 'random'
        """
        self.mode = mode
        self.dataset_loader = DatasetLoader()

    def is_live(self) -> bool:
        return False

    def source_name(self) -> str:
        return "Mock Sensor"

    def fetch_measurements(
        self,
        category_id: Optional[str] = None,
        crop_id: str = "maize",
        stage_id: str = "vegetative_growth",
    ) -> SensorPayload:
        """
        Generate synthetic telemetry clearly marked as MOCK_SIMULATION.
        """
        now_ts = datetime.now(timezone.utc).isoformat()
        readings: Dict[str, Dict[str, Any]] = {}

        # Determine which parameters to populate
        if category_id and category_id.lower() in CATEGORIES:
            param_ids = CATEGORIES[category_id.lower()]["parameter_ids"]
        else:
            param_ids = list(PARAMETERS.keys())

        for pid in param_ids:
            param_cfg = PARAMETERS[pid]
            rec = self.dataset_loader.get_record(crop_id, stage_id, pid)
            std_unit = param_cfg["standard_unit"]

            if rec and rec.is_verified():
                min_v = rec.min_value
                max_v = rec.max_value
                span = max_v - min_v

                if self.mode == "below_range":
                    sim_val = round(max(0.0, min_v - (span * 0.25) - 1.0), 2)
                elif self.mode == "above_range":
                    sim_val = round(max_v + (span * 0.25) + 1.0, 2)
                elif self.mode == "within_range":
                    sim_val = round(min_v + (span * 0.5), 2)
                else:  # random
                    choice = random.choice(["below", "within", "above"])
                    if choice == "below":
                        sim_val = round(max(0.0, min_v - (span * 0.2) - 0.5), 2)
                    elif choice == "above":
                        sim_val = round(max_v + (span * 0.2) + 0.5, 2)
                    else:
                        sim_val = round(random.uniform(min_v, max_v), 2)
            else:
                # Default baseline fallback for unverified
                defaults = {
                    "temperature": 26.5,
                    "relative_humidity": 65.0,
                    "soil_moisture": 70.0,
                    "soil_ph": 6.5,
                    "light_intensity": 35000.0,
                    "nitrogen": 150.0,
                    "phosphorus": 20.0,
                    "potassium": 160.0,
                }
                sim_val = defaults.get(pid, 20.0)

            readings[pid] = {
                "value": sim_val,
                "unit": std_unit,
                "is_simulated": True,
            }

        return SensorPayload(
            device_id="MOCK-ESP32-SIMULATOR-001",
            timestamp=now_ts,
            source_type="MOCK_SIMULATION",
            readings=readings,
            status="OK",
            error_message=None,
            is_live=False,
        )
