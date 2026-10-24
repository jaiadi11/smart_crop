"""Data models and value objects for Smart Crop Stage Advisor."""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone


class ComparisonStatus(str, Enum):
    WITHIN_RANGE = "WITHIN RANGE"
    BELOW_RANGE = "BELOW RANGE"
    ABOVE_RANGE = "ABOVE RANGE"
    REFERENCE_UNAVAILABLE = "REFERENCE UNAVAILABLE"
    INVALID_MEASUREMENT = "INVALID MEASUREMENT"


class ValidationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"


class MeasurementSource(str, Enum):
    MANUAL = "Manual"
    LIVE_SENSOR = "Live Sensor"
    MOCK_SENSOR = "Mock Sensor"


@dataclass
class ReferenceRangeRecord:
    """Represents a single agronomic parameter range for a crop-stage combination."""
    record_id: str
    crop_id: str
    crop_name: str
    stage_id: str
    stage_name: str
    parameter_id: str
    parameter_name: str
    min_value: Optional[float]
    max_value: Optional[float]
    unit: str
    source_title: str
    source_url: str
    validation_status: str
    notes: str

    def is_verified(self) -> bool:
        return (
            self.validation_status == ValidationStatus.VERIFIED.value
            and self.min_value is not None
            and self.max_value is not None
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReferenceRangeRecord":
        return cls(
            record_id=data.get("record_id", ""),
            crop_id=data.get("crop_id", ""),
            crop_name=data.get("crop_name", ""),
            stage_id=data.get("stage_id", ""),
            stage_name=data.get("stage_name", ""),
            parameter_id=data.get("parameter_id", ""),
            parameter_name=data.get("parameter_name", ""),
            min_value=float(data["min_value"]) if data.get("min_value") is not None else None,
            max_value=float(data["max_value"]) if data.get("max_value") is not None else None,
            unit=data.get("unit", ""),
            source_title=data.get("source_title", ""),
            source_url=data.get("source_url", ""),
            validation_status=data.get("validation_status", ValidationStatus.UNVERIFIED.value),
            notes=data.get("notes", ""),
        )


@dataclass
class MeasurementInput:
    """Incoming measurement before or during validation."""
    parameter_id: str
    value: Any
    unit: str
    source: str = MeasurementSource.MANUAL.value
    timestamp: Optional[str] = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ComparisonResult:
    """Detailed result of comparing a measured value against reference range."""
    crop_id: str
    crop_name: str
    stage_id: str
    stage_name: str
    category_id: str
    category_name: str
    parameter_id: str
    parameter_name: str
    source: str
    raw_value: Any
    normalized_value: Optional[float]
    measured_unit: str
    reference_min: Optional[float]
    reference_max: Optional[float]
    reference_unit: Optional[str]
    status: ComparisonStatus
    source_title: Optional[str]
    source_url: Optional[str]
    explanation: str
    is_verified: bool
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        res["status"] = self.status.value if isinstance(self.status, ComparisonStatus) else str(self.status)
        return res


@dataclass
class SensorPayload:
    """Validated sensor payload from hardware or mock simulator."""
    device_id: str
    timestamp: str
    source_type: str  # "LIVE_HARDWARE" or "MOCK_SIMULATION"
    readings: Dict[str, Dict[str, Any]]
    status: str = "OK"
    error_message: Optional[str] = None
    is_live: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
