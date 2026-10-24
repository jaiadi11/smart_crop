"""UI Selectors for Crop, Growth Stage, Category, and Measurement Mode."""
import streamlit as st
from typing import Tuple, Dict, Any

from src.config import CROPS, GROWTH_STAGES, CATEGORIES


def render_selectors() -> Tuple[str, str, str, str]:
    """
    Render crop, stage, category, and source selection controls.
    Automatically detects selection changes and clears stale results.
    Returns: (crop_id, stage_id, category_id, measurement_mode)
    """
    st.sidebar.header("🌱 Advisory Selection")

    # 1. Crop Selection
    crop_options = list(CROPS.keys())
    crop_names = [CROPS[c]["name"] for c in crop_options]
    selected_crop_idx = st.sidebar.selectbox(
        "1. Select Crop",
        range(len(crop_options)),
        format_func=lambda i: crop_names[i],
        key="selector_crop_idx",
    )
    crop_id = crop_options[selected_crop_idx]

    # 2. Growth Stage Selection
    stage_options = list(GROWTH_STAGES.keys())
    stage_names = [GROWTH_STAGES[s]["name"] for s in stage_options]
    selected_stage_idx = st.sidebar.selectbox(
        "2. Select Growth Stage",
        range(len(stage_options)),
        format_func=lambda i: stage_names[i],
        key="selector_stage_idx",
    )
    stage_id = stage_options[selected_stage_idx]

    # 3. Parameter Category Selection (NPK is ONE category)
    category_options = list(CATEGORIES.keys())
    category_names = [CATEGORIES[c]["name"] for c in category_options]
    selected_category_idx = st.sidebar.selectbox(
        "3. Select Measurement Category",
        range(len(category_options)),
        format_func=lambda i: category_names[i],
        key="selector_category_idx",
    )
    category_id = category_options[selected_category_idx]

    # 4. Measurement Source Selection
    mode_options = ["Manual Entry", "Live Sensor (Wi-Fi)", "Mock Sensor (Simulation)"]
    selected_mode = st.sidebar.radio(
        "4. Select Measurement Source",
        mode_options,
        key="selector_source_mode",
    )

    # Stale Result Clearing Logic
    current_selection_key = f"{crop_id}:{stage_id}:{category_id}:{selected_mode}"
    previous_selection_key = st.session_state.get("_active_selection_key", None)

    if previous_selection_key is not None and previous_selection_key != current_selection_key:
        # User changed a selection; clear previous comparison results
        st.session_state.pop("comparison_results", None)
        st.session_state.pop("recommendations", None)
        st.session_state.pop("sensor_payload", None)
        st.session_state.pop("sensor_error", None)

    st.session_state["_active_selection_key"] = current_selection_key

    # Reset / New Measurement Action
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Reset / New Measurement", use_container_width=True, key="btn_sidebar_reset"):
        st.session_state.pop("comparison_results", None)
        st.session_state.pop("recommendations", None)
        st.session_state.pop("sensor_payload", None)
        st.session_state.pop("sensor_error", None)
        st.rerun()

    # Display Crop/Stage info summary in sidebar
    st.sidebar.caption(f"**Scientific Name:** *{CROPS[crop_id].get('scientific_name', '')}*")
    st.sidebar.caption(f"**Stage Focus:** {GROWTH_STAGES[stage_id].get('description', '')}")

    return crop_id, stage_id, category_id, selected_mode

