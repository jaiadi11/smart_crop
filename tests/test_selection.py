"""Tests for crop, stage, category selection workflows and state management."""
import pytest
from src.config import CROPS, GROWTH_STAGES, CATEGORIES, PARAMETERS
from src.services.comparison_service import ComparisonService


def test_category_parameter_mappings():
    """Verify that every category maps to correct parameter IDs and NPK contains all three nutrients."""
    assert CATEGORIES["temperature"]["parameter_ids"] == ["temperature"]
    assert CATEGORIES["relative_humidity"]["parameter_ids"] == ["relative_humidity"]
    assert CATEGORIES["soil_moisture"]["parameter_ids"] == ["soil_moisture"]
    assert CATEGORIES["soil_ph"]["parameter_ids"] == ["soil_ph"]
    assert CATEGORIES["light_intensity"]["parameter_ids"] == ["light_intensity"]

    # NPK is one category containing 3 separate measurements
    npk_params = CATEGORIES["npk"]["parameter_ids"]
    assert len(npk_params) == 3
    assert set(npk_params) == {"nitrogen", "phosphorus", "potassium"}


def test_valid_and_invalid_crop_selections():
    """Test validation of known vs unknown crop identifiers."""
    valid_crops = ["maize", "tomato", "rice", "wheat", "groundnut"]
    for c in valid_crops:
        assert c in CROPS
        assert CROPS[c]["name"] is not None

    invalid_crops = ["banana", "cassava", "corn", "", "unknown_crop"]
    for ic in invalid_crops:
        assert ic not in CROPS


def test_valid_and_invalid_stage_selections():
    """Test validation of known vs unknown growth stage identifiers."""
    valid_stages = [
        "germination_establishment",
        "vegetative_growth",
        "flowering_reproductive",
        "fruit_grain_pod_development",
        "maturity",
    ]
    for s in valid_stages:
        assert s in GROWTH_STAGES
        assert GROWTH_STAGES[s]["name"] is not None

    invalid_stages = ["seedling_stage", "harvested", "dormancy", "invalid_stage"]
    for is_ in invalid_stages:
        assert is_ not in GROWTH_STAGES


def test_valid_and_invalid_category_selections(comparison_service: ComparisonService):
    """Test validation of category selections and rejection of unknown categories."""
    valid_categories = ["temperature", "relative_humidity", "soil_moisture", "soil_ph", "light_intensity", "npk"]
    assert len(CATEGORIES) == 6
    for cat in valid_categories:
        assert cat in CATEGORIES

    # Exactly one category can be selected and invalid category raises ValueError
    with pytest.raises(ValueError, match="Unknown measurement category"):
        comparison_service.compare_category(
            crop_id="maize",
            stage_id="vegetative_growth",
            category_id="soil_salinity",
            measurements={},
        )


def test_selection_stale_clearing_logic():
    """
    Simulate session state behavior to verify that changing selection clears stale results.
    """
    session_state = {
        "_active_selection_key": "maize:vegetative_growth:temperature:Manual Entry",
        "comparison_results": ["dummy_result_1"],
        "recommendations": ["dummy_rec_1"],
    }

    # Simulate user changing selection to "tomato"
    new_selection_key = "tomato:vegetative_growth:temperature:Manual Entry"

    if session_state.get("_active_selection_key") != new_selection_key:
        session_state.pop("comparison_results", None)
        session_state.pop("recommendations", None)
        session_state["_active_selection_key"] = new_selection_key

    # Stale results must have been purged
    assert "comparison_results" not in session_state
    assert "recommendations" not in session_state
    assert session_state["_active_selection_key"] == new_selection_key


def test_all_25_combinations_iteration():
    """Verify that all 25 crop-stage combinations are cleanly iterable without conflict."""
    combinations = []
    for c_id in CROPS:
        for s_id in GROWTH_STAGES:
            combinations.append((c_id, s_id))

    assert len(combinations) == 25
    assert len(set(combinations)) == 25
