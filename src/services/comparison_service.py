"""Shared comparison engine for evaluating measurements against agronomic reference ranges."""
import math
from typing import Dict, List, Optional, Tuple, Any

from src.config import CROPS, GROWTH_STAGES, PARAMETERS, CATEGORIES
from src.models import (
    ComparisonStatus,
    ComparisonResult,
    MeasurementSource,
    ReferenceRangeRecord,
)
from src.data.dataset_loader import DatasetLoader


class UnitConversionHelper:
    """Handles unit compatibility validation and standard normalization."""

    @staticmethod
    def normalize(parameter_id: str, value: float, unit: str) -> Tuple[bool, Optional[float], str, Optional[str]]:
        """
        Validate unit and normalize value to parameter standard unit.
        Returns: (is_compatible, normalized_value, standard_unit, error_message)
        """
        param_cfg = PARAMETERS.get(parameter_id.lower())
        if not param_cfg:
            return False, None, unit, f"Unknown parameter identifier: '{parameter_id}'"

        standard_unit = param_cfg["standard_unit"]
        compatible_units = [u.lower() for u in param_cfg["compatible_units"]]
        norm_unit = unit.strip()

        if norm_unit.lower() not in compatible_units:
            return (
                False,
                None,
                standard_unit,
                f"Incompatible unit '{unit}' for {param_cfg['name']}. Expected one of: {param_cfg['compatible_units']}"
            )

        u = norm_unit.lower()

        # Temperature conversions
        if parameter_id == "temperature":
            if u in ["°f", "f"]:
                # Convert Fahrenheit to Celsius
                converted = (value - 32.0) * 5.0 / 9.0
                return True, round(converted, 2), standard_unit, None
            return True, round(value, 2), standard_unit, None

        # Light Intensity conversions
        if parameter_id == "light_intensity":
            if u == "klux":
                # Convert klux to lux
                converted = value * 1000.0
                return True, round(converted, 1), standard_unit, None
            return True, round(value, 1), standard_unit, None

        # NPK conversions
        if parameter_id in ["nitrogen", "phosphorus", "potassium"]:
            if u == "ppm":
                # In standard soil test reports, 1 ppm = 1 mg/kg
                return True, round(value, 2), standard_unit, None
            if u == "kg/ha":
                # Approximate Indian standard conversion: 1 mg/kg = 2 kg/ha (assuming 2 million kg soil in 0-15cm furrow slice)
                converted = value / 2.0
                return True, round(converted, 2), standard_unit, None
            return True, round(value, 2), standard_unit, None

        # Standard direct value
        return True, round(value, 2), standard_unit, None


