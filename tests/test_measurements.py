"""Tests for measurement processing, NPK composite evaluations, and recommendations."""
import math
import pytest
from src.models import ComparisonStatus, MeasurementSource
from src.services.measurement_service import MeasurementService


def test_npk_independent_evaluations(measurement_service: MeasurementService):
    """
    Verify that NPK produces THREE distinct comparisons evaluated independently:
    e.g. Nitrogen below range, Phosphorus within range, Potassium above range.
    """
    inputs = {
        "nitrogen": (140.0, "mg/kg"),    # strictly below (140 < 180)
        "phosphorus": (20.0, "mg/kg"),   # within (15 <= 20 <= 28)
        "potassium": (300.0, "mg/kg"),   # strictly above (300 > 250)
    }

    results, recommendations = measurement_service.process_manual_entry(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="npk",
        inputs=inputs,
    )

    assert len(results) == 3
    assert len(recommendations) == 3

    # Check Nitrogen
    n_res = next(r for r in results if r.parameter_id == "nitrogen")
    assert n_res.status == ComparisonStatus.BELOW_RANGE
    assert n_res.normalized_value == 140.0

    # Check Phosphorus
    p_res = next(r for r in results if r.parameter_id == "phosphorus")
    assert p_res.status == ComparisonStatus.WITHIN_RANGE
    assert p_res.normalized_value == 20.0

    # Check Potassium
    k_res = next(r for r in results if r.parameter_id == "potassium")
    assert k_res.status == ComparisonStatus.ABOVE_RANGE
    assert k_res.normalized_value == 300.0


def test_npk_requires_all_three_nutrients(measurement_service: MeasurementService):
    """
    Verify that NPK requires all three nutrient values.
    If potassium is omitted or None, it must be flagged as INVALID_MEASUREMENT.
    """
    incomplete_inputs = {
        "nitrogen": (180.0, "mg/kg"),
        "phosphorus": (22.0, "mg/kg"),
        # Potassium is omitted
    }

    results, recommendations = measurement_service.process_manual_entry(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="npk",
        inputs=incomplete_inputs,
    )

    assert len(results) == 3
    k_res = next(r for r in results if r.parameter_id == "potassium")
    assert k_res.status == ComparisonStatus.INVALID_MEASUREMENT
    assert "empty or missing" in k_res.explanation


def test_manual_value_validation_missing_and_invalid_numbers(measurement_service: MeasurementService):
    """Verify handling of missing strings, empty inputs, non-numeric strings, and NaN."""
    # Empty string
    results, _ = measurement_service.process_manual_entry(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="temperature",
        inputs={"temperature": ("", "°C")},
    )
    assert results[0].status == ComparisonStatus.INVALID_MEASUREMENT
    assert "empty or missing" in results[0].explanation

    # Non-numeric text
    results, _ = measurement_service.process_manual_entry(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="temperature",
        inputs={"temperature": ("invalid_num", "°C")},
    )
    assert results[0].status == ComparisonStatus.INVALID_MEASUREMENT
    assert "Cannot parse" in results[0].explanation

    # NaN / Inf
    results, _ = measurement_service.process_manual_entry(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="temperature",
        inputs={"temperature": (float("nan"), "°C")},
    )
    assert results[0].status == ComparisonStatus.INVALID_MEASUREMENT
    assert "finite number" in results[0].explanation


def test_manual_physical_boundaries_validation(measurement_service: MeasurementService):
    """Verify physical sanity checks on percentage (0-100), pH (0-14), and light (>=0)."""
    # Relative humidity > 100%
    results, _ = measurement_service.process_manual_entry(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="relative_humidity",
        inputs={"relative_humidity": (120.0, "%")},
    )
    assert results[0].status == ComparisonStatus.INVALID_MEASUREMENT
    assert "between 0% and 100%" in results[0].explanation

    # Soil moisture < 0%
    results, _ = measurement_service.process_manual_entry(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="soil_moisture",
        inputs={"soil_moisture": (-5.0, "%")},
    )
    assert results[0].status == ComparisonStatus.INVALID_MEASUREMENT
    assert "between 0% and 100%" in results[0].explanation

    # pH < 0 or > 14
    results, _ = measurement_service.process_manual_entry(
        crop_id="tomato",
        stage_id="vegetative_growth",
        category_id="soil_ph",
        inputs={"soil_ph": (14.5, "pH")},
    )
    assert results[0].status == ComparisonStatus.INVALID_MEASUREMENT
    assert "between 0.0 and 14.0" in results[0].explanation

    # Negative Light
    results, _ = measurement_service.process_manual_entry(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="light_intensity",
        inputs={"light_intensity": (-500.0, "lux")},
    )
    assert results[0].status == ComparisonStatus.INVALID_MEASUREMENT
    assert "cannot be negative" in results[0].explanation


def test_manual_unit_validation_incompatible(measurement_service: MeasurementService):
    """Verify that incompatible units are rejected without silent corruption."""
    results, _ = measurement_service.process_manual_entry(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="temperature",
        inputs={"temperature": (25.0, "psi")},
    )
    assert results[0].status == ComparisonStatus.INVALID_MEASUREMENT
    assert "Incompatible unit" in results[0].explanation


def test_single_parameter_manual_evaluation(measurement_service: MeasurementService):
    """Test standard single parameter manual measurement flow."""
    inputs = {
        "soil_moisture": (75.0, "%")
    }

    results, recommendations = measurement_service.process_manual_entry(
        crop_id="rice",
        stage_id="fruit_grain_pod_development",
        category_id="soil_moisture",
        inputs=inputs,
    )

    assert len(results) == 1
    assert len(recommendations) == 1
    assert results[0].status == ComparisonStatus.WITHIN_RANGE
    assert results[0].source == MeasurementSource.MANUAL.value


def test_environmental_parameters_never_generate_fertilizer_advice(measurement_service: MeasurementService):
    """
    CRITICAL: Never generate fertilizer recommendations solely from temperature,
    humidity, or light readings. Distinguish measurement interpretation from fertilizer advice.
    """
    for param, val, unit in [
        ("temperature", 38.0, "°C"),
        ("relative_humidity", 30.0, "%"),
        ("light_intensity", 10000.0, "lux"),
    ]:
        results, recommendations = measurement_service.process_manual_entry(
            crop_id="maize",
            stage_id="vegetative_growth",
            category_id=param,
            inputs={param: (val, unit)},
        )
        rec = recommendations[0]
        rec_text = (rec["action"] + " " + rec["guidance"]).lower()
        assert "fertilizer" not in rec_text
        assert "npk" not in rec_text
        assert "nitrogen" not in rec_text
        assert "potassium" not in rec_text
        assert "phosphorus" not in rec_text


def test_recommendation_guidance_content(measurement_service: MeasurementService):
    """Verify that recommendations contain actionable agronomic steps."""
    inputs = {"soil_moisture": (45.0, "%")}
    results, recommendations = measurement_service.process_manual_entry(
        crop_id="maize",
        stage_id="flowering_reproductive",
        category_id="soil_moisture",
        inputs=inputs,
    )

    rec = recommendations[0]
    assert rec["severity"] == "danger"
    assert "Immediate Irrigation Required" in rec["action"]
    assert "URGENT" in rec["guidance"]
