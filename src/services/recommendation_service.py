"""Recommendation service providing agronomic guidance based on comparison results."""
from typing import Dict, Any, List
from src.models import ComparisonResult, ComparisonStatus


class RecommendationService:
    """Generates stage-aware agronomic recommendations and corrective actions."""

    @staticmethod
    def get_recommendation(result: ComparisonResult) -> Dict[str, Any]:
        """Generate specific guidance for a given comparison result."""
        status = result.status
        crop_id = result.crop_id.lower()
        stage_id = result.stage_id.lower()
        param_id = result.parameter_id.lower()

        if status == ComparisonStatus.INVALID_MEASUREMENT:
            return {
                "action": "Check Input or Sensor Calibration",
                "severity": "warning",
                "guidance": (
                    f"The measurement was rejected as invalid. {result.explanation}. "
                    "Please verify the measurement value, sensor wiring, and unit compatibility."
                ),
            }

        if status == ComparisonStatus.REFERENCE_UNAVAILABLE:
            return {
                "action": "Consult Local Agronomic Extension",
                "severity": "info",
                "guidance": (
                    f"No verified operational range is established for {result.parameter_name} "
                    f"at this stage ({result.stage_name}). {result.explanation}. "
                    "Do not attempt automated classification; consult ICAR/TNAU/State Agricultural Extension specialists."
                ),
            }

        if status == ComparisonStatus.WITHIN_RANGE:
            return {
                "action": "Maintain Current Management Practice",
                "severity": "success",
                "guidance": (
                    f"Optimal conditions detected. {result.parameter_name} is within the scientific reference "
                    f"bracket [{result.reference_min} - {result.reference_max} {result.reference_unit}] for "
                    f"{result.crop_name} during {result.stage_name}. Continue routine monitoring."
                ),
            }

        # Handle BELOW_RANGE
        if status == ComparisonStatus.BELOW_RANGE:
            if param_id == "soil_moisture":
                if stage_id in ["flowering_reproductive", "fruit_grain_pod_development"]:
                    return {
                        "action": "Immediate Irrigation Required (Critical Reproductive Window)",
                        "severity": "danger",
                        "guidance": (
                            f"URGENT: {result.crop_name} is in its moisture-sensitive {result.stage_name} phase. "
                            f"Soil moisture at {result.normalized_value}% is below minimum {result.reference_min}%. "
                            "Water deficit now can cause irreversible flower abortion, silking delay, or poor pod filling. "
                            "Initiate targeted irrigation immediately."
                        ),
                    }
                return {
                    "action": "Schedule Supplemental Irrigation",
                    "severity": "warning",
                    "guidance": (
                        f"Soil moisture ({result.normalized_value}%) is below optimal {result.reference_min}%. "
                        "Apply irrigation to restore root zone field capacity."
                    ),
                }

            if param_id == "temperature":
                return {
                    "action": "Cold Protection & Thermal Moderation",
                    "severity": "warning",
                    "guidance": (
                        f"Ambient temperature ({result.normalized_value}°C) is below recommended threshold "
                        f"({result.reference_min}°C). Consider polytunnels, mulch, or light night irrigation to buffer low temperatures."
                    ),
                }

            if param_id == "relative_humidity":
                return {
                    "action": "Mitigate Dry Atmospheric Stress",
                    "severity": "warning",
                    "guidance": (
                        f"Relative humidity ({result.normalized_value}%) is below {result.reference_min}%. "
                        "Low humidity increases vapor pressure deficit (VPD) and accelerates flower drying. "
                        "Consider micro-sprinklers or windbreaks to enhance microclimate humidity."
                    ),
                }

            if param_id == "soil_ph":
                return {
                    "action": "Soil Acidity Management (Liming)",
                    "severity": "warning",
                    "guidance": (
                        f"Soil pH ({result.normalized_value}) is below optimal {result.reference_min}. "
                        "Acidic soil restricts phosphorus and cation availability. Apply agricultural lime (calcium carbonate) "
                        "or dolomite as per soil test recommendations."
                    ),
                }

            if param_id == "light_intensity":
                return {
                    "action": "Optimize Light Interception",
                    "severity": "info",
                    "guidance": (
                        f"Illuminance ({result.normalized_value} lux) is below optimal photosynthetic band ({result.reference_min} lux). "
                        "Check for excessive cloud cover, weed shading, or high-density canopy crowding."
                    ),
                }

            if param_id in ["nitrogen", "phosphorus", "potassium"]:
                nutrient_names = {"nitrogen": "Nitrogen", "phosphorus": "Phosphorus", "potassium": "Potassium"}
                return {
                    "action": f"Apply Supplemental {nutrient_names.get(param_id, param_id.title())}",
                    "severity": "warning",
                    "guidance": (
                        f"Available soil {nutrient_names.get(param_id, param_id.title())} ({result.normalized_value} {result.reference_unit}) "
                        f"is below the target threshold ({result.reference_min} {result.reference_unit}) for {result.stage_name}. "
                        "Top-dress or fertigate according to recommended split dosage schedules."
                    ),
                }

        # Handle ABOVE_RANGE
        if status == ComparisonStatus.ABOVE_RANGE:
            if param_id == "soil_moisture":
                return {
                    "action": "Withhold Irrigation & Ensure Drainage",
                    "severity": "warning",
                    "guidance": (
                        f"Soil moisture ({result.normalized_value}%) exceeds safe upper threshold ({result.reference_max}%). "
                        "Excess soil water induces hypoxia, root decay (Phytophthora/Pythium), and nutrient leaching. "
                        "Halt irrigation and inspect field drainage ditches immediately."
                    ),
                }

            if param_id == "temperature":
                if stage_id in ["flowering_reproductive"]:
                    return {
                        "action": "URGENT Heat Stress Mitigation",
                        "severity": "danger",
                        "guidance": (
                            f"CRITICAL: Canopy temperature ({result.normalized_value}°C) exceeds maximum threshold ({result.reference_max}°C) "
                            f"during {result.stage_name}. High thermal exposure desicates pollen and induces floral sterility. "
                            "Deploy shade nets, activate overhead canopy misting, or irrigate to lower canopy temperature."
                        ),
                    }
                return {
                    "action": "Heat Stress Alleviation",
                    "severity": "warning",
                    "guidance": (
                        f"Temperature ({result.normalized_value}°C) is above optimal range ({result.reference_max}°C). "
                        "Provide shade netting or enhance greenhouse ventilation."
                    ),
                }

            if param_id == "relative_humidity":
                return {
                    "action": "Aerate Canopy to Prevent Fungal Pathogens",
                    "severity": "warning",
                    "guidance": (
                        f"Relative humidity ({result.normalized_value}%) exceeds safe upper limit ({result.reference_max}%). "
                        "Persistent high humidity triggers foliar fungal outbreaks (blights, rusts, mildews) and prevents anther opening. "
                        "Improve air circulation and avoid overhead watering."
                    ),
                }

            if param_id == "soil_ph":
                return {
                    "action": "Soil Alkalinity / Salinity Management",
                    "severity": "warning",
                    "guidance": (
                        f"Soil pH ({result.normalized_value}) exceeds optimal range ({result.reference_max}). "
                        "Alkaline conditions fix phosphorus, iron, and zinc into insoluble forms. Apply agricultural gypsum "
                        "or elemental sulfur to lower pH and leach excess sodium."
                    ),
                }

            if param_id == "light_intensity":
                return {
                    "action": "Deploy Shade Protection",
                    "severity": "info",
                    "guidance": (
                        f"Solar radiation ({result.normalized_value} lux) exceeds light saturation threshold ({result.reference_max} lux). "
                        "Risk of photoinhibition, leaf scorch, or sunscald on developing fruits. Use 30-50% agro-shade nets."
                    ),
                }

            if param_id in ["nitrogen", "phosphorus", "potassium"]:
                nutrient_names = {"nitrogen": "Nitrogen", "phosphorus": "Phosphorus", "potassium": "Potassium"}
                return {
                    "action": f"Withhold Further {nutrient_names.get(param_id, param_id.title())} Additions",
                    "severity": "warning",
                    "guidance": (
                        f"Soil {nutrient_names.get(param_id, param_id.title())} ({result.normalized_value} {result.reference_unit}) "
                        f"exceeds optimal bounds ({result.reference_max} {result.reference_unit}). "
                        "Excess nitrogen delays flowering and promotes insect infestation; excess potassium blocks magnesium absorption. "
                        "Do not apply additional fertilizers until levels normalize."
                    ),
                }

        return {
            "action": "Evaluate Observation",
            "severity": "info",
            "guidance": result.explanation,
        }
