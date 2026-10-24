"""Configuration and agronomic definitions for Smart Crop Stage Advisor."""
from pathlib import Path
from typing import Dict, List, Any

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "src" / "data"
DATABASE_FILE = DATA_DIR / "reference_ranges.json"
VALIDATION_REPORT_FILE = DATA_DIR / "validation_report.json"

# Supported Crops (exactly 5 crops)
CROPS: Dict[str, Dict[str, str]] = {
    "maize": {
        "id": "maize",
        "name": "Maize",
        "scientific_name": "Zea mays",
        "description": "Grain cereal crop sensitive to water stress at silking/tasseling.",
    },
    "tomato": {
        "id": "tomato",
        "name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "description": "Solanaceous vegetable crop requiring specific temperature and moisture for fruit set.",
    },
    "rice": {
        "id": "rice",
        "name": "Rice",
        "scientific_name": "Oryza sativa",
        "description": "Staple wetland and upland cereal crop with high humidity and moisture demands during flowering.",
    },
    "wheat": {
        "id": "wheat",
        "name": "Wheat",
        "scientific_name": "Triticum aestivum",
        "description": "Cool-season cereal grain vulnerable to terminal heat stress during grain filling.",
    },
    "groundnut": {
        "id": "groundnut",
        "name": "Groundnut",
        "scientific_name": "Arachis hypogaea",
        "description": "Legume oilseed crop requiring optimal soil moisture and friable soil for peg penetration and pod development.",
    },
}

# Supported Growth Stages (exactly 5 stages)
GROWTH_STAGES: Dict[str, Dict[str, Any]] = {
    "germination_establishment": {
        "id": "germination_establishment",
        "name": "Germination / Establishment",
        "stage_order": 1,
        "description": "Seed imbibition, radicle emergence, coleoptile/plumule appearance and early seedling establishment.",
    },
    "vegetative_growth": {
        "id": "vegetative_growth",
        "name": "Vegetative Growth",
        "stage_order": 2,
        "description": "Canopy development, tillering/branching, stem elongation and leaf area expansion.",
    },
    "flowering_reproductive": {
        "id": "flowering_reproductive",
        "name": "Flowering / Reproductive",
        "stage_order": 3,
        "description": "Anthesis, tasseling/silking, panicle heading, pollination and fertilization.",
    },
    "fruit_grain_pod_development": {
        "id": "fruit_grain_pod_development",
        "name": "Fruit / Grain / Pod Development",
        "stage_order": 4,
        "description": "Fruit sizing, grain filling (milky to dough stage), pegging and pod enlargement.",
    },
    "maturity": {
        "id": "maturity",
        "name": "Maturity",
        "stage_order": 5,
        "description": "Physiological maturity, grain hardening, senescence, ripening and pre-harvest dry-down.",
    },
}

# The 8 individual measurement parameters
PARAMETERS: Dict[str, Dict[str, Any]] = {
    "temperature": {
        "id": "temperature",
        "name": "Temperature",
        "standard_unit": "°C",
        "compatible_units": ["°C", "degC", "C", "°F", "F"],
        "category_id": "temperature",
        "is_nutrient": False,
        "description": "Ambient / canopy air temperature",
    },
    "relative_humidity": {
        "id": "relative_humidity",
        "name": "Relative Humidity",
        "standard_unit": "%",
        "compatible_units": ["%", "%RH", "percent"],
        "category_id": "relative_humidity",
        "is_nutrient": False,
        "description": "Atmospheric relative humidity percentage",
    },
    "soil_moisture": {
        "id": "soil_moisture",
        "name": "Soil Moisture",
        "standard_unit": "%",
        "compatible_units": ["%", "%VWC", "percent"],
        "category_id": "soil_moisture",
        "is_nutrient": False,
        "description": "Volumetric soil water content or percentage of field capacity in the effective root zone",
    },
    "soil_ph": {
        "id": "soil_ph",
        "name": "Soil pH",
        "standard_unit": "pH",
        "compatible_units": ["pH"],
        "category_id": "soil_ph",
        "is_nutrient": False,
        "description": "Soil reaction (acidity/alkalinity) measured in 1:2.5 or 1:1 soil-water suspension",
    },
    "light_intensity": {
        "id": "light_intensity",
        "name": "Light Intensity",
        "standard_unit": "lux",
        "compatible_units": ["lux", "lx", "klux"],
        "category_id": "light_intensity",
        "is_nutrient": False,
        "description": "Incident illuminance on canopy surface",
    },
    "nitrogen": {
        "id": "nitrogen",
        "name": "Available Nitrogen (N)",
        "standard_unit": "mg/kg",
        "compatible_units": ["mg/kg", "ppm", "kg/ha"],
        "category_id": "npk",
        "is_nutrient": True,
        "description": "Soil available nitrogen (alkaline permanganate method / nitrate-N)",
    },
    "phosphorus": {
        "id": "phosphorus",
        "name": "Available Phosphorus (P)",
        "standard_unit": "mg/kg",
        "compatible_units": ["mg/kg", "ppm", "kg/ha"],
        "category_id": "npk",
        "is_nutrient": True,
        "description": "Soil available phosphorus (Olsen / Bray extractable)",
    },
    "potassium": {
        "id": "potassium",
        "name": "Available Potassium (K)",
        "standard_unit": "mg/kg",
        "compatible_units": ["mg/kg", "ppm", "kg/ha"],
        "category_id": "npk",
        "is_nutrient": True,
        "description": "Soil available potassium (neutral normal ammonium acetate extractable)",
    },
}

