"""Input forms for Manual Entry, Live Sensor, and Mock Sensor modes."""
import streamlit as st
from typing import Dict, Tuple, Any, Optional

from src.config import (
    PARAMETERS,
    CATEGORIES,
    DEFAULT_SENSOR_ENDPOINT,
    DEFAULT_SENSOR_TIMEOUT_SECONDS,
    DEFAULT_SENSOR_POLLING_INTERVAL_SECONDS,
)
from src.services.measurement_service import MeasurementService


def render_measurement_form(
    crop_id: str,
    stage_id: str,
    category_id: str,
    measurement_mode: str,
    measurement_service: MeasurementService,
) -> None:
    """Render the active input form based on selected mode and category."""
    st.subheader(f"📊 Measurement Input: {CATEGORIES[category_id]['name']}")

    if measurement_mode == "Manual Entry":
        render_manual_entry_form(crop_id, stage_id, category_id, measurement_service)
    elif measurement_mode == "Live Sensor (Wi-Fi)":
        render_live_sensor_form(crop_id, stage_id, category_id, measurement_service)
    elif measurement_mode == "Mock Sensor (Simulation)":
        render_mock_sensor_form(crop_id, stage_id, category_id, measurement_service)


def render_manual_entry_form(
    crop_id: str,
    stage_id: str,
    category_id: str,
    measurement_service: MeasurementService,
) -> None:
    """Render manual entry fields. For NPK, requests Nitrogen, Phosphorus, Potassium together."""
    st.info("Enter your laboratory or field hand-probe readings below. Only fields relevant to the selected category are displayed.")

    category_cfg = CATEGORIES[category_id]
    param_ids = category_cfg["parameter_ids"]

    with st.form(key=f"form_manual_{category_id}"):
        inputs: Dict[str, Tuple[Any, str]] = {}

        if category_id == "npk":
            st.markdown("##### Soil Macronutrient Suite (NPK)")
            st.caption("Standard laboratory soil test values must be expressed in mg/kg (or ppm / kg/ha). All three nutrients are required.")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Available Nitrogen (N)**")
                n_val = st.number_input("Nitrogen Value", value=160.0, step=5.0, key="manual_n_val", help="Soil available nitrogen in mg/kg")
                n_unit = st.selectbox("Unit (N)", ["mg/kg", "ppm", "kg/ha"], key="manual_n_unit")
                inputs["nitrogen"] = (n_val, n_unit)

            with col2:
                st.markdown("**Available Phosphorus (P)**")
                p_val = st.number_input("Phosphorus Value", value=20.0, step=1.0, key="manual_p_val", help="Soil available phosphorus in mg/kg")
                p_unit = st.selectbox("Unit (P)", ["mg/kg", "ppm", "kg/ha"], key="manual_p_unit")
                inputs["phosphorus"] = (p_val, p_unit)

            with col3:
                st.markdown("**Available Potassium (K)**")
                k_val = st.number_input("Potassium Value", value=180.0, step=5.0, key="manual_k_val", help="Soil available potassium in mg/kg")
                k_unit = st.selectbox("Unit (K)", ["mg/kg", "ppm", "kg/ha"], key="manual_k_unit")
                inputs["potassium"] = (k_val, k_unit)
        else:
            pid = param_ids[0]
            pcfg = PARAMETERS[pid]
            col1, col2 = st.columns([3, 1])

            # Provide agronomic guidance hints on standard scale
            hints = {
                "temperature": "Ambient or canopy temperature in °C",
                "relative_humidity": "Percentage relative humidity (valid: 0–100%)",
                "soil_moisture": "Percentage volumetric soil water content (valid: 0–100%)",
                "soil_ph": "Soil reaction on the standard pH scale (valid: 0.0–14.0)",
                "light_intensity": "Canopy illuminance in lux",
            }
            default_vals = {
                "temperature": 25.0,
                "relative_humidity": 65.0,
                "soil_moisture": 65.0,
                "soil_ph": 6.5,
                "light_intensity": 35000.0,
            }

            with col1:
                val = st.number_input(
                    f"Measured {pcfg['name']}",
                    value=default_vals.get(pid, 25.0),
                    step=0.1 if pid == "soil_ph" else 1.0,
                    help=hints.get(pid, ""),
                    key=f"manual_{pid}_val",
                )
            with col2:
                unit = st.selectbox("Unit", pcfg["compatible_units"], key=f"manual_{pid}_unit")
            inputs[pid] = (val, unit)

        submit_btn = st.form_submit_button("📊 Submit & Compare Measurement", use_container_width=True)

        if submit_btn:
            results, recs = measurement_service.process_manual_entry(
                crop_id=crop_id,
                stage_id=stage_id,
                category_id=category_id,
                inputs=inputs,
            )
            st.session_state["comparison_results"] = results
            st.session_state["recommendations"] = recs
            st.session_state.pop("sensor_payload", None)
            st.session_state.pop("sensor_error", None)


