"""Dataset loader, validator, and provenance inspector for agronomic reference ranges."""
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from src.config import (
    CROPS,
    GROWTH_STAGES,
    PARAMETERS,
    CATEGORIES,
    DATABASE_FILE,
    VALIDATION_REPORT_FILE,
)
from src.models import ReferenceRangeRecord, ValidationStatus


class DatasetValidationError(Exception):
    """Raised when the reference dataset fails schema or integrity checks."""
    pass


class DatasetLoader:
    """Loads, validates, and indexes crop-stage reference parameter ranges."""

    def __init__(self, database_path: Optional[Path] = None):
        self.database_path = database_path or DATABASE_FILE
        self._records: Dict[str, ReferenceRangeRecord] = {}
        self._index: Dict[Tuple[str, str, str], ReferenceRangeRecord] = {}
        self._validation_report: Optional[Dict[str, Any]] = None
        self.load()

    @staticmethod
    def validate_record_dict(item: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate structure, types, and agronomic consistency of an individual record dictionary.
        Returns: (is_valid, error_message)
        """
        if not isinstance(item, dict):
            return False, "Record must be a JSON object / dictionary"

        required_fields = ["record_id", "crop_id", "stage_id", "parameter_id", "unit", "validation_status"]
        for f in required_fields:
            if f not in item or str(item[f]).strip() == "":
                return False, f"Missing or empty required field: '{f}'"

        status = item.get("validation_status")
        if status not in [ValidationStatus.VERIFIED.value, ValidationStatus.UNVERIFIED.value]:
            return False, f"Invalid validation_status: '{status}'"

        if status == ValidationStatus.VERIFIED.value:
            if item.get("min_value") is None or item.get("max_value") is None:
                return False, "Verified record cannot have null min_value or max_value"
            try:
                min_v = float(item["min_value"])
                max_v = float(item["max_value"])
            except (ValueError, TypeError):
                return False, "Verified record min_value and max_value must be numeric"
            if min_v > max_v:
                return False, f"min_value ({min_v}) cannot be strictly greater than max_value ({max_v})"
        elif status == ValidationStatus.UNVERIFIED.value:
            if item.get("min_value") is not None or item.get("max_value") is not None:
                return False, "Unverified record must have null min_value and max_value"

        return True, None

    def load(self, strict: bool = False) -> None:
        """Load dataset from JSON, reject malformed records, and build lookup indexes."""
        if not self.database_path.exists():
            raise FileNotFoundError(f"Reference database file not found at {self.database_path}")

        with open(self.database_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_records = data.get("records", [])
        self._records.clear()
        self._index.clear()
        self._rejected_records = []

        for item in raw_records:
            is_valid, err_msg = self.validate_record_dict(item)
            if not is_valid:
                self._rejected_records.append({"item": item, "error": err_msg})
                if strict:
                    raise DatasetValidationError(f"Malformed dataset record: {err_msg}")
                continue

            record = ReferenceRangeRecord.from_dict(item)
            self._records[record.record_id] = record
            key = (record.crop_id.lower(), record.stage_id.lower(), record.parameter_id.lower())
            self._index[key] = record

        # Generate report and validate completeness
        self._validation_report = self.generate_validation_report()


    def get_record(self, crop_id: str, stage_id: str, parameter_id: str) -> Optional[ReferenceRangeRecord]:
        """Fetch a specific parameter record by crop, stage, and parameter ID."""
        key = (crop_id.lower(), stage_id.lower(), parameter_id.lower())
        return self._index.get(key)

    def get_category_records(self, crop_id: str, stage_id: str, category_id: str) -> List[ReferenceRangeRecord]:
        """Fetch all parameter records belonging to a category (e.g., 3 for NPK, 1 for others)."""
        category_cfg = CATEGORIES.get(category_id.lower())
        if not category_cfg:
            return []

        param_ids = category_cfg["parameter_ids"]
        records = []
        for pid in param_ids:
            rec = self.get_record(crop_id, stage_id, pid)
            if rec:
                records.append(rec)
        return records

    def get_all_records(self) -> List[ReferenceRangeRecord]:
        """Return all 200 records."""
        return list(self._records.values())

    def generate_validation_report(self) -> Dict[str, Any]:
        """Perform rigorous integrity checks across all 25 combinations and 8 parameters."""
        expected_crops = list(CROPS.keys())
        expected_stages = list(GROWTH_STAGES.keys())
        expected_params = list(PARAMETERS.keys())

        total_expected = len(expected_crops) * len(expected_stages) * len(expected_params)
        verified_count = 0
        unverified_count = 0
        missing_records = []
        invalid_ranges = []
        missing_sources = []
        unverified_records_summary = []
        verified_records_summary = []

        # Check every combination
        for crop_id in expected_crops:
            for stage_id in expected_stages:
                for param_id in expected_params:
                    rec = self.get_record(crop_id, stage_id, param_id)
                    if not rec:
                        missing_records.append({
                            "crop_id": crop_id,
                            "stage_id": stage_id,
                            "parameter_id": param_id,
                            "error": "Record missing from database"
                        })
                        continue

                    # Source provenance check
                    if not rec.source_title or not rec.source_url:
                        missing_sources.append({
                            "record_id": rec.record_id,
                            "crop": rec.crop_name,
                            "stage": rec.stage_name,
                            "parameter": rec.parameter_name,
                            "reason": "Missing source title or URL"
                        })

                    if rec.validation_status == ValidationStatus.VERIFIED.value:
                        verified_count += 1
                        # Range validity
                        if rec.min_value is None or rec.max_value is None:
                            invalid_ranges.append({
                                "record_id": rec.record_id,
                                "reason": "Verified record has null min or max value"
                            })
                        elif rec.min_value > rec.max_value:
                            invalid_ranges.append({
                                "record_id": rec.record_id,
                                "min": rec.min_value,
                                "max": rec.max_value,
                                "reason": "min_value is strictly greater than max_value"
                            })
                        verified_records_summary.append({
                            "record_id": rec.record_id,
                            "crop": rec.crop_name,
                            "stage": rec.stage_name,
                            "parameter": rec.parameter_name,
                            "range": f"{rec.min_value} - {rec.max_value} {rec.unit}",
                            "source": rec.source_title
                        })
                    elif rec.validation_status == ValidationStatus.UNVERIFIED.value:
                        unverified_count += 1
                        # Must have null min and max
                        if rec.min_value is not None or rec.max_value is not None:
                            invalid_ranges.append({
                                "record_id": rec.record_id,
                                "min": rec.min_value,
                                "max": rec.max_value,
                                "reason": "Unverified record must have null min and max values"
                            })
                        unverified_records_summary.append({
                            "record_id": rec.record_id,
                            "crop": rec.crop_name,
                            "stage": rec.stage_name,
                            "parameter": rec.parameter_name,
                            "reason": rec.notes,
                            "gap_standard": rec.source_title
                        })
                    else:
                        invalid_ranges.append({
                            "record_id": rec.record_id,
                            "status": rec.validation_status,
                            "reason": f"Unknown validation status: {rec.validation_status}"
                        })

        is_valid = (
            len(missing_records) == 0
            and len(invalid_ranges) == 0
            and len(missing_sources) == 0
            and (verified_count + unverified_count == total_expected)
        )

        report = {
            "is_valid": is_valid,
            "total_expected_records": total_expected,
            "total_actual_records": len(self._records),
            "total_crops": len(expected_crops),
            "total_growth_stages": len(expected_stages),
            "total_combinations": len(expected_crops) * len(expected_stages),
            "total_parameters_per_combination": len(expected_params),
            "verified_count": verified_count,
            "unverified_count": unverified_count,
            "missing_records_count": len(missing_records),
            "invalid_ranges_count": len(invalid_ranges),
            "missing_sources_count": len(missing_sources),
            "missing_records": missing_records,
            "invalid_ranges": invalid_ranges,
            "missing_sources": missing_sources,
            "unverified_records": unverified_records_summary,
            "database_file": str(self.database_path),
        }

        # Save to disk
        try:
            VALIDATION_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(VALIDATION_REPORT_FILE, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
        except Exception:
            pass

        return report

    @property
    def validation_report(self) -> Dict[str, Any]:
        if not self._validation_report:
            self._validation_report = self.generate_validation_report()
        return self._validation_report
