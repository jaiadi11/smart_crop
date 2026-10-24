"""Smart Crop Stage Advisor - Main Streamlit Application."""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any

from src.config import CROPS, GROWTH_STAGES, CATEGORIES, PARAMETERS
from src.models import ComparisonStatus, ComparisonResult
from src.data.dataset_loader import DatasetLoader
from src.services.measurement_service import MeasurementService
from src.ui.selectors import render_selectors
from src.ui.measurement_form import render_measurement_form


st.set_page_config(
    page_title="Smart Crop Stage Advisor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_dataset_loader() -> DatasetLoader:
    return DatasetLoader()


@st.cache_resource
def get_measurement_service() -> MeasurementService:
    loader = get_dataset_loader()
    return MeasurementService(dataset_loader=loader)


def render_status_badge(status: ComparisonStatus) -> str:
    """Return colored HTML badge corresponding to status."""
    styles = {
        ComparisonStatus.WITHIN_RANGE: ("#10b981", "#ecfdf5", "✅ WITHIN RANGE"),
        ComparisonStatus.BELOW_RANGE: ("#f59e0b", "#fffbeb", "⚠️ BELOW RANGE"),
        ComparisonStatus.ABOVE_RANGE: ("#ef4444", "#fef2f2", "🚨 ABOVE RANGE"),
        ComparisonStatus.REFERENCE_UNAVAILABLE: ("#6b7280", "#f3f4f6", "⚪ REFERENCE UNAVAILABLE"),
        ComparisonStatus.INVALID_MEASUREMENT: ("#dc2626", "#fee2e2", "❌ INVALID MEASUREMENT"),
    }
    border, bg, label = styles.get(status, ("#6b7280", "#f3f4f6", str(status)))
    return (
        f'<span style="background-color: {bg}; color: {border}; border: 1.5px solid {border}; '
        f'padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.9rem;">{label}</span>'
    )


def render_comparison_card(result: ComparisonResult, recommendation: Dict[str, Any]) -> None:
    """Render a comprehensive result card adhering to Section E display specifications."""
    with st.container():
        st.markdown(
            f"""
            <div style="border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px; margin-bottom: 20px; background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f3f4f6; padding-bottom: 12px; margin-bottom: 16px;">
                    <div>
                        <h3 style="margin: 0; color: #111827;">{result.parameter_name}</h3>
                        <span style="font-size: 0.85rem; color: #6b7280;">Category: {result.category_name} &bull; Timestamp: {result.timestamp}</span>
                    </div>
                    <div>
                        {render_status_badge(result.status)}
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="Measured Value",
                value=f"{result.raw_value} {result.measured_unit}" if result.raw_value is not None else "N/A",
                delta=f"Norm: {result.normalized_value} {result.reference_unit}" if (result.normalized_value is not None and result.measured_unit != result.reference_unit) else None,
            )
        with col2:
            st.metric(
                label="Agronomic Target Range",
                value=f"{result.reference_min} - {result.reference_max} {result.reference_unit}" if result.is_verified else "UNVERIFIED",
            )
        with col3:
            st.metric(
                label="Measurement Source",
                value=result.source,
            )
        with col4:
            st.metric(
                label="Crop & Stage",
                value=result.crop_name,
                help=f"Stage: {result.stage_name}",
            )

        st.markdown(f"**Explanation:** {result.explanation}")

        # Scientific provenance
        if result.source_title:
            st.markdown(
                f"""
                <div style="font-size: 0.85rem; color: #4b5563; background: #f9fafb; padding: 10px; border-radius: 6px; margin-top: 10px;">
                    📚 <strong>Reference Source:</strong> {result.source_title} 
                    {f'<br>🔗 <a href="{result.source_url}" target="_blank" style="color: #2563eb;">View Reference Documentation</a>' if result.source_url else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Agronomic Action
        if recommendation:
            st.markdown(
                f"""
                <div style="font-size: 0.9rem; padding: 12px; border-radius: 6px; margin-top: 10px; background-color: #f0fdf4; border-left: 4px solid #10b981;">
                    🎯 <strong>Agronomic Guidance:</strong> {recommendation.get('action')}<br>
                    <span style="color: #374151;">{recommendation.get('guidance')}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)


def main():
    st.title("🌾 Smart Crop Stage Advisor")
    st.caption("Database-Driven Agronomic Decision Support & Wi-Fi Sensor Telemetry Comparison")

    loader = get_dataset_loader()
    measurement_service = get_measurement_service()

    # Sidebar Selectors
    crop_id, stage_id, category_id, measurement_mode = render_selectors()

    # Tabs for Workflow, Reference Database, Scientific Validation Report, and Hardware Protocol
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔬 Stage Advisor & Comparison",
        "📖 Reference Database (25 Combinations)",
        "📋 Agronomic Validation Report",
        "🔌 Wi-Fi Protocol & Hardware Docs",
    ])

    with tab1:
        # Context header with Reset button
        h_col1, h_col2 = st.columns([4, 1])
        with h_col1:
            st.markdown(
                f"""
                #### Active Selection: **{CROPS[crop_id]['name']}** &bull; **{GROWTH_STAGES[stage_id]['name']}** &bull; Parameter: **{CATEGORIES[category_id]['name']}**
                """
            )
        with h_col2:
            if st.button("🔄 Reset / Clear", key="btn_main_reset", use_container_width=True):
                st.session_state.pop("comparison_results", None)
                st.session_state.pop("recommendations", None)
                st.session_state.pop("sensor_payload", None)
                st.session_state.pop("sensor_error", None)
                st.rerun()

        # Render form
        render_measurement_form(crop_id, stage_id, category_id, measurement_mode, measurement_service)

        # Render Results Section if available
        results: Optional[List[ComparisonResult]] = st.session_state.get("comparison_results")
        recs: Optional[List[Dict[str, Any]]] = st.session_state.get("recommendations")

        if results:
            st.markdown("---")
            r_col1, r_col2 = st.columns([4, 1])
            with r_col1:
                st.subheader("📋 Agronomic Comparison Results")
            with r_col2:
                if st.button("🔄 New Measurement", key="btn_new_measurement", use_container_width=True):
                    st.session_state.pop("comparison_results", None)
                    st.session_state.pop("recommendations", None)
                    st.session_state.pop("sensor_payload", None)
                    st.session_state.pop("sensor_error", None)
                    st.rerun()


            # Check if this was an NPK composite category
            if category_id == "npk":
                st.info(
                    "NPK macronutrients are evaluated independently. Each nutrient has a distinct physiological role, uptake mechanism, and reference threshold."
                )

            for idx, res in enumerate(results):
                rec = recs[idx] if recs and idx < len(recs) else {}
                render_comparison_card(res, rec)
        else:
            if not st.session_state.get("sensor_error"):
                st.info("Select inputs above and click evaluate to perform agronomic comparison.")

    with tab2:
        st.subheader("📚 25 Crop-Stage Agronomic Database (200 Records)")
        st.write(
            "Explore all 200 reference records across the 5 crops and 5 growth stages. Filter by crop or parameter."
        )

        f_crop = st.selectbox("Filter Crop", ["All"] + [c["name"] for c in CROPS.values()], key="db_crop_filter")
        f_stage = st.selectbox("Filter Growth Stage", ["All"] + [s["name"] for s in GROWTH_STAGES.values()], key="db_stage_filter")
        f_status = st.selectbox("Filter Status", ["All", "VERIFIED", "UNVERIFIED"], key="db_status_filter")

        all_records = loader.get_all_records()
        filtered = []
        for r in all_records:
            if f_crop != "All" and r.crop_name != f_crop:
                continue
            if f_stage != "All" and r.stage_name != f_stage:
                continue
            if f_status != "All" and r.validation_status != f_status:
                continue
            filtered.append({
                "Crop": r.crop_name,
                "Stage": r.stage_name,
                "Parameter": r.parameter_name,
                "Min": str(r.min_value) if r.min_value is not None else "—",
                "Max": str(r.max_value) if r.max_value is not None else "—",
                "Unit": r.unit,
                "Status": r.validation_status,
                "Source": r.source_title,
                "Notes": r.notes,
            })


        df = pd.DataFrame(filtered)
        st.dataframe(df, use_container_width=True, height=500)
        st.caption(f"Showing {len(filtered)} of {len(all_records)} total parameter records.")

    with tab3:
        st.subheader("📊 Dataset Provenance & Agronomic Validation Report")
        report = loader.validation_report

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Parameter Records", report["total_actual_records"])
        m2.metric("Crop-Stage Combinations", report["total_combinations"])
        m3.metric("Scientifically Verified", report["verified_count"])
        m4.metric("Unverified (Agronomic Gaps)", report["unverified_count"])

        st.markdown("### Agronomic Data Integrity Assessment")
        if report["is_valid"]:
            st.success("✅ Dataset Integrity Pass: All 25 crop-stage combinations and 200 parameter records exist without corruption.")
        else:
            st.error("❌ Dataset integrity failed. Check missing or invalid records.")

        st.markdown(
            """
            #### Transparency & Agronomic Standard Gaps
            In adherence to scientific rigor:
            - **Subterranean Germination Lux**: Photic sensor boundaries for germinating seeds underground are marked `UNVERIFIED` because ambient light does not govern seedbed imbibition.
            - **Maturity / Senescence Photoperiod & Nutrients**: Standard university agronomic packages prohibit late nutrient applications to prevent vegetative re-flushes, lodging, and delayed ripening. Light intensity is non-limiting at senescence. These records are explicitly marked `UNVERIFIED` with null values.
            - **The system refuses to classify field readings against unverified records**, returning `REFERENCE UNAVAILABLE`.
            """
        )

        with st.expander("🔎 View All 25 Unverified Agronomic Gaps & Scientific Rationale"):
            unv_df = pd.DataFrame(report.get("unverified_records", []))
            st.dataframe(unv_df, use_container_width=True)

    with tab4:
        st.subheader("🔌 Wi-Fi Hardware Communication Protocol")
        st.markdown(
            """
            ### Hardware Interface Contract
            The application communicates with microcontroller field nodes (e.g., ESP32, ESP8266, Arduino Nano RP2040 Connect, Raspberry Pi Pico W) via local network Wi-Fi.

            #### Expected HTTP GET Response Schema
            When the application polls the configured endpoint `GET http://<device-ip>:<port>/sensors`, the microcontroller must reply with `200 OK` and a JSON payload adhering to the following structure:

            ```json
            {
              "device_id": "ESP32-AGRI-NODE-01",
              "timestamp": "2026-10-24T12:00:00Z",
              "readings": {
                "temperature": { "value": 24.5, "unit": "°C" },
                "relative_humidity": { "value": 65.0, "unit": "%" },
                "soil_moisture": { "value": 72.0, "unit": "%" },
                "soil_ph": { "value": 6.4, "unit": "pH" },
                "light_intensity": { "value": 35000, "unit": "lux" },
                "nitrogen": { "value": 175.0, "unit": "mg/kg" },
                "phosphorus": { "value": 22.0, "unit": "mg/kg" },
                "potassium": { "value": 180.0, "unit": "mg/kg" }
              }
            }
            ```

            #### Alternative Protocols & Adaptation Guide
            - **HTTP POST (Push Architecture)**: If microcontrollers sleep to conserve battery and push data when waking, deploy a lightweight FastAPI or Flask webhook server in the network. The webhook receives `POST /telemetry`, validates the payload using `HttpSensorReceiver.validate_payload()`, and caches the latest readings in memory or Redis for Streamlit to consume.
            - **MQTT Broker (Publish/Subscribe)**: For distributed field deployments, microcontrollers publish to topics like `sensors/{device_id}/telemetry`. A background daemon subscribes to the broker using `paho-mqtt`, unpacks the JSON payload, and writes to the local state buffer.
            """
        )


if __name__ == "__main__":
    main()