class ComparisonService:
    """Core comparison engine comparing field measurements against verified agronomic records."""

    def __init__(self, dataset_loader: Optional[DatasetLoader] = None):
        self.dataset_loader = dataset_loader or DatasetLoader()

    def _validate_physical_boundaries(self, parameter_id: str, value: float) -> Optional[str]:
        """Verify that the measurement falls within physically possible limits."""
        if math.isnan(value) or math.isinf(value):
            return "Measurement value is not a finite number"

        if parameter_id == "relative_humidity" and not (0.0 <= value <= 100.0):
            return f"Relative humidity must be between 0% and 100% (got {value}%)"

        if parameter_id == "soil_moisture" and not (0.0 <= value <= 100.0):
            return f"Soil moisture percentage must be between 0% and 100% (got {value}%)"

        if parameter_id == "soil_ph" and not (0.0 <= value <= 14.0):
            return f"Soil pH must be on the standard scale between 0.0 and 14.0 (got {value})"

        if parameter_id == "light_intensity" and value < 0.0:
            return f"Light intensity cannot be negative (got {value} lux)"

        if parameter_id in ["nitrogen", "phosphorus", "potassium"] and value < 0.0:
            return f"Soil nutrient concentration cannot be negative (got {value})"

        if parameter_id == "temperature" and (value < -50.0 or value > 80.0):
            return f"Temperature reading {value}°C is outside plausible terrestrial agricultural limits"

        return None

    def compare_single(
        self,
        crop_id: str,
        stage_id: str,
        category_id: str,
        parameter_id: str,
        raw_value: Any,
        unit: str,
        source: str = MeasurementSource.MANUAL.value,
        timestamp: Optional[str] = None,
    ) -> ComparisonResult:
        """
        Evaluate a single measurement against the corresponding crop-stage reference range.
        Returns a rich ComparisonResult.
        """
        crop_info = CROPS.get(crop_id.lower(), {"id": crop_id, "name": crop_id.title()})
        stage_info = GROWTH_STAGES.get(stage_id.lower(), {"id": stage_id, "name": stage_id.replace("_", " ").title()})
        category_info = CATEGORIES.get(category_id.lower(), {"id": category_id, "name": category_id.title()})
        param_info = PARAMETERS.get(parameter_id.lower(), {"id": parameter_id, "name": parameter_id.replace("_", " ").title(), "standard_unit": unit})

        record = self.dataset_loader.get_record(crop_id, stage_id, parameter_id)

        # 1. Parse numeric value
        try:
            if raw_value is None or str(raw_value).strip() == "":
                return ComparisonResult(
                    crop_id=crop_id,
                    crop_name=crop_info["name"],
                    stage_id=stage_id,
                    stage_name=stage_info["name"],
                    category_id=category_id,
                    category_name=category_info["name"],
                    parameter_id=parameter_id,
                    parameter_name=param_info["name"],
                    source=source,
                    raw_value=raw_value,
                    normalized_value=None,
                    measured_unit=unit,
                    reference_min=record.min_value if record else None,
                    reference_max=record.max_value if record else None,
                    reference_unit=record.unit if record else param_info.get("standard_unit"),
                    status=ComparisonStatus.INVALID_MEASUREMENT,
                    source_title=record.source_title if record else None,
                    source_url=record.source_url if record else None,
                    explanation="Measurement value is empty or missing.",
                    is_verified=False,
                )
            numeric_val = float(raw_value)
        except (ValueError, TypeError):
            return ComparisonResult(
                crop_id=crop_id,
                crop_name=crop_info["name"],
                stage_id=stage_id,
                stage_name=stage_info["name"],
                category_id=category_id,
                category_name=category_info["name"],
                parameter_id=parameter_id,
                parameter_name=param_info["name"],
                source=source,
                raw_value=raw_value,
                normalized_value=None,
                measured_unit=unit,
                reference_min=record.min_value if record else None,
                reference_max=record.max_value if record else None,
                reference_unit=record.unit if record else param_info.get("standard_unit"),
                status=ComparisonStatus.INVALID_MEASUREMENT,
                source_title=record.source_title if record else None,
                source_url=record.source_url if record else None,
                explanation=f"Cannot parse '{raw_value}' as a valid numeric measurement.",
                is_verified=False,
            )

        # 2. Check Unit compatibility and normalize
        is_comp, norm_val, std_unit, unit_err = UnitConversionHelper.normalize(parameter_id, numeric_val, unit)
        if not is_comp or norm_val is None:
            return ComparisonResult(
                crop_id=crop_id,
                crop_name=crop_info["name"],
                stage_id=stage_id,
                stage_name=stage_info["name"],
                category_id=category_id,
                category_name=category_info["name"],
                parameter_id=parameter_id,
                parameter_name=param_info["name"],
                source=source,
                raw_value=raw_value,
                normalized_value=None,
                measured_unit=unit,
                reference_min=record.min_value if record else None,
                reference_max=record.max_value if record else None,
                reference_unit=record.unit if record else std_unit,
                status=ComparisonStatus.INVALID_MEASUREMENT,
                source_title=record.source_title if record else None,
                source_url=record.source_url if record else None,
                explanation=unit_err or "Incompatible unit supplied.",
                is_verified=False,
            )

        # 3. Check Physical bounds
        bound_err = self._validate_physical_boundaries(parameter_id, norm_val)
        if bound_err:
            return ComparisonResult(
                crop_id=crop_id,
                crop_name=crop_info["name"],
                stage_id=stage_id,
                stage_name=stage_info["name"],
                category_id=category_id,
                category_name=category_info["name"],
                parameter_id=parameter_id,
                parameter_name=param_info["name"],
                source=source,
                raw_value=raw_value,
                normalized_value=norm_val,
                measured_unit=unit,
                reference_min=record.min_value if record else None,
                reference_max=record.max_value if record else None,
                reference_unit=record.unit if record else std_unit,
                status=ComparisonStatus.INVALID_MEASUREMENT,
                source_title=record.source_title if record else None,
                source_url=record.source_url if record else None,
                explanation=f"Physical sanity check failed: {bound_err}",
                is_verified=False,
            )

        # 4. Check Reference Record availability and validation status
        if not record or not record.is_verified():
            unverified_reason = record.notes if record else "No reference record found in database"
            source_t = record.source_title if record else "Not Available"
            source_u = record.source_url if record else ""
            return ComparisonResult(
                crop_id=crop_id,
                crop_name=crop_info["name"],
                stage_id=stage_id,
                stage_name=stage_info["name"],
                category_id=category_id,
                category_name=category_info["name"],
                parameter_id=parameter_id,
                parameter_name=param_info["name"],
                source=source,
                raw_value=raw_value,
                normalized_value=norm_val,
                measured_unit=unit,
                reference_min=None,
                reference_max=None,
                reference_unit=record.unit if record else std_unit,
                status=ComparisonStatus.REFERENCE_UNAVAILABLE,
                source_title=source_t,
                source_url=source_u,
                explanation=f"Reference data is unavailable or UNVERIFIED for {crop_info['name']} during {stage_info['name']}. Rationale: {unverified_reason}",
                is_verified=False,
            )

        # 5. Core Comparison with inclusive boundaries
        min_v = record.min_value
        max_v = record.max_value

        unit_str = record.unit
        norm_str = f"{norm_val} {unit_str}"
        if unit.strip().lower() != unit_str.strip().lower():
            norm_str += f" (converted from {raw_value} {unit})"

        if norm_val < min_v:
            status = ComparisonStatus.BELOW_RANGE
            explanation = (
                f"Measured {param_info['name']} ({norm_str}) is BELOW the recommended range "
                f"[{min_v} - {max_v} {unit_str}] for {crop_info['name']} at {stage_info['name']}."
            )
        elif norm_val > max_v:
            status = ComparisonStatus.ABOVE_RANGE
            explanation = (
                f"Measured {param_info['name']} ({norm_str}) is ABOVE the recommended range "
                f"[{min_v} - {max_v} {unit_str}] for {crop_info['name']} at {stage_info['name']}."
            )
        else:
            status = ComparisonStatus.WITHIN_RANGE
            explanation = (
                f"Measured {param_info['name']} ({norm_str}) is WITHIN the optimal reference range "
                f"[{min_v} - {max_v} {unit_str}] for {crop_info['name']} at {stage_info['name']}."
            )

        return ComparisonResult(
            crop_id=crop_id,
            crop_name=crop_info["name"],
            stage_id=stage_id,
            stage_name=stage_info["name"],
            category_id=category_id,
            category_name=category_info["name"],
            parameter_id=parameter_id,
            parameter_name=param_info["name"],
            source=source,
            raw_value=raw_value,
            normalized_value=norm_val,
            measured_unit=unit,
            reference_min=min_v,
            reference_max=max_v,
            reference_unit=unit_str,
            status=status,
            source_title=record.source_title,
            source_url=record.source_url,
            explanation=explanation,
            is_verified=True,
        )

    def compare_category(
        self,
        crop_id: str,
        stage_id: str,
        category_id: str,
        measurements: Dict[str, Tuple[Any, str]],
        source: str = MeasurementSource.MANUAL.value,
        timestamp: Optional[str] = None,
    ) -> List[ComparisonResult]:
        """
        Evaluate all measurements for a category.
        For single-parameter categories: returns a list of 1 result.
        For NPK: evaluates Nitrogen, Phosphorus, Potassium independently and returns 3 results.
        """
        category_cfg = CATEGORIES.get(category_id.lower())
        if not category_cfg:
            raise ValueError(f"Unknown measurement category: {category_id}")

        results: List[ComparisonResult] = []
        for param_id in category_cfg["parameter_ids"]:
            if param_id in measurements:
                val, u = measurements[param_id]
                res = self.compare_single(
                    crop_id=crop_id,
                    stage_id=stage_id,
                    category_id=category_id,
                    parameter_id=param_id,
                    raw_value=val,
                    unit=u,
                    source=source,
                    timestamp=timestamp,
                )
            else:
                # Parameter was not supplied
                res = self.compare_single(
                    crop_id=crop_id,
                    stage_id=stage_id,
                    category_id=category_id,
                    parameter_id=param_id,
                    raw_value=None,
                    unit=PARAMETERS[param_id]["standard_unit"],
                    source=source,
                    timestamp=timestamp,
                )
            results.append(res)

        return results