# The 6 selectable measurement categories
CATEGORIES: Dict[str, Dict[str, Any]] = {
    "temperature": {
        "id": "temperature",
        "name": "Temperature",
        "parameter_ids": ["temperature"],
        "is_composite": False,
        "description": "Ambient / canopy thermal level",
    },
    "relative_humidity": {
        "id": "relative_humidity",
        "name": "Humidity",
        "parameter_ids": ["relative_humidity"],
        "is_composite": False,
        "description": "Atmospheric humidity level",
    },
    "soil_moisture": {
        "id": "soil_moisture",
        "name": "Soil Moisture",
        "parameter_ids": ["soil_moisture"],
        "is_composite": False,
        "description": "Root-zone soil moisture content",
    },
    "soil_ph": {
        "id": "soil_ph",
        "name": "pH",
        "parameter_ids": ["soil_ph"],
        "is_composite": False,
        "description": "Soil acidity / alkalinity level",
    },
    "light_intensity": {
        "id": "light_intensity",
        "name": "Light Intensity",
        "parameter_ids": ["light_intensity"],
        "is_composite": False,
        "description": "Canopy illuminance",
    },
    "npk": {
        "id": "npk",
        "name": "NPK",
        "parameter_ids": ["nitrogen", "phosphorus", "potassium"],
        "is_composite": True,
        "description": "Soil macronutrients: Nitrogen (N), Phosphorus (P), Potassium (K)",
    },
}

# Hardware Defaults & Environment Configuration
import os

DEFAULT_SENSOR_ENDPOINT = os.getenv("SENSOR_HTTP_ENDPOINT", "http://192.168.1.100:8080/sensors")
DEFAULT_SENSOR_TIMEOUT_SECONDS = float(os.getenv("SENSOR_TIMEOUT_SECONDS", "5.0"))
DEFAULT_SENSOR_POLLING_INTERVAL_SECONDS = float(os.getenv("SENSOR_POLLING_INTERVAL_SECONDS", "10.0"))
MOCK_SENSOR_ENABLED = os.getenv("MOCK_SENSOR_ENABLED", "true").lower() in ("true", "1", "yes")

# Parameter aliases for flexible microcontroller payload parsing
PARAMETER_ALIASES: Dict[str, str] = {
    "temperature": "temperature",
    "temp": "temperature",
    "t": "temperature",
    "air_temperature": "temperature",
    "relative_humidity": "relative_humidity",
    "humidity": "relative_humidity",
    "rh": "relative_humidity",
    "air_humidity": "relative_humidity",
    "soil_moisture": "soil_moisture",
    "moisture": "soil_moisture",
    "sm": "soil_moisture",
    "soil_moist": "soil_moisture",
    "soil_water_content": "soil_moisture",
    "soil_ph": "soil_ph",
    "ph": "soil_ph",
    "acidity": "soil_ph",
    "light_intensity": "light_intensity",
    "light": "light_intensity",
    "lux": "light_intensity",
    "illuminance": "light_intensity",
    "solar_radiation": "light_intensity",
    "nitrogen": "nitrogen",
    "n": "nitrogen",
    "phosphorus": "phosphorus",
    "p": "phosphorus",
    "potassium": "potassium",
    "k": "potassium",
    "npk": "npk",
}

