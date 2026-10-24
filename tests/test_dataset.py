"""Tests for agronomic reference dataset completeness, provenance, and integrity."""
import pytest
from src.config import CROPS, GROWTH_STAGES, PARAMETERS
from src.models import ValidationStatus
from src.data.dataset_loader import DatasetLoader


def test_crops_completeness(dataset_loader: DatasetLoader):
    """Verify that all five specified crops exist."""
    expected_crops = {"maize", "tomato", "rice", "wheat", "groundnut"}
    assert set(CROPS.keys()) == expected_crops
    assert len(CROPS) == 5


def test_growth_stages_completeness(dataset_loader: DatasetLoader):
    """Verify that all five specified growth stages exist."""
    expected_stages = {
        "germination_establishment",
        "vegetative_growth",
        "flowering_reproductive",
        "fruit_grain_pod_development",
        "maturity",
    }
    assert set(GROWTH_STAGES.keys()) == expected_stages
    assert len(GROWTH_STAGES) == 5


def test_parameters_completeness(dataset_loader: DatasetLoader):
    """Verify that all eight required individual measurement parameters exist."""
    expected_params = {
        "temperature",
        "relative_humidity",
        "soil_moisture",
        "soil_ph",
        "light_intensity",
        "nitrogen",
        "phosphorus",
        "potassium",
    }
    assert set(PARAMETERS.keys()) == expected_params
    assert len(PARAMETERS) == 8


def test_total_records_count(dataset_loader: DatasetLoader):
    """Verify that exactly 200 parameter records exist across 25 crop-stage combinations."""
    all_records = dataset_loader.get_all_records()
    assert len(all_records) == 200


def test_all_25_combinations_exist(dataset_loader: DatasetLoader):
    """Verify that every one of the 25 combinations contains all 8 parameter records."""
    for crop_id in CROPS:
        for stage_id in GROWTH_STAGES:
            for param_id in PARAMETERS:
                rec = dataset_loader.get_record(crop_id, stage_id, param_id)
                assert rec is not None, f"Missing record for {crop_id}:{stage_id}:{param_id}"
                assert rec.crop_id == crop_id
                assert rec.stage_id == stage_id
                assert rec.parameter_id == param_id


def test_verified_records_integrity(dataset_loader: DatasetLoader):
    """Verify that all VERIFIED records have valid numeric min <= max and sources."""
    verified_records = [r for r in dataset_loader.get_all_records() if r.validation_status == ValidationStatus.VERIFIED.value]
    assert len(verified_records) > 0

    for rec in verified_records:
        assert rec.min_value is not None, f"Verified record {rec.record_id} has null min_value"
        assert rec.max_value is not None, f"Verified record {rec.record_id} has null max_value"
        assert rec.min_value <= rec.max_value, f"Verified record {rec.record_id} min > max ({rec.min_value} > {rec.max_value})"
        assert rec.source_title and len(rec.source_title.strip()) > 5
        assert rec.source_url and rec.source_url.startswith("http")
        assert rec.unit and len(rec.unit.strip()) > 0
        assert rec.is_verified() is True


def test_unverified_records_integrity(dataset_loader: DatasetLoader):
    """Verify that all UNVERIFIED records have min=None, max=None, and explanatory notes."""
    unverified_records = [r for r in dataset_loader.get_all_records() if r.validation_status == ValidationStatus.UNVERIFIED.value]
    assert len(unverified_records) > 0

    for rec in unverified_records:
        assert rec.min_value is None, f"Unverified record {rec.record_id} must have null min_value"
        assert rec.max_value is None, f"Unverified record {rec.record_id} must have null max_value"
        assert rec.notes and len(rec.notes.strip()) > 10, f"Unverified record {rec.record_id} must have explanation notes"
        assert rec.is_verified() is False


def test_validation_report_generation(dataset_loader: DatasetLoader):
    """Verify that the validation report confirms zero missing records and complete dataset validity."""
    report = dataset_loader.validation_report
    assert report["is_valid"] is True
    assert report["total_actual_records"] == 200
    assert report["total_expected_records"] == 200
    assert report["missing_records_count"] == 0
    assert report["invalid_ranges_count"] == 0
    assert report["missing_sources_count"] == 0
    assert report["verified_count"] + report["unverified_count"] == 200


def test_malformed_dataset_records_rejection():
    """Verify that malformed records are detected and rejected by dataset validation."""
    # 1. Missing required field
    is_v, err = DatasetLoader.validate_record_dict({
        "crop_id": "maize",
        "stage_id": "vegetative_growth",
        # missing record_id, parameter_id, etc.
    })
    assert is_v is False
    assert "Missing or empty required field" in err

    # 2. Verified record with min > max
    is_v, err = DatasetLoader.validate_record_dict({
        "record_id": "rec_01",
        "crop_id": "maize",
        "stage_id": "vegetative_growth",
        "parameter_id": "temperature",
        "unit": "°C",
        "validation_status": "VERIFIED",
        "min_value": 35.0,
        "max_value": 20.0,  # min > max
    })
    assert is_v is False
    assert "cannot be strictly greater than max_value" in err

    # 3. Verified record with null values
    is_v, err = DatasetLoader.validate_record_dict({
        "record_id": "rec_02",
        "crop_id": "maize",
        "stage_id": "vegetative_growth",
        "parameter_id": "temperature",
        "unit": "°C",
        "validation_status": "VERIFIED",
        "min_value": None,
        "max_value": 30.0,
    })
    assert is_v is False
    assert "cannot have null min_value or max_value" in err

    # 4. Unknown validation status
    is_v, err = DatasetLoader.validate_record_dict({
        "record_id": "rec_03",
        "crop_id": "maize",
        "stage_id": "vegetative_growth",
        "parameter_id": "temperature",
        "unit": "°C",
        "validation_status": "CUSTOM_STATUS",
    })
    assert is_v is False
    assert "Invalid validation_status" in err

    # 5. Non-dictionary input
    is_v, err = DatasetLoader.validate_record_dict("not_a_dict")
    assert is_v is False
    assert "must be a JSON object" in err