def render_live_sensor_form(
    crop_id: str,
    stage_id: str,
    category_id: str,
    measurement_service: MeasurementService,
) -> None:
    """Render Wi-Fi HTTP sensor integration form with connection diagnostics."""
    st.markdown(
        """
        > [!IMPORTANT]
        > **Live Wi-Fi Hardware Integration**: This adapter communicates with physical microcontroller hardware
        > (e.g. ESP32, ESP8266, Arduino Wi-Fi, Raspberry Pi Pico W) via local network HTTP GET requests.
        > It strictly validates network responses, parameters, units, and timestamps.
        """
    )

    # Connection Status Indicator
    last_payload = st.session_state.get("sensor_payload")
    sensor_error = st.session_state.get("sensor_error")

    if sensor_error:
        conn_badge = "🔴 Connection Fault / Error"
        conn_color = "#fee2e2"
        conn_border = "#ef4444"
    elif last_payload and last_payload.is_live and last_payload.status == "OK":
        conn_badge = f"🟢 Connected & Verified (Device: {last_payload.device_id})"
        conn_color = "#ecfdf5"
        conn_border = "#10b981"
    else:
        conn_badge = "⚪ Ready to Poll (Endpoint Unverified)"
        conn_color = "#f3f4f6"
        conn_border = "#9ca3af"

    st.markdown(
        f'<div style="background-color: {conn_color}; border: 1.5px solid {conn_border}; border-radius: 8px; '
        f'padding: 8px 14px; margin-bottom: 14px; font-weight: 600; font-size: 0.9rem;">{conn_badge}</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        endpoint = st.text_input(
            "Microcontroller HTTP Endpoint",
            value=DEFAULT_SENSOR_ENDPOINT,
            help="HTTP URL exposed by the Wi-Fi microcontroller (e.g., http://192.168.1.100:8080/sensors)",
            key="live_endpoint_input",
        )
    with col2:
        timeout = st.number_input(
            "Timeout (s)",
            min_value=1.0,
            max_value=30.0,
            value=DEFAULT_SENSOR_TIMEOUT_SECONDS,
            step=1.0,
            help="Maximum seconds to wait for microcontroller response before timeout",
            key="live_timeout_input",
        )
    with col3:
        polling_interval = st.number_input(
            "Interval (s)",
            min_value=1.0,
            max_value=300.0,
            value=DEFAULT_SENSOR_POLLING_INTERVAL_SECONDS,
            step=5.0,
            help="Recommended polling interval for scheduled sensor readings",
            key="live_interval_input",
        )

    if st.button("📡 Measure / Fetch Live Sensor Reading", use_container_width=True, key="btn_read_live_sensor"):
        measurement_service.live_receiver.endpoint_url = endpoint
        measurement_service.live_receiver.timeout_seconds = timeout
        measurement_service.live_receiver.polling_interval_seconds = polling_interval

        with st.spinner(f"Contacting Wi-Fi sensor at {endpoint}..."):
            payload = measurement_service.fetch_live_sensor(endpoint)

        st.session_state["sensor_payload"] = payload

        if payload.status == "ERROR":
            st.session_state["sensor_error"] = payload.error_message
            st.session_state.pop("comparison_results", None)
            st.session_state.pop("recommendations", None)
            st.error(f"❌ Hardware Communication Error: {payload.error_message}")
            st.info(
                "💡 **Troubleshooting Tips:**\n"
                "- Verify that the microcontroller is powered on and connected to the same Wi-Fi subnet.\n"
                "- Confirm the microcontroller's local IP address and HTTP port.\n"
                "- Ensure the HTTP server returns a JSON payload with valid parameter names and units.\n"
                "- If no physical hardware is present, switch to **Mock Sensor (Simulation)** in the sidebar."
            )
        else:
            st.session_state.pop("sensor_error", None)
            # Display received telemetry details
            st.success(f"✅ Received valid telemetry from {payload.device_id} at {payload.timestamp}")

            results, recs = measurement_service.process_sensor_payload(
                crop_id=crop_id,
                stage_id=stage_id,
                category_id=category_id,
                payload=payload,
            )
            st.session_state["comparison_results"] = results
            st.session_state["recommendations"] = recs


def render_mock_sensor_form(
    crop_id: str,
    stage_id: str,
    category_id: str,
    measurement_service: MeasurementService,
) -> None:
    """Render Mock Simulator form, explicitly marked as synthetic simulation."""
    st.warning(
        "⚠️ **MOCK SENSOR MODE**: Telemetry generated in this mode is synthetic for testing purposes. "
        "It is strictly separated from physical hardware and will never be represented as live data."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        sim_scenario = st.selectbox(
            "Simulation Scenario",
            [
                ("within_range", "Optimal / Within Reference Range"),
                ("below_range", "Stress Deficit / Below Reference Range"),
                ("above_range", "Stress Excess / Above Reference Range"),
                ("random", "Random Microclimate Fluctuation"),
            ],
            format_func=lambda x: x[1],
            key="mock_scenario_select",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("🧪 Generate & Compare Mock Telemetry", use_container_width=True, key="btn_mock_telemetry")

    if generate_btn:
        payload = measurement_service.fetch_mock_sensor(
            category_id=category_id,
            crop_id=crop_id,
            stage_id=stage_id,
            sim_mode=sim_scenario[0],
        )
        st.session_state["sensor_payload"] = payload
        st.session_state.pop("sensor_error", None)

        results, recs = measurement_service.process_sensor_payload(
            crop_id=crop_id,
            stage_id=stage_id,
            category_id=category_id,
            payload=payload,
        )
        st.session_state["comparison_results"] = results
        st.session_state["recommendations"] = recs
