"""Abstract base interface for crop sensor hardware integrations."""
from abc import ABC, abstractmethod
from typing import Optional
from src.models import SensorPayload


class SensorInterface(ABC):
    """Hardware-independent interface defining the contract for sensor data acquisition."""

    @abstractmethod
    def fetch_measurements(self, category_id: Optional[str] = None) -> SensorPayload:
        """Fetch current measurement readings from device or simulator."""
        pass

    @abstractmethod
    def is_live(self) -> bool:
        """Returns True if the interface communicates with physical hardware, False if mock/simulation."""
        pass

    @abstractmethod
    def source_name(self) -> str:
        """User-facing source label ('Live Sensor' vs 'Mock Sensor')."""
        pass
