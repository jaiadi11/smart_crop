"""Tests for comparison engine boundaries, statuses, and unit conversions."""
import pytest
from src.models import ComparisonStatus
from src.services.comparison_service import ComparisonService
from src.data.dataset_loader import DatasetLoader


def test_comparison_below_range(comparison_service: ComparisonService):
    """Test value strictly below the validated minimum."""
    # Maize vegetative temperature is [21.0, 32.0] °C
    res = comparison_service.compare_single(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="temperature",
        parameter_id="temperature",
        raw_value=18.0,
        unit="°C",
    )
    assert res.status == ComparisonStatus.BELOW_RANGE
    assert "BELOW the recommended range" in res.explanation
    assert res.reference_min == 21.0
    assert res.reference_max == 32.0


def test_comparison_within_range(comparison_service: ComparisonService):
    """Test midpoint value strictly within the validated range."""
    # Maize vegetative temperature is [21.0, 32.0] °C
    res = comparison_service.compare_single(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="temperature",
        parameter_id="temperature",
        raw_value=26.5,
        unit="°C",
    )
    assert res.status == ComparisonStatus.WITHIN_RANGE
    assert "WITHIN the optimal reference range" in res.explanation


def test_comparison_above_range(comparison_service: ComparisonService):
    """Test value strictly above the validated maximum."""
    # Maize vegetative temperature is [21.0, 32.0] °C
    res = comparison_service.compare_single(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="temperature",
        parameter_id="temperature",
        raw_value=35.0,
        unit="°C",
    )
    assert res.status == ComparisonStatus.ABOVE_RANGE
    assert "ABOVE the recommended range" in res.explanation


def test_inclusive_boundaries(comparison_service: ComparisonService, dataset_loader: DatasetLoader):
    """Verify inclusive boundary handling: x == min and x == max must both evaluate to WITHIN RANGE."""
    rec = dataset_loader.get_record("maize", "vegetative_growth", "temperature")
    assert rec is not None and rec.is_verified()

    # Exact minimum boundary
    res_min = comparison_service.compare_single(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="temperature",
        parameter_id="temperature",
        raw_value=rec.min_value,
        unit="°C",
    )
    assert res_min.status == ComparisonStatus.WITHIN_RANGE

    # Exact maximum boundary
    res_max = comparison_service.compare_single(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="temperature",
        parameter_id="temperature",
        raw_value=rec.max_value,
        unit="°C",
    )
    assert res_max.status == ComparisonStatus.WITHIN_RANGE


def test_unverified_range_returns_reference_unavailable(comparison_service: ComparisonService):
    """Verify that unverified records return REFERENCE UNAVAILABLE without guessing status."""
    # Maize germination light intensity is UNVERIFIED
    res = comparison_service.compare_single(
        crop_id="maize",
        stage_id="germination_establishment",
        category_id="light_intensity",
        parameter_id="light_intensity",
        raw_value=30000.0,
        unit="lux",
    )
    assert res.status == ComparisonStatus.REFERENCE_UNAVAILABLE
    assert "Reference data is unavailable or UNVERIFIED" in res.explanation
    assert res.reference_min is None
    assert res.reference_max is None


def test_incompatible_unit_rejection(comparison_service: ComparisonService):
    """Verify that incompatible units are rejected with INVALID MEASUREMENT."""
    res = comparison_service.compare_single(
        crop_id="tomato",
        stage_id="vegetative_growth",
        category_id="temperature",
        parameter_id="temperature",
        raw_value=25.0,
        unit="lux",  # lux is incompatible with temperature
    )
    assert res.status == ComparisonStatus.INVALID_MEASUREMENT
    assert "Incompatible unit" in res.explanation


def test_physical_limits_validation(comparison_service: ComparisonService):
    """Verify that physically impossible measurements return INVALID MEASUREMENT."""
    # Negative humidity
    res_neg_rh = comparison_service.compare_single(
        crop_id="tomato",
        stage_id="vegetative_growth",
        category_id="relative_humidity",
        parameter_id="relative_humidity",
        raw_value=-5.0,
        unit="%",
    )
    assert res_neg_rh.status == ComparisonStatus.INVALID_MEASUREMENT

    # Soil pH > 14
    res_ph = comparison_service.compare_single(
        crop_id="tomato",
        stage_id="vegetative_growth",
        category_id="soil_ph",
        parameter_id="soil_ph",
        raw_value=16.0,
        unit="pH",
    )
    assert res_ph.status == ComparisonStatus.INVALID_MEASUREMENT


def test_unit_conversion_fahrenheit_to_celsius(comparison_service: ComparisonService):
    """Test Fahrenheit conversion: 77°F = 25°C which is within [21, 32]°C."""
    res = comparison_service.compare_single(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="temperature",
        parameter_id="temperature",
        raw_value=77.0,
        unit="°F",
    )
    assert res.status == ComparisonStatus.WITHIN_RANGE
    assert res.normalized_value == 25.0
    assert res.measured_unit == "°F"
    assert res.reference_unit == "°C"


def test_unit_conversion_klux_to_lux(comparison_service: ComparisonService):
    """Test klux conversion: 35.0 klux = 35000 lux."""
    res = comparison_service.compare_single(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="light_intensity",
        parameter_id="light_intensity",
        raw_value=35.0,
        unit="klux",
    )
    assert res.status == ComparisonStatus.WITHIN_RANGE
    assert res.normalized_value == 35000.0


def test_non_numeric_measurement_rejection(comparison_service: ComparisonService):
    """Test that malformed string values produce INVALID MEASUREMENT."""
    res = comparison_service.compare_single(
        crop_id="maize",
        stage_id="vegetative_growth",
        category_id="temperature",
        parameter_id="temperature",
        raw_value="abc",
        unit="°C",
    )
    assert res.status == ComparisonStatus.INVALID_MEASUREMENT
    assert "Cannot parse" in res.explanation
