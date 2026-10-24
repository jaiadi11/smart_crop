"""Tests for Wi-Fi sensor adapter, mock simulator, and protocol validation."""
import pytest
from unittest.mock import patch, MagicMock
import requests

from src.models import ComparisonStatus, MeasurementSource
from src.hardware.http_receiver import HttpSensorReceiver
from src.hardware.mock_sensor import MockSensorSimulator
from src.services.measurement_service import MeasurementService


def test_http_sensor_single_measurement_payload_contract():
    """
    Verify the Section 4 example contract:
    {
      "parameter": "temperature",
      "value": 28.4,
      "unit": "C",
      "timestamp": "2026-10-24T10:00:00Z"
    }
    """
    receiver = HttpSensorReceiver()
    raw_payload = {
        "parameter": "temperature",
        "value": 28.4,
        "unit": "C",
        "timestamp": "2026-10-24T10:00:00Z",
    }

    payload = receiver.validate_payload(raw_payload)
    assert payload.status == "OK"
    assert payload.is_live is True
    assert payload.timestamp == "2026-10-24T10:00:00Z"
    assert "temperature" in payload.readings
    assert payload.readings["temperature"]["value"] == 28.4
    assert payload.readings["temperature"]["unit"] == "C"


def test_http_sensor_npk_composite_payload_contract():
    """
    Verify the Section 4 NPK contract supporting one response containing
    all three nutrient values and their declared units.
    """
    receiver = HttpSensorReceiver()
    raw_payload = {
        "parameter": "npk",
        "nitrogen": {"value": 175.0, "unit": "mg/kg"},
        "phosphorus": {"value": 22.0, "unit": "mg/kg"},
        "potassium": {"value": 180.0, "unit": "mg/kg"},
        "timestamp": "2026-10-24T10:00:00Z",
    }

    payload = receiver.validate_payload(raw_payload)
    assert payload.status == "OK"
    assert payload.is_live is True
    assert len(payload.readings) == 3
    assert payload.readings["nitrogen"]["value"] == 175.0
    assert payload.readings["phosphorus"]["value"] == 22.0
    assert payload.readings["potassium"]["value"] == 180.0
    assert payload.readings["nitrogen"]["unit"] == "mg/kg"


def test_http_sensor_valid_multi_readings_payload():
    """Verify that a valid multi-reading JSON sensor payload is correctly parsed and validated."""
    receiver = HttpSensorReceiver()
    raw_payload = {
        "device_id": "ESP32-FIELD-NODE-01",
        "timestamp": "2026-10-24T12:00:00Z",
        "readings": {
            "temperature": {"value": 24.5, "unit": "°C"},
            "relative_humidity": {"value": 65.0, "unit": "%"},
            "soil_moisture": {"value": 72.0, "unit": "%"},
            "soil_ph": {"value": 6.4, "unit": "pH"},
            "nitrogen": {"value": 180.0, "unit": "mg/kg"},
            "phosphorus": {"value": 22.0, "unit": "mg/kg"},
            "potassium": {"value": 190.0, "unit": "mg/kg"},
        },
    }

    payload = receiver.validate_payload(raw_payload)
    assert payload.status == "OK"
    assert payload.device_id == "ESP32-FIELD-NODE-01"
    assert payload.is_live is True
    assert payload.readings["temperature"]["value"] == 24.5
    assert payload.readings["nitrogen"]["value"] == 180.0


def test_http_sensor_handles_unsupported_parameters():
    """Verify that unrecognized sensor parameters are flagged or ignored without crashing."""
    receiver = HttpSensorReceiver()
    # In single-parameter mode, unknown parameter returns ERROR
    single_unknown = {
        "parameter": "wind_speed",
        "value": 15.0,
        "unit": "m/s",
    }
    p_single = receiver.validate_payload(single_unknown)
    assert p_single.status == "ERROR"
    assert "Unsupported sensor parameter" in p_single.error_message

    # In multi-reading mode, unsupported parameter is ignored with note
    multi_unknown = {
        "device_id": "ESP32-01",
        "timestamp": "2026-10-24T12:00:00Z",
        "readings": {
            "temperature": {"value": 25.0, "unit": "°C"},
            "unsupported_wind_speed": {"value": 12.0, "unit": "m/s"},
            "unknown_co2_level": {"value": 400.0, "unit": "ppm"},
        },
    }
    payload = receiver.validate_payload(multi_unknown)
    assert payload.status == "OK"
    assert "temperature" in payload.readings
    assert "unsupported_wind_speed" not in payload.readings
    assert "Ignored unsupported parameters" in payload.error_message


