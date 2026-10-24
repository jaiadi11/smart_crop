"""HTTP adapter for Wi-Fi connected agronomic microcontrollers (e.g. ESP32 / Arduino / Raspberry Pi)."""
import os
import requests
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from src.config import (
    DEFAULT_SENSOR_ENDPOINT,
    DEFAULT_SENSOR_TIMEOUT_SECONDS,
    DEFAULT_SENSOR_POLLING_INTERVAL_SECONDS,
    PARAMETERS,
    PARAMETER_ALIASES,
    CATEGORIES,
)
from src.models import SensorPayload
from src.hardware.sensor_interface import SensorInterface


class HttpSensorReceiver(SensorInterface):
    """
    Connects to physical Wi-Fi sensor module via HTTP.
    Strictly marked as Live Sensor; handles network faults and payload validation.
    Never fabricates readings.
    """

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        polling_interval_seconds: Optional[float] = None,
    ):
        self.endpoint_url = endpoint_url or os.getenv("SENSOR_HTTP_ENDPOINT", DEFAULT_SENSOR_ENDPOINT)
        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else float(
            os.getenv("SENSOR_TIMEOUT_SECONDS", str(DEFAULT_SENSOR_TIMEOUT_SECONDS))
        )
        self.polling_interval_seconds = polling_interval_seconds if polling_interval_seconds is not None else float(
            os.getenv("SENSOR_POLLING_INTERVAL_SECONDS", str(DEFAULT_SENSOR_POLLING_INTERVAL_SECONDS))
        )

    def is_live(self) -> bool:
        return True

    def source_name(self) -> str:
        return "Live Sensor"

    def fetch_measurements(self, category_id: Optional[str] = None) -> SensorPayload:
        """
        Poll the configured Wi-Fi endpoint and validate the received agronomic payload.
        """
        now_ts = datetime.now(timezone.utc).isoformat()
        try:
            response = requests.get(self.endpoint_url, timeout=self.timeout_seconds)
            response.raise_for_status()
        except requests.exceptions.ConnectTimeout:
            return SensorPayload(
                device_id="UNKNOWN",
                timestamp=now_ts,
                source_type="LIVE_HARDWARE",
                readings={},
                status="ERROR",
                error_message=f"Connection timed out after {self.timeout_seconds}s while contacting {self.endpoint_url}",
                is_live=True,
            )
        except requests.exceptions.ConnectionError:
            return SensorPayload(
                device_id="UNKNOWN",
                timestamp=now_ts,
                source_type="LIVE_HARDWARE",
                readings={},
                status="ERROR",
                error_message=f"Failed to connect to Wi-Fi sensor at {self.endpoint_url}. Ensure the hardware is powered on and joined to the local network.",
                is_live=True,
            )
        except requests.exceptions.HTTPError as he:
            return SensorPayload(
                device_id="UNKNOWN",
                timestamp=now_ts,
                source_type="LIVE_HARDWARE",
                readings={},
                status="ERROR",
                error_message=f"HTTP Error {response.status_code} from sensor endpoint: {str(he)}",
                is_live=True,
            )
        except Exception as e:
            return SensorPayload(
                device_id="UNKNOWN",
                timestamp=now_ts,
                source_type="LIVE_HARDWARE",
                readings={},
                status="ERROR",
                error_message=f"Unexpected communication failure: {str(e)}",
                is_live=True,
            )

        # Parse JSON
        try:
            data = response.json()
        except Exception:
            return SensorPayload(
                device_id="UNKNOWN",
                timestamp=now_ts,
                source_type="LIVE_HARDWARE",
                readings={},
                status="ERROR",
                error_message=f"Malformed sensor payload: Response from {self.endpoint_url} is not valid JSON.",
                is_live=True,
            )

        return self.validate_payload(data, category_id=category_id)

    def validate_payload(self, data: Any, category_id: Optional[str] = None) -> SensorPayload:
        """
        Validate payload structure, types, units, and timestamps.
        Supports:
        1. Single measurement contract: {"parameter": "temperature", "value": 28.4, "unit": "C", "timestamp": "..."}
        2. NPK single response contract: {"parameter": "npk", "nitrogen": ..., "phosphorus": ..., "potassium": ...}
        3. Multi-reading dictionary: {"device_id": "...", "readings": {"temperature": {"value": 24.5, "unit": "°C"}}}
        """
        now_ts = datetime.now(timezone.utc).isoformat()
        if not isinstance(data, dict):
            return SensorPayload(
                device_id="UNKNOWN",
                timestamp=now_ts,
                source_type="LIVE_HARDWARE",
                readings={},
                status="ERROR",
                error_message="Payload must be a JSON object containing sensor readings.",
                is_live=True,
            )

        device_id = str(data.get("device_id", "LIVE-ESP32-DEVICE"))
        ts = str(data.get("timestamp", now_ts))

        valid_readings: Dict[str, Dict[str, Any]] = {}
        unsupported_params: List[str] = []
        invalid_units: List[str] = []

        # Case 1: Payload has a top-level "parameter" key (e.g. single measurement or NPK response)
        if "parameter" in data:
            raw_param = str(data.get("parameter", "")).strip().lower()
            resolved_param = PARAMETER_ALIASES.get(raw_param, raw_param)

            if resolved_param == "npk":
                # NPK composite response containing all 3 nutrients
                npk_source = data.get("readings") or data.get("values") or data
                for nut in ["nitrogen", "phosphorus", "potassium"]:
                    nut_data = npk_source.get(nut)
                    if nut_data is None:
                        # Try short alias n, p, k
                        nut_data = npk_source.get(nut[0])

                    if isinstance(nut_data, dict):
                        n_val = nut_data.get("value")
                        n_unit = nut_data.get("unit", "mg/kg")
                    elif isinstance(nut_data, (int, float)):
                        n_val = nut_data
                        n_unit = str(data.get("unit", "mg/kg"))
                    else:
                        n_val = None
                        n_unit = "mg/kg"

                    try:
                        n_numeric = float(n_val) if n_val is not None else None
                    except (ValueError, TypeError):
                        n_numeric = None

                    valid_readings[nut] = {
                        "value": n_numeric,
                        "unit": str(n_unit).strip(),
                        "raw": nut_data,
                    }

            elif resolved_param in PARAMETERS:
                val = data.get("value")
                u = str(data.get("unit", PARAMETERS[resolved_param]["standard_unit"])).strip()

                try:
                    numeric_val = float(val) if val is not None else None
                except (ValueError, TypeError):
                    numeric_val = None

                # Unit validation
                compat_units = [cu.lower() for cu in PARAMETERS[resolved_param]["compatible_units"]]
                if u.lower() not in compat_units:
                    invalid_units.append(f"{resolved_param}: '{u}' (expected one of {PARAMETERS[resolved_param]['compatible_units']})")

                valid_readings[resolved_param] = {
                    "value": numeric_val,
                    "unit": u,
                    "raw": val,
                }
            else:
                return SensorPayload(
                    device_id=device_id,
                    timestamp=ts,
                    source_type="LIVE_HARDWARE",
                    readings={},
                    status="ERROR",
                    error_message=f"Unsupported sensor parameter: '{data.get('parameter')}'. Supported parameters: {list(PARAMETERS.keys())} or 'npk'",
                    is_live=True,
                )

        # Case 2: Multi-reading dictionary under "readings"
        elif "readings" in data:
            raw_readings = data.get("readings", {})
            if not isinstance(raw_readings, dict):
                return SensorPayload(
                    device_id=device_id,
                    timestamp=ts,
                    source_type="LIVE_HARDWARE",
                    readings={},
                    status="ERROR",
                    error_message="Field 'readings' must be an object/dict mapping parameter IDs to {value, unit}.",
                    is_live=True,
                )

            for p_key, p_val in raw_readings.items():
                param_raw = str(p_key).lower().strip()
                param_key = PARAMETER_ALIASES.get(param_raw, param_raw)

                if param_key not in PARAMETERS:
                    unsupported_params.append(str(p_key))
                    continue

                if isinstance(p_val, dict):
                    val = p_val.get("value")
                    u = str(p_val.get("unit", PARAMETERS[param_key]["standard_unit"])).strip()
                elif isinstance(p_val, (int, float)):
                    val = p_val
                    u = PARAMETERS[param_key]["standard_unit"]
                else:
                    continue

                try:
                    numeric_val = float(val) if val is not None else None
                except (ValueError, TypeError):
                    numeric_val = None

                # Unit validation
                compat_units = [cu.lower() for cu in PARAMETERS[param_key]["compatible_units"]]
                if u and u.lower() not in compat_units:
                    invalid_units.append(f"{param_key}: '{u}' (expected one of {PARAMETERS[param_key]['compatible_units']})")

                valid_readings[param_key] = {
                    "value": numeric_val,
                    "unit": u if u else PARAMETERS[param_key]["standard_unit"],
                    "raw": p_val,
                }

        # Case 3: Flat dictionary where keys may be parameter names
        else:
            found_any = False
            for p_key, p_val in data.items():
                param_raw = str(p_key).lower().strip()
                param_key = PARAMETER_ALIASES.get(param_raw, param_raw)
                if param_key in PARAMETERS:
                    found_any = True
                    if isinstance(p_val, dict):
                        val = p_val.get("value")
                        u = str(p_val.get("unit", PARAMETERS[param_key]["standard_unit"])).strip()
                    elif isinstance(p_val, (int, float)):
                        val = p_val
                        u = PARAMETERS[param_key]["standard_unit"]
                    else:
                        continue

                    try:
                        numeric_val = float(val) if val is not None else None
                    except (ValueError, TypeError):
                        numeric_val = None

                    valid_readings[param_key] = {
                        "value": numeric_val,
                        "unit": u if u else PARAMETERS[param_key]["standard_unit"],
                        "raw": p_val,
                    }

            if not found_any:
                return SensorPayload(
                    device_id=device_id,
                    timestamp=ts,
                    source_type="LIVE_HARDWARE",
                    readings={},
                    status="ERROR",
                    error_message="Payload structure unrecognized: missing 'parameter' or 'readings' field.",
                    is_live=True,
                )

        error_notes = []
        if unsupported_params:
            error_notes.append(f"Ignored unsupported parameters: {unsupported_params}")
        if invalid_units:
            error_notes.append(f"Invalid unit(s) detected: {'; '.join(invalid_units)}")

        return SensorPayload(
            device_id=device_id,
            timestamp=ts,
            source_type="LIVE_HARDWARE",
            readings=valid_readings,
            status="OK",
            error_message="; ".join(error_notes) if error_notes else None,
            is_live=True,
        )