def test_http_sensor_handles_wrong_units():
    """Verify that wrong/incompatible units in sensor payload are detected."""
    receiver = HttpSensorReceiver()
    raw_payload = {
        "parameter": "temperature",
        "value": 25.0,
        "unit": "lux",  # Wrong unit for temperature
    }
    payload = receiver.validate_payload(raw_payload)
    assert payload.status == "OK"
    assert "Invalid unit(s) detected" in payload.error_message
    assert "temperature: 'lux'" in payload.error_message


def test_http_sensor_handles_connection_timeout():
    """Verify that network timeout returns a clear ERROR payload."""
    receiver = HttpSensorReceiver(endpoint_url="http://192.168.1.200:8080/sensors", timeout_seconds=1.0)
    with patch("requests.get", side_effect=requests.exceptions.ConnectTimeout("Timed out")):
        payload = receiver.fetch_measurements()

    assert payload.status == "ERROR"
    assert payload.is_live is True
    assert "Connection timed out" in payload.error_message


def test_http_sensor_handles_connection_error():
    """Verify that host unreachable / refused connection returns a clear ERROR payload."""
    receiver = HttpSensorReceiver(endpoint_url="http://192.168.1.200:8080/sensors")
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError("Connection refused")):
        payload = receiver.fetch_measurements()

    assert payload.status == "ERROR"
    assert payload.is_live is True
    assert "Failed to connect to Wi-Fi sensor" in payload.error_message


def test_http_sensor_handles_malformed_json():
    """Verify that non-JSON response from device returns a clear ERROR payload."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = ValueError("Invalid JSON syntax")

    receiver = HttpSensorReceiver()
    with patch("requests.get", return_value=mock_response):
        payload = receiver.fetch_measurements()

    assert payload.status == "ERROR"
    assert "Malformed sensor payload" in payload.error_message


def test_http_sensor_configurable_timeout_and_polling():
    """Verify configurable timeout and polling intervals."""
    receiver = HttpSensorReceiver(
        endpoint_url="http://10.0.0.5:5000/telemetry",
        timeout_seconds=8.0,
        polling_interval_seconds=15.0,
    )
    assert receiver.endpoint_url == "http://10.0.0.5:5000/telemetry"
    assert receiver.timeout_seconds == 8.0
    assert receiver.polling_interval_seconds == 15.0


def test_mock_sensor_strictly_separated_from_live():
    """
    CRITICAL: Verify prevention of mock readings being represented as live measurements.
    Mock sensor must never report is_live = True or source_type = LIVE_HARDWARE.
    """
    mock_sim = MockSensorSimulator()
    live_recv = HttpSensorReceiver()

    # Base contract check
    assert mock_sim.is_live() is False
    assert live_recv.is_live() is True

    assert mock_sim.source_name() == "Mock Sensor"
    assert live_recv.source_name() == "Live Sensor"

    # Generated payload check
    payload = mock_sim.fetch_measurements(category_id="temperature", crop_id="maize", stage_id="vegetative_growth")
    assert payload.is_live is False
    assert payload.source_type == "MOCK_SIMULATION"
    assert "MOCK" in payload.device_id


def test_sensor_payload_processing_flow(measurement_service: MeasurementService):
    """Test full pipeline of receiving sensor telemetry and evaluating comparison."""
    mock_sim = MockSensorSimulator(mode="within_range")
    payload = mock_sim.fetch_measurements(category_id="npk", crop_id="maize", stage_id="vegetative_growth")

    results, recs = measurement_service.process_sensor_payload(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="npk",
        payload=payload,
    )

    assert len(results) == 3
    assert results[0].source == MeasurementSource.MOCK_SENSOR.value
    # In within_range mode, nutrients evaluate to WITHIN_RANGE
    for r in results:
        assert r.status == ComparisonStatus.WITHIN_RANGE
