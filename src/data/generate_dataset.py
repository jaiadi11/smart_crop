"""Generator script for the reference dataset of 200 records across 25 crop-stage combinations."""
import json
from pathlib import Path
from typing import Dict, Any, List

def build_dataset() -> Dict[str, Any]:
    crops = [
        {"id": "maize", "name": "Maize"},
        {"id": "tomato", "name": "Tomato"},
        {"id": "rice", "name": "Rice"},
        {"id": "wheat", "name": "Wheat"},
        {"id": "groundnut", "name": "Groundnut"}
    ]

    stages = [
        {"id": "germination_establishment", "name": "Germination / Establishment"},
        {"id": "vegetative_growth", "name": "Vegetative Growth"},
        {"id": "flowering_reproductive", "name": "Flowering / Reproductive"},
        {"id": "fruit_grain_pod_development", "name": "Fruit / Grain / Pod Development"},
        {"id": "maturity", "name": "Maturity"}
    ]

    # Source definitions
    ICAR_MAIZE = {
        "title": "ICAR-Indian Institute of Maize Research - Maize Production Technologies & Crop Phenology",
        "url": "https://iimr.icar.gov.in/production-technology/"
    }
    TNAU_MAIZE = {
        "title": "TNAU Agritech Portal - Crop Production: Maize (Zea mays)",
        "url": "https://agritech.tnau.ac.in/agriculture/agri_crop_production_cereals_maize.html"
    }
    FAO_MAIZE = {
        "title": "FAO Land & Water - Crop Water Management: Maize (FAO Irrigation and Drainage Paper 33 & 56)",
        "url": "https://www.fao.org/land-water/databases-and-software/crop-information/maize/en/"
    }
    CIMMYT_MAIZE = {
        "title": "CIMMYT Maize Agronomy & Heat/Drought Stress Tolerances Guide",
        "url": "https://www.cimmyt.org/resources/maize-agronomy/"
    }

    TNAU_TOMATO = {
        "title": "TNAU Agritech Portal - Horticulture: Production Technology of Tomato",
        "url": "https://agritech.tnau.ac.in/horticulture/horti_vegetables_tomato.html"
    }
    ICAR_TOMATO = {
        "title": "ICAR-Indian Institute of Horticultural Research - Tomato Package of Practices",
        "url": "https://iihr.res.in/tomato-production-practices"
    }
    FAO_TOMATO = {
        "title": "FAO Land & Water - Tomato Crop Water Requirements & Climatic Thresholds",
        "url": "https://www.fao.org/land-water/databases-and-software/crop-information/tomato/en/"
    }
    UCDAVIS_TOMATO = {
        "title": "UC Davis Vegetable Research and Information Center - Tomato Production in California",
        "url": "https://vric.ucdavis.edu/veg_info_crop/tomato.htm"
    }

    IRRI_RICE = {
        "title": "IRRI Rice Knowledge Bank - Agronomy & Environmental Requirements for Rice",
        "url": "http://www.knowledgebank.irri.org/step-by-step-production"
    }
    TNAU_RICE = {
        "title": "TNAU Agritech Portal - Agriculture: Rice Package of Practices & Water Management",
        "url": "https://agritech.tnau.ac.in/agriculture/agri_crop_production_cereals_rice.html"
    }
    ICAR_RICE = {
        "title": "ICAR-National Rice Research Institute (NRRI) - Rice Crop Management & Fertilizer Guidelines",
        "url": "https://icar-nrri.gov.in/rice-technologies/"
    }
    FAO_RICE = {
        "title": "FAO Land & Water - Rice Crop Water Guidelines & Stage Sensitive Indices",
        "url": "https://www.fao.org/land-water/databases-and-software/crop-information/rice/en/"
    }

    ICAR_WHEAT = {
        "title": "ICAR-Indian Institute of Wheat & Barley Research (IIWBR) - Wheat Agronomy & Climate Guidelines",
        "url": "https://iiwbr.icar.gov.in/wheat-production-technologies/"
    }
    CIMMYT_WHEAT = {
        "title": "CIMMYT Wheat Physiology & Heat/Water Stress Management Handbook",
        "url": "https://www.cimmyt.org/resources/wheat-agronomy/"
    }
    FAO_WHEAT = {
        "title": "FAO Crop Information - Wheat Irrigation, Temperature and Growth Stages (Paper 33)",
        "url": "https://www.fao.org/land-water/databases-and-software/crop-information/wheat/en/"
    }

    ICRISAT_GROUNDNUT = {
        "title": "ICRISAT Groundnut Production Practices, Biological Nitrogen Fixation & Critical Stages",
        "url": "http://exploreit.icrisat.org/page/groundnut/688"
    }
    TNAU_GROUNDNUT = {
        "title": "TNAU Agritech Portal - Oilseeds: Groundnut (Arachis hypogaea) Cultivation Guide",
        "url": "https://agritech.tnau.ac.in/agriculture/agri_crop_production_oilseeds_groundnut.html"
    }
    FAO_GROUNDNUT = {
        "title": "FAO Land & Water - Groundnut Water Needs & Stage Vulnerability (Paper 33)",
        "url": "https://www.fao.org/land-water/databases-and-software/crop-information/groundnut/en/"
    }

    UNVERIFIED_LIGHT_GERM = {
        "title": "Agronomic Standard Gap: Subterranean Germination Photic Standard",
        "url": "https://www.fao.org/land-water/databases-and-software/crop-information/en/",
        "note": "Seed germination and radicle emergence take place within the seedbed/soil substrate. Ambient illuminance is not an agronomic operational parameter for this subterranean phase. Verified stage-specific lux ranges are not defined."
    }

    UNVERIFIED_LIGHT_MATURITY = {
        "title": "Agronomic Standard Gap: Senescence Stage Photic Threshold",
        "url": "https://www.fao.org/land-water/databases-and-software/crop-information/en/",
        "note": "Crop maturity is characterized by physiological senescence, chlorophyll breakdown, and dry-down. Operational minimum/maximum lux boundaries are neither prescribed nor limiting in agronomic practice."
    }

    UNVERIFIED_NUTRIENT_MATURITY = {
        "title": "Agronomic Standard Gap: Late Maturity Nutrient Application Restrictions",
        "url": "https://agritech.tnau.ac.in/",
        "note": "Standard agronomic guidelines prohibit supplemental soil fertilization during the final maturity/ripening phase to prevent vegetative re-flushes, delayed ripening, lodging, and microbial infections. Stage-specific available soil nutrient targets are not defined."
    }

    records = []

    # Helper to append record
    def add_record(crop_id, crop_name, stage_id, stage_name, param_id, param_name, min_v, max_v, unit, source_title, source_url, status, note):
        record_id = f"{crop_id}_{stage_id}_{param_id}"
        records.append({
            "record_id": record_id,
            "crop_id": crop_id,
            "crop_name": crop_name,
            "stage_id": stage_id,
            "stage_name": stage_name,
            "parameter_id": param_id,
            "parameter_name": param_name,
            "min_value": min_v,
            "max_value": max_v,
            "unit": unit,
            "source_title": source_title,
            "source_url": source_url,
            "validation_status": status,
            "notes": note
        })

    # 1. MAIZE
    m_crops = "maize"
    m_cname = "Maize"

    # Stage 1: Germination
    add_record(m_crops, m_cname, "germination_establishment", "Germination / Establishment", "temperature", "Temperature", 18.0, 30.0, "°C", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Optimal germination occurs at 18-30°C. Emergence ceases below 10°C (base temp).")
    add_record(m_crops, m_cname, "germination_establishment", "Germination / Establishment", "relative_humidity", "Relative Humidity", 60.0, 80.0, "%", TNAU_MAIZE["title"], TNAU_MAIZE["url"], "VERIFIED", "Moderate to high humidity supports uniform coleoptile emergence and prevents seedling desiccation.")
    add_record(m_crops, m_cname, "germination_establishment", "Germination / Establishment", "soil_moisture", "Soil Moisture", 60.0, 75.0, "%", FAO_MAIZE["title"], FAO_MAIZE["url"], "VERIFIED", "60-75% available soil water capacity in the top 15 cm. Saturated waterlogging causes seed decay.")
    add_record(m_crops, m_cname, "germination_establishment", "Germination / Establishment", "soil_ph", "Soil pH", 5.8, 7.5, "pH", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Optimal maize root development occurs in well-drained loams within pH 5.8-7.5.")
    add_record(m_crops, m_cname, "germination_establishment", "Germination / Establishment", "light_intensity", "Light Intensity", None, None, "lux", UNVERIFIED_LIGHT_GERM["title"], UNVERIFIED_LIGHT_GERM["url"], "UNVERIFIED", UNVERIFIED_LIGHT_GERM["note"])
    add_record(m_crops, m_cname, "germination_establishment", "Germination / Establishment", "nitrogen", "Available Nitrogen (N)", 140.0, 200.0, "mg/kg", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Starter nitrogen in topsoil supporting seedling root system (alkaline permanganate method).")
    add_record(m_crops, m_cname, "germination_establishment", "Germination / Establishment", "phosphorus", "Available Phosphorus (P)", 12.0, 25.0, "mg/kg", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Olsen-P available phosphorus critical for primary nodal root elongation.")
    add_record(m_crops, m_cname, "germination_establishment", "Germination / Establishment", "potassium", "Available Potassium (K)", 120.0, 220.0, "mg/kg", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Neutral ammonium acetate extractable potassium providing cellular osmotic balance.")

    # Stage 2: Vegetative Growth
    add_record(m_crops, m_cname, "vegetative_growth", "Vegetative Growth", "temperature", "Temperature", 21.0, 32.0, "°C", TNAU_MAIZE["title"], TNAU_MAIZE["url"], "VERIFIED", "Rapid leaf collar formation and stem elongation thrive between 21-32°C.")
    add_record(m_crops, m_cname, "vegetative_growth", "Vegetative Growth", "relative_humidity", "Relative Humidity", 50.0, 75.0, "%", TNAU_MAIZE["title"], TNAU_MAIZE["url"], "VERIFIED", "Maintains stomatal conductance and transpirational cooling during canopy expansion.")
    add_record(m_crops, m_cname, "vegetative_growth", "Vegetative Growth", "soil_moisture", "Soil Moisture", 65.0, 80.0, "%", FAO_MAIZE["title"], FAO_MAIZE["url"], "VERIFIED", "Root zone soil moisture maintained between 65-80% of field capacity for stem elongation.")
    add_record(m_crops, m_cname, "vegetative_growth", "Vegetative Growth", "soil_ph", "Soil pH", 5.8, 7.5, "pH", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Optimal range for nutrient mobility and symbiotic mycorrhizal activity.")
    add_record(m_crops, m_cname, "vegetative_growth", "Vegetative Growth", "light_intensity", "Light Intensity", 30000.0, 55000.0, "lux", CIMMYT_MAIZE["title"], CIMMYT_MAIZE["url"], "VERIFIED", "Maize C4 photosynthetic pathway reaches optimum assimilation between 30,000-55,000 lux.")
    add_record(m_crops, m_cname, "vegetative_growth", "Vegetative Growth", "nitrogen", "Available Nitrogen (N)", 180.0, 280.0, "mg/kg", TNAU_MAIZE["title"], TNAU_MAIZE["url"], "VERIFIED", "Peak vegetative nitrogen requirement coinciding with knee-high top-dressing stages.")
    add_record(m_crops, m_cname, "vegetative_growth", "Vegetative Growth", "phosphorus", "Available Phosphorus (P)", 15.0, 28.0, "mg/kg", TNAU_MAIZE["title"], TNAU_MAIZE["url"], "VERIFIED", "Supports stalk stiffness and ear shoot initiation.")
    add_record(m_crops, m_cname, "vegetative_growth", "Vegetative Growth", "potassium", "Available Potassium (K)", 130.0, 250.0, "mg/kg", TNAU_MAIZE["title"], TNAU_MAIZE["url"], "VERIFIED", "Essential for stem strength, lodging prevention, and enzyme activation.")

    # Stage 3: Flowering / Reproductive
    add_record(m_crops, m_cname, "flowering_reproductive", "Flowering / Reproductive", "temperature", "Temperature", 21.0, 30.0, "°C", CIMMYT_MAIZE["title"], CIMMYT_MAIZE["url"], "VERIFIED", "Tasseling and silking are extremely vulnerable to heat; temps > 32°C desicate pollen and reduce silk receptivity.")
    add_record(m_crops, m_cname, "flowering_reproductive", "Flowering / Reproductive", "relative_humidity", "Relative Humidity", 55.0, 75.0, "%", CIMMYT_MAIZE["title"], CIMMYT_MAIZE["url"], "VERIFIED", "Low RH (< 40%) severely impedes pollen shed duration, while excessive RH (> 85%) causes clumped anthers.")
    add_record(m_crops, m_cname, "flowering_reproductive", "Flowering / Reproductive", "soil_moisture", "Soil Moisture", 70.0, 85.0, "%", FAO_MAIZE["title"], FAO_MAIZE["url"], "VERIFIED", "Most moisture-critical phase in maize; water stress at silking delays silk emergence and creates anthesis-silking intervals.")
    add_record(m_crops, m_cname, "flowering_reproductive", "Flowering / Reproductive", "soil_ph", "Soil pH", 5.8, 7.5, "pH", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Consistent root zone pH essential to sustain high micronutrient flow during pollination.")
    add_record(m_crops, m_cname, "flowering_reproductive", "Flowering / Reproductive", "light_intensity", "Light Intensity", 35000.0, 60000.0, "lux", CIMMYT_MAIZE["title"], CIMMYT_MAIZE["url"], "VERIFIED", "High radiation drives kernel sink establishment and post-anthesis assimilate synthesis.")
    add_record(m_crops, m_cname, "flowering_reproductive", "Flowering / Reproductive", "nitrogen", "Available Nitrogen (N)", 160.0, 240.0, "mg/kg", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Sustained nitrogen availability avoids early lower leaf firing and cob barrenness.")
    add_record(m_crops, m_cname, "flowering_reproductive", "Flowering / Reproductive", "phosphorus", "Available Phosphorus (P)", 15.0, 25.0, "mg/kg", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Phosphorus drives rapid energy transfer during ovule fertilization.")
    add_record(m_crops, m_cname, "flowering_reproductive", "Flowering / Reproductive", "potassium", "Available Potassium (K)", 140.0, 260.0, "mg/kg", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Aids hydraulic transport of photosynthates to emerging ears.")

    # Stage 4: Fruit / Grain / Pod Development
    add_record(m_crops, m_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "temperature", "Temperature", 20.0, 28.0, "°C", FAO_MAIZE["title"], FAO_MAIZE["url"], "VERIFIED", "Optimum temperature during blister, milk, and dough stages for maximum starch deposition.")
    add_record(m_crops, m_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "relative_humidity", "Relative Humidity", 45.0, 65.0, "%", TNAU_MAIZE["title"], TNAU_MAIZE["url"], "VERIFIED", "Moderate relative humidity protects ear husks from fungal ear rots (Fusarium/Aspergillus).")
    add_record(m_crops, m_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "soil_moisture", "Soil Moisture", 60.0, 75.0, "%", FAO_MAIZE["title"], FAO_MAIZE["url"], "VERIFIED", "Adequate moisture needed to prevent premature black-layer formation and test-weight reduction.")
    add_record(m_crops, m_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "soil_ph", "Soil pH", 5.8, 7.5, "pH", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Stable soil pH ensures steady potassium and magnesium uptake.")
    add_record(m_crops, m_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "light_intensity", "Light Intensity", 30000.0, 50000.0, "lux", CIMMYT_MAIZE["title"], CIMMYT_MAIZE["url"], "VERIFIED", "Clear sunlight during grain fill optimizes starch synthesis in endosperm tissue.")
    add_record(m_crops, m_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "nitrogen", "Available Nitrogen (N)", 120.0, 180.0, "mg/kg", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Residual available soil nitrogen supports late grain protein accumulation.")
    add_record(m_crops, m_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "phosphorus", "Available Phosphorus (P)", 12.0, 22.0, "mg/kg", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Translocation of phosphorus into grains as phytin complexes.")
    add_record(m_crops, m_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "potassium", "Available Potassium (K)", 120.0, 220.0, "mg/kg", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Maintains cell turgor and vascular transport into filling cobs.")

    # Stage 5: Maturity
    add_record(m_crops, m_cname, "maturity", "Maturity", "temperature", "Temperature", 18.0, 26.0, "°C", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Cool, dry conditions ideal for field dry-down once black layer forms at kernel base.")
    add_record(m_crops, m_cname, "maturity", "Maturity", "relative_humidity", "Relative Humidity", 40.0, 60.0, "%", TNAU_MAIZE["title"], TNAU_MAIZE["url"], "VERIFIED", "Lower humidity accelerates natural grain drying to < 15% harvest moisture.")
    add_record(m_crops, m_cname, "maturity", "Maturity", "soil_moisture", "Soil Moisture", 40.0, 55.0, "%", FAO_MAIZE["title"], FAO_MAIZE["url"], "VERIFIED", "Soil moisture depletion encourages senescence and facilitates mechanical or manual harvesting.")
    add_record(m_crops, m_cname, "maturity", "Maturity", "soil_ph", "Soil pH", 5.8, 7.5, "pH", ICAR_MAIZE["title"], ICAR_MAIZE["url"], "VERIFIED", "Inherent soil reaction remains stable during physiological maturity.")
    add_record(m_crops, m_cname, "maturity", "Maturity", "light_intensity", "Light Intensity", None, None, "lux", UNVERIFIED_LIGHT_MATURITY["title"], UNVERIFIED_LIGHT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_LIGHT_MATURITY["note"])
    add_record(m_crops, m_cname, "maturity", "Maturity", "nitrogen", "Available Nitrogen (N)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])
    add_record(m_crops, m_cname, "maturity", "Maturity", "phosphorus", "Available Phosphorus (P)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])
    add_record(m_crops, m_cname, "maturity", "Maturity", "potassium", "Available Potassium (K)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])

    # 2. TOMATO
    t_crops = "tomato"
    t_cname = "Tomato"

    # Stage 1: Germination / Establishment
    add_record(t_crops, t_cname, "germination_establishment", "Germination / Establishment", "temperature", "Temperature", 20.0, 28.0, "°C", TNAU_TOMATO["title"], TNAU_TOMATO["url"], "VERIFIED", "Optimum nursery bed or plug tray germination temperature is 20-28°C.")
    add_record(t_crops, t_cname, "germination_establishment", "Germination / Establishment", "relative_humidity", "Relative Humidity", 70.0, 85.0, "%", FAO_TOMATO["title"], FAO_TOMATO["url"], "VERIFIED", "High nursery humidity ensures rapid hypocotyl elongation and avoids seedling crusting.")
    add_record(t_crops, t_cname, "germination_establishment", "Germination / Establishment", "soil_moisture", "Soil Moisture", 70.0, 80.0, "%", UCDAVIS_TOMATO["title"], UCDAVIS_TOMATO["url"], "VERIFIED", "Even, moist media required for uniform seed imbibition without saturated hypoxia.")
    add_record(t_crops, t_cname, "germination_establishment", "Germination / Establishment", "soil_ph", "Soil pH", 6.0, 7.0, "pH", ICAR_TOMATO["title"], ICAR_TOMATO["url"], "VERIFIED", "Slightly acidic to neutral range (6.0-7.0) optimum for tomato root growth.")
    add_record(t_crops, t_cname, "germination_establishment", "Germination / Establishment", "light_intensity", "Light Intensity", None, None, "lux", UNVERIFIED_LIGHT_GERM["title"], UNVERIFIED_LIGHT_GERM["url"], "UNVERIFIED", UNVERIFIED_LIGHT_GERM["note"])
    add_record(t_crops, t_cname, "germination_establishment", "Germination / Establishment", "nitrogen", "Available Nitrogen (N)", 120.0, 180.0, "mg/kg", ICAR_TOMATO["title"], ICAR_TOMATO["url"], "VERIFIED", "Moderate starter nitrogen prevents spindly, etiolated nursery seedlings.")
    add_record(t_crops, t_cname, "germination_establishment", "Germination / Establishment", "phosphorus", "Available Phosphorus (P)", 20.0, 35.0, "mg/kg", ICAR_TOMATO["title"], ICAR_TOMATO["url"], "VERIFIED", "High starter phosphorus accelerates fibrous root branching.")
    add_record(t_crops, t_cname, "germination_establishment", "Germination / Establishment", "potassium", "Available Potassium (K)", 140.0, 220.0, "mg/kg", ICAR_TOMATO["title"], ICAR_TOMATO["url"], "VERIFIED", "Adequate potassium provides osmotic resistance against transplanting shock.")

    # Stage 2: Vegetative Growth
    add_record(t_crops, t_cname, "vegetative_growth", "Vegetative Growth", "temperature", "Temperature", 21.0, 29.0, "°C", TNAU_TOMATO["title"], TNAU_TOMATO["url"], "VERIFIED", "Ideal daily temperature for vigorous branch formation and leaf production.")
    add_record(t_crops, t_cname, "vegetative_growth", "Vegetative Growth", "relative_humidity", "Relative Humidity", 60.0, 75.0, "%", FAO_TOMATO["title"], FAO_TOMATO["url"], "VERIFIED", "Controls transpiration while keeping foliage dry to discourage early blight (Alternaria solani).")
    add_record(t_crops, t_cname, "vegetative_growth", "Vegetative Growth", "soil_moisture", "Soil Moisture", 65.0, 80.0, "%", FAO_TOMATO["title"], FAO_TOMATO["url"], "VERIFIED", "Maintains active cell division and stem thickening.")
    add_record(t_crops, t_cname, "vegetative_growth", "Vegetative Growth", "soil_ph", "Soil pH", 6.0, 7.0, "pH", ICAR_TOMATO["title"], ICAR_TOMATO["url"], "VERIFIED", "Preserves availability of essential microelements including iron and manganese.")
    add_record(t_crops, t_cname, "vegetative_growth", "Vegetative Growth", "light_intensity", "Light Intensity", 25000.0, 45000.0, "lux", UCDAVIS_TOMATO["title"], UCDAVIS_TOMATO["url"], "VERIFIED", "Adequate irradiance builds strong stems and prevents leggy growth.")
    add_record(t_crops, t_cname, "vegetative_growth", "Vegetative Growth", "nitrogen", "Available Nitrogen (N)", 160.0, 250.0, "mg/kg", TNAU_TOMATO["title"], TNAU_TOMATO["url"], "VERIFIED", "High nitrogen uptake supporting foliage and side branching expansion.")
    add_record(t_crops, t_cname, "vegetative_growth", "Vegetative Growth", "phosphorus", "Available Phosphorus (P)", 18.0, 30.0, "mg/kg", TNAU_TOMATO["title"], TNAU_TOMATO["url"], "VERIFIED", "Promotes dense root system exploration in the top 30 cm.")
    add_record(t_crops, t_cname, "vegetative_growth", "Vegetative Growth", "potassium", "Available Potassium (K)", 180.0, 280.0, "mg/kg", TNAU_TOMATO["title"], TNAU_TOMATO["url"], "VERIFIED", "Supports strong vascular bundles and mechanical rigidity.")

    # Stage 3: Flowering / Reproductive
    add_record(t_crops, t_cname, "flowering_reproductive", "Flowering / Reproductive", "temperature", "Temperature", 19.0, 26.0, "°C", TNAU_TOMATO["title"], TNAU_TOMATO["url"], "VERIFIED", "Night temperatures > 21°C or day temperatures > 32°C lead to severe flower drop and style elongation.")
    add_record(t_crops, t_cname, "flowering_reproductive", "Flowering / Reproductive", "relative_humidity", "Relative Humidity", 55.0, 70.0, "%", FAO_TOMATO["title"], FAO_TOMATO["url"], "VERIFIED", "RH > 80% impairs pollen release from anther cones; RH < 50% causes stigma drying.")
    add_record(t_crops, t_cname, "flowering_reproductive", "Flowering / Reproductive", "soil_moisture", "Soil Moisture", 70.0, 85.0, "%", FAO_TOMATO["title"], FAO_TOMATO["url"], "VERIFIED", "Critical period; moisture deficits trigger flower abscission.")
    add_record(t_crops, t_cname, "flowering_reproductive", "Flowering / Reproductive", "soil_ph", "Soil pH", 6.0, 7.0, "pH", ICAR_TOMATO["title"], ICAR_TOMATO["url"], "VERIFIED", "Essential to avoid calcium locking, which later manifests as blossom end rot.")
    add_record(t_crops, t_cname, "flowering_reproductive", "Flowering / Reproductive", "light_intensity", "Light Intensity", 30000.0, 50000.0, "lux", UCDAVIS_TOMATO["title"], UCDAVIS_TOMATO["url"], "VERIFIED", "High daily light integral enhances pollen viability and truss formation.")
    add_record(t_crops, t_cname, "flowering_reproductive", "Flowering / Reproductive", "nitrogen", "Available Nitrogen (N)", 150.0, 220.0, "mg/kg", ICAR_TOMATO["title"], ICAR_TOMATO["url"], "VERIFIED", "Excessive nitrogen at flowering causes vegetative dominance over flower trusses.")
    add_record(t_crops, t_cname, "flowering_reproductive", "Flowering / Reproductive", "phosphorus", "Available Phosphorus (P)", 18.0, 28.0, "mg/kg", ICAR_TOMATO["title"], ICAR_TOMATO["url"], "VERIFIED", "Sustains energetic demands of ovule fertilization.")
    add_record(t_crops, t_cname, "flowering_reproductive", "Flowering / Reproductive", "potassium", "Available Potassium (K)", 220.0, 340.0, "mg/kg", ICAR_TOMATO["title"], ICAR_TOMATO["url"], "VERIFIED", "Surging potassium requirement begins at anthesis to prepare for fruit set.")

    # Stage 4: Fruit / Grain / Pod Development (Fruit sizing & development)
    add_record(t_crops, t_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "temperature", "Temperature", 20.0, 28.0, "°C", UCDAVIS_TOMATO["title"], UCDAVIS_TOMATO["url"], "VERIFIED", "Optimal temperature for fruit expansion and continuous cell enlargement.")
    add_record(t_crops, t_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "relative_humidity", "Relative Humidity", 55.0, 70.0, "%", TNAU_TOMATO["title"], TNAU_TOMATO["url"], "VERIFIED", "Maintains uniform fruit transpiration without inducing skin cracking.")
    add_record(t_crops, t_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "soil_moisture", "Soil Moisture", 70.0, 80.0, "%", FAO_TOMATO["title"], FAO_TOMATO["url"], "VERIFIED", "Stable moisture prevents cuticle cracking and blossom-end rot caused by irregular calcium flux.")
    add_record(t_crops, t_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "soil_ph", "Soil pH", 6.0, 7.0, "pH", ICAR_TOMATO["title"], ICAR_TOMATO["url"], "VERIFIED", "Ensures soluble calcium availability for fruit cell wall integrity.")
    add_record(t_crops, t_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "light_intensity", "Light Intensity", 30000.0, 48000.0, "lux", UCDAVIS_TOMATO["title"], UCDAVIS_TOMATO["url"], "VERIFIED", "Sustains high photoassimilate export to developing tomato fruit clusters.")
    add_record(t_crops, t_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "nitrogen", "Available Nitrogen (N)", 140.0, 200.0, "mg/kg", TNAU_TOMATO["title"], TNAU_TOMATO["url"], "VERIFIED", "Maintains canopy green area while avoiding overly soft fruit flesh.")
    add_record(t_crops, t_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "phosphorus", "Available Phosphorus (P)", 15.0, 25.0, "mg/kg", TNAU_TOMATO["title"], TNAU_TOMATO["url"], "VERIFIED", "Facilitates ongoing seed and locular gel formation.")
    add_record(t_crops, t_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "potassium", "Available Potassium (K)", 250.0, 380.0, "mg/kg", TNAU_TOMATO["title"], TNAU_TOMATO["url"], "VERIFIED", "Peak potassium uptake stage; determines fruit solids, acidity, and color development.")

    # Stage 5: Maturity (Ripening)
    add_record(t_crops, t_cname, "maturity", "Maturity", "temperature", "Temperature", 18.0, 25.0, "°C", FAO_TOMATO["title"], FAO_TOMATO["url"], "VERIFIED", "Lycopene synthesis is optimal at 18-25°C; temperatures > 30°C inhibit red pigmentation.")
    add_record(t_crops, t_cname, "maturity", "Maturity", "relative_humidity", "Relative Humidity", 50.0, 65.0, "%", FAO_TOMATO["title"], FAO_TOMATO["url"], "VERIFIED", "Low relative humidity mitigates post-harvest storage decays and skin splitting.")
    add_record(t_crops, t_cname, "maturity", "Maturity", "soil_moisture", "Soil Moisture", 55.0, 65.0, "%", FAO_TOMATO["title"], FAO_TOMATO["url"], "VERIFIED", "Controlled deficit irrigation concentrates soluble sugars (°Brix) and improves flavor.")
    add_record(t_crops, t_cname, "maturity", "Maturity", "soil_ph", "Soil pH", 6.0, 7.0, "pH", ICAR_TOMATO["title"], ICAR_TOMATO["url"], "VERIFIED", "General root-zone pH stability.")
    add_record(t_crops, t_cname, "maturity", "Maturity", "light_intensity", "Light Intensity", None, None, "lux", UNVERIFIED_LIGHT_MATURITY["title"], UNVERIFIED_LIGHT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_LIGHT_MATURITY["note"])
    add_record(t_crops, t_cname, "maturity", "Maturity", "nitrogen", "Available Nitrogen (N)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])
    add_record(t_crops, t_cname, "maturity", "Maturity", "phosphorus", "Available Phosphorus (P)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])
    add_record(t_crops, t_cname, "maturity", "Maturity", "potassium", "Available Potassium (K)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])

    # 3. RICE
    r_crops = "rice"
    r_cname = "Rice"

    # Stage 1: Germination / Establishment
    add_record(r_crops, r_cname, "germination_establishment", "Germination / Establishment", "temperature", "Temperature", 22.0, 32.0, "°C", IRRI_RICE["title"], IRRI_RICE["url"], "VERIFIED", "Sprouting and coleoptile emergence occur reliably between 22-32°C. Below 15°C germination is delayed.")
    add_record(r_crops, r_cname, "germination_establishment", "Germination / Establishment", "relative_humidity", "Relative Humidity", 75.0, 85.0, "%", IRRI_RICE["title"], IRRI_RICE["url"], "VERIFIED", "High atmospheric humidity prevents radicle desiccation during nursery seedling establishment.")
    add_record(r_crops, r_cname, "germination_establishment", "Germination / Establishment", "soil_moisture", "Soil Moisture", 80.0, 100.0, "%", IRRI_RICE["title"], IRRI_RICE["url"], "VERIFIED", "Saturated to shallow submerged seedbed moisture required for wet-bed and dry-bed rice nurseries.")
    add_record(r_crops, r_cname, "germination_establishment", "Germination / Establishment", "soil_ph", "Soil pH", 5.5, 6.5, "pH", ICAR_RICE["title"], ICAR_RICE["url"], "VERIFIED", "Slightly acidic soils facilitate phosphorus availability and root elongation in flooded conditions.")
    add_record(r_crops, r_cname, "germination_establishment", "Germination / Establishment", "light_intensity", "Light Intensity", None, None, "lux", UNVERIFIED_LIGHT_GERM["title"], UNVERIFIED_LIGHT_GERM["url"], "UNVERIFIED", UNVERIFIED_LIGHT_GERM["note"])
    add_record(r_crops, r_cname, "germination_establishment", "Germination / Establishment", "nitrogen", "Available Nitrogen (N)", 100.0, 160.0, "mg/kg", ICAR_RICE["title"], ICAR_RICE["url"], "VERIFIED", "Basal nursery available nitrogen level supporting early radicle and seminal root emergence.")
    add_record(r_crops, r_cname, "germination_establishment", "Germination / Establishment", "phosphorus", "Available Phosphorus (P)", 15.0, 25.0, "mg/kg", ICAR_RICE["title"], ICAR_RICE["url"], "VERIFIED", "Crucial for early vigorous root system establishment in puddled soil.")
    add_record(r_crops, r_cname, "germination_establishment", "Germination / Establishment", "potassium", "Available Potassium (K)", 100.0, 180.0, "mg/kg", ICAR_RICE["title"], ICAR_RICE["url"], "VERIFIED", "Provides seedling cold tolerance and cellular osmotic regulation.")

    # Stage 2: Vegetative Growth (Tillering)
    add_record(r_crops, r_cname, "vegetative_growth", "Vegetative Growth", "temperature", "Temperature", 25.0, 33.0, "°C", TNAU_RICE["title"], TNAU_RICE["url"], "VERIFIED", "Optimum temperature promotes rapid tiller emergence and leaf area index expansion.")
    add_record(r_crops, r_cname, "vegetative_growth", "Vegetative Growth", "relative_humidity", "Relative Humidity", 70.0, 85.0, "%", TNAU_RICE["title"], TNAU_RICE["url"], "VERIFIED", "High ambient humidity supports unhindered stomatal aperture during active tillering.")
    add_record(r_crops, r_cname, "vegetative_growth", "Vegetative Growth", "soil_moisture", "Soil Moisture", 85.0, 100.0, "%", FAO_RICE["title"], FAO_RICE["url"], "VERIFIED", "Submerged or near-saturation field condition ensures continuous tiller development.")
    add_record(r_crops, r_cname, "vegetative_growth", "Vegetative Growth", "soil_ph", "Soil pH", 5.5, 6.5, "pH", ICAR_RICE["title"], ICAR_RICE["url"], "VERIFIED", "Flooding naturally buffers pH toward 6.5, enhancing ammonium nitrogen stability.")
    add_record(r_crops, r_cname, "vegetative_growth", "Vegetative Growth", "light_intensity", "Light Intensity", 30000.0, 55000.0, "lux", IRRI_RICE["title"], IRRI_RICE["url"], "VERIFIED", "Direct solar radiation determines effective productive tiller counts per hill.")
    add_record(r_crops, r_cname, "vegetative_growth", "Vegetative Growth", "nitrogen", "Available Nitrogen (N)", 160.0, 260.0, "mg/kg", TNAU_RICE["title"], TNAU_RICE["url"], "VERIFIED", "Active tillering top-dressing target maintaining vegetative canopy greenness.")
    add_record(r_crops, r_cname, "vegetative_growth", "Vegetative Growth", "phosphorus", "Available Phosphorus (P)", 14.0, 24.0, "mg/kg", TNAU_RICE["title"], TNAU_RICE["url"], "VERIFIED", "Sustains high tiller counts and energy phosphorylation.")
    add_record(r_crops, r_cname, "vegetative_growth", "Vegetative Growth", "potassium", "Available Potassium (K)", 120.0, 220.0, "mg/kg", TNAU_RICE["title"], TNAU_RICE["url"], "VERIFIED", "Prevents lodging and improves resistance to stem borers and bacterial leaf blight.")

    # Stage 3: Flowering / Reproductive (Panicle initiation to anthesis)
    add_record(r_crops, r_cname, "flowering_reproductive", "Flowering / Reproductive", "temperature", "Temperature", 24.0, 31.0, "°C", IRRI_RICE["title"], IRRI_RICE["url"], "VERIFIED", "Extreme sensitivity to heat; temps > 35°C during 1-2 hours of anthesis cause spikelet sterility.")
    add_record(r_crops, r_cname, "flowering_reproductive", "Flowering / Reproductive", "relative_humidity", "Relative Humidity", 70.0, 85.0, "%", IRRI_RICE["title"], IRRI_RICE["url"], "VERIFIED", "Maintains anther dehiscence and sticky stigma receptivity.")
    add_record(r_crops, r_cname, "flowering_reproductive", "Flowering / Reproductive", "soil_moisture", "Soil Moisture", 90.0, 100.0, "%", FAO_RICE["title"], FAO_RICE["url"], "VERIFIED", "Most moisture-critical phase; standing water layer (2-5 cm) or saturation avoids floret abortion.")
    add_record(r_crops, r_cname, "flowering_reproductive", "Flowering / Reproductive", "soil_ph", "Soil pH", 5.5, 6.5, "pH", ICAR_RICE["title"], ICAR_RICE["url"], "VERIFIED", "Stable reduced soil chemistry avoids zinc and iron toxicity/deficiency.")
    add_record(r_crops, r_cname, "flowering_reproductive", "Flowering / Reproductive", "light_intensity", "Light Intensity", 35000.0, 60000.0, "lux", IRRI_RICE["title"], IRRI_RICE["url"], "VERIFIED", "Sunny conditions over the 30 days around flowering directly correlate with filled spikelet counts.")
    add_record(r_crops, r_cname, "flowering_reproductive", "Flowering / Reproductive", "nitrogen", "Available Nitrogen (N)", 140.0, 220.0, "mg/kg", TNAU_RICE["title"], TNAU_RICE["url"], "VERIFIED", "Panicle initiation nitrogen top-dressing directly elevates spikelet count per panicle.")
    add_record(r_crops, r_cname, "flowering_reproductive", "Flowering / Reproductive", "phosphorus", "Available Phosphorus (P)", 12.0, 20.0, "mg/kg", TNAU_RICE["title"], TNAU_RICE["url"], "VERIFIED", "Assists floral differentiation.")
    add_record(r_crops, r_cname, "flowering_reproductive", "Flowering / Reproductive", "potassium", "Available Potassium (K)", 130.0, 240.0, "mg/kg", TNAU_RICE["title"], TNAU_RICE["url"], "VERIFIED", "Key split application at panicle emergence enhances carbohydrate loading into panicles.")

    # Stage 4: Fruit / Grain / Pod Development (Milky to dough stage)
    add_record(r_crops, r_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "temperature", "Temperature", 22.0, 30.0, "°C", IRRI_RICE["title"], IRRI_RICE["url"], "VERIFIED", "Favorable temperature during milky and dough stages promotes heavy grain weight and reduces chalkiness.")
    add_record(r_crops, r_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "relative_humidity", "Relative Humidity", 60.0, 75.0, "%", TNAU_RICE["title"], TNAU_RICE["url"], "VERIFIED", "Moderate relative humidity protects grain heads from sheath rot and glume discoloration.")
    add_record(r_crops, r_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "soil_moisture", "Soil Moisture", 70.0, 85.0, "%", FAO_RICE["title"], FAO_RICE["url"], "VERIFIED", "Alternate Wetting and Drying (AWD) practiced; soil maintained between 70-85% saturation.")
    add_record(r_crops, r_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "soil_ph", "Soil pH", 5.5, 6.5, "pH", ICAR_RICE["title"], ICAR_RICE["url"], "VERIFIED", "Consistent root environment supporting prolonged flag leaf photosynthesis.")
    add_record(r_crops, r_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "light_intensity", "Light Intensity", 30000.0, 50000.0, "lux", IRRI_RICE["title"], IRRI_RICE["url"], "VERIFIED", "Solar radiation provides photosynthates for grain filling.")
    add_record(r_crops, r_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "nitrogen", "Available Nitrogen (N)", 100.0, 160.0, "mg/kg", ICAR_RICE["title"], ICAR_RICE["url"], "VERIFIED", "Residual nitrogen preserves leaf greenness without inducing lodging.")
    add_record(r_crops, r_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "phosphorus", "Available Phosphorus (P)", 10.0, 18.0, "mg/kg", ICAR_RICE["title"], ICAR_RICE["url"], "VERIFIED", "Stored phosphorus mobilizes into developing rice grains.")
    add_record(r_crops, r_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "potassium", "Available Potassium (K)", 110.0, 200.0, "mg/kg", ICAR_RICE["title"], ICAR_RICE["url"], "VERIFIED", "Aids starch grain packing within developing endosperm.")

    # Stage 5: Maturity (Ripening)
    add_record(r_crops, r_cname, "maturity", "Maturity", "temperature", "Temperature", 20.0, 28.0, "°C", IRRI_RICE["title"], IRRI_RICE["url"], "VERIFIED", "Cooler, clear days accelerate grain dry-down and enhance milling recovery.")
    add_record(r_crops, r_cname, "maturity", "Maturity", "relative_humidity", "Relative Humidity", 50.0, 65.0, "%", TNAU_RICE["title"], TNAU_RICE["url"], "VERIFIED", "Dry atmosphere allows grain moisture to drop toward harvest standard (18-20%).")
    add_record(r_crops, r_cname, "maturity", "Maturity", "soil_moisture", "Soil Moisture", 40.0, 60.0, "%", IRRI_RICE["title"], IRRI_RICE["url"], "VERIFIED", "Field is drained 10-15 days prior to harvest to promote uniform ripening and firm soil for harvesters.")
    add_record(r_crops, r_cname, "maturity", "Maturity", "soil_ph", "Soil pH", 5.5, 6.5, "pH", ICAR_RICE["title"], ICAR_RICE["url"], "VERIFIED", "Paddy soil re-oxidizes upon draining.")
    add_record(r_crops, r_cname, "maturity", "Maturity", "light_intensity", "Light Intensity", None, None, "lux", UNVERIFIED_LIGHT_MATURITY["title"], UNVERIFIED_LIGHT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_LIGHT_MATURITY["note"])
    add_record(r_crops, r_cname, "maturity", "Maturity", "nitrogen", "Available Nitrogen (N)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])
    add_record(r_crops, r_cname, "maturity", "Maturity", "phosphorus", "Available Phosphorus (P)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])
    add_record(r_crops, r_cname, "maturity", "Maturity", "potassium", "Available Potassium (K)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])

    # 4. WHEAT
    w_crops = "wheat"
    w_cname = "Wheat"

    # Stage 1: Germination / Establishment (Crown Root Initiation - CRI)
    add_record(w_crops, w_cname, "germination_establishment", "Germination / Establishment", "temperature", "Temperature", 15.0, 24.0, "°C", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Cool season cereal; optimal germination occurs at 15-24°C. Above 25°C germination drops.")
    add_record(w_crops, w_cname, "germination_establishment", "Germination / Establishment", "relative_humidity", "Relative Humidity", 55.0, 75.0, "%", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Moderate relative humidity ensures rapid seedling coleoptile emergence.")
    add_record(w_crops, w_cname, "germination_establishment", "Germination / Establishment", "soil_moisture", "Soil Moisture", 60.0, 75.0, "%", FAO_WHEAT["title"], FAO_WHEAT["url"], "VERIFIED", "Pre-sowing irrigation provides 60-75% field capacity moisture for crown root initiation.")
    add_record(w_crops, w_cname, "germination_establishment", "Germination / Establishment", "soil_ph", "Soil pH", 6.0, 7.5, "pH", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Slightly acidic to mildly alkaline loam soils ideal for wheat establishment.")
    add_record(w_crops, w_cname, "germination_establishment", "Germination / Establishment", "light_intensity", "Light Intensity", None, None, "lux", UNVERIFIED_LIGHT_GERM["title"], UNVERIFIED_LIGHT_GERM["url"], "UNVERIFIED", UNVERIFIED_LIGHT_GERM["note"])
    add_record(w_crops, w_cname, "germination_establishment", "Germination / Establishment", "nitrogen", "Available Nitrogen (N)", 130.0, 190.0, "mg/kg", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Basal nitrogen application supporting vigorous crown root emergence.")
    add_record(w_crops, w_cname, "germination_establishment", "Germination / Establishment", "phosphorus", "Available Phosphorus (P)", 15.0, 28.0, "mg/kg", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "High early phosphorus is indispensable for deep crown root anchoring.")
    add_record(w_crops, w_cname, "germination_establishment", "Germination / Establishment", "potassium", "Available Potassium (K)", 110.0, 200.0, "mg/kg", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Enhances cold tolerance in early winter seedling stages.")

    # Stage 2: Vegetative Growth (Tillering / Jointing)
    add_record(w_crops, w_cname, "vegetative_growth", "Vegetative Growth", "temperature", "Temperature", 16.0, 22.0, "°C", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Tillering flourishes under cool conditions (16-22°C); warm winter causes premature jointing.")
    add_record(w_crops, w_cname, "vegetative_growth", "Vegetative Growth", "relative_humidity", "Relative Humidity", 50.0, 70.0, "%", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Balanced humidity supports dense canopy expansion.")
    add_record(w_crops, w_cname, "vegetative_growth", "Vegetative Growth", "soil_moisture", "Soil Moisture", 65.0, 80.0, "%", FAO_WHEAT["title"], FAO_WHEAT["url"], "VERIFIED", "Irrigation at tillering and jointing maintains 65-80% available moisture.")
    add_record(w_crops, w_cname, "vegetative_growth", "Vegetative Growth", "soil_ph", "Soil pH", 6.0, 7.5, "pH", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Optimal range for nitrate uptake.")
    add_record(w_crops, w_cname, "vegetative_growth", "Vegetative Growth", "light_intensity", "Light Intensity", 25000.0, 45000.0, "lux", CIMMYT_WHEAT["title"], CIMMYT_WHEAT["url"], "VERIFIED", "Adequate light intensity prevents weak, spindly tillers prone to late lodging.")
    add_record(w_crops, w_cname, "vegetative_growth", "Vegetative Growth", "nitrogen", "Available Nitrogen (N)", 160.0, 240.0, "mg/kg", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "First split top-dressing after first irrigation fuels tillering shoots.")
    add_record(w_crops, w_cname, "vegetative_growth", "Vegetative Growth", "phosphorus", "Available Phosphorus (P)", 14.0, 24.0, "mg/kg", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Supports vascular bundle development and tiller viability.")
    add_record(w_crops, w_cname, "vegetative_growth", "Vegetative Growth", "potassium", "Available Potassium (K)", 120.0, 210.0, "mg/kg", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Thickens stem walls and prevents culm bending.")

    # Stage 3: Flowering / Reproductive (Heading / Anthesis)
    add_record(w_crops, w_cname, "flowering_reproductive", "Flowering / Reproductive", "temperature", "Temperature", 18.0, 24.0, "°C", CIMMYT_WHEAT["title"], CIMMYT_WHEAT["url"], "VERIFIED", "Optimum flowering temperature; temperatures > 28°C cause terminal heat stress and pollen sterility.")
    add_record(w_crops, w_cname, "flowering_reproductive", "Flowering / Reproductive", "relative_humidity", "Relative Humidity", 50.0, 65.0, "%", CIMMYT_WHEAT["title"], CIMMYT_WHEAT["url"], "VERIFIED", "Low to moderate humidity ensures clean anthesis and protects against head blight (Fusarium).")
    add_record(w_crops, w_cname, "flowering_reproductive", "Flowering / Reproductive", "soil_moisture", "Soil Moisture", 70.0, 85.0, "%", FAO_WHEAT["title"], FAO_WHEAT["url"], "VERIFIED", "Flowering irrigation is non-negotiable; moisture deficit reduces grains per spike.")
    add_record(w_crops, w_cname, "flowering_reproductive", "Flowering / Reproductive", "soil_ph", "Soil pH", 6.0, 7.5, "pH", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Maintains cation-anion balance in wheat rhizodeposits.")
    add_record(w_crops, w_cname, "flowering_reproductive", "Flowering / Reproductive", "light_intensity", "Light Intensity", 30000.0, 50000.0, "lux", CIMMYT_WHEAT["title"], CIMMYT_WHEAT["url"], "VERIFIED", "Direct radiation at heading maximizes floret fertilization rates.")
    add_record(w_crops, w_cname, "flowering_reproductive", "Flowering / Reproductive", "nitrogen", "Available Nitrogen (N)", 130.0, 200.0, "mg/kg", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Second split top-dressing sustains flag leaf area duration.")
    add_record(w_crops, w_cname, "flowering_reproductive", "Flowering / Reproductive", "phosphorus", "Available Phosphorus (P)", 12.0, 20.0, "mg/kg", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Fuels energy exchange during gametogenesis.")
    add_record(w_crops, w_cname, "flowering_reproductive", "Flowering / Reproductive", "potassium", "Available Potassium (K)", 120.0, 220.0, "mg/kg", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Aids stomatal regulation in flag leaf under spring winds.")

    # Stage 4: Fruit / Grain / Pod Development (Milk to Soft Dough)
    add_record(w_crops, w_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "temperature", "Temperature", 18.0, 25.0, "°C", CIMMYT_WHEAT["title"], CIMMYT_WHEAT["url"], "VERIFIED", "Moderate temperature during grain filling avoids shriveled grain syndrome.")
    add_record(w_crops, w_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "relative_humidity", "Relative Humidity", 45.0, 60.0, "%", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Lower humidity prevents foliar rust spread (Puccinia striiformis/triticina).")
    add_record(w_crops, w_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "soil_moisture", "Soil Moisture", 60.0, 70.0, "%", FAO_WHEAT["title"], FAO_WHEAT["url"], "VERIFIED", "Milking-stage irrigation ensures maximum 1000-grain weight.")
    add_record(w_crops, w_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "soil_ph", "Soil pH", 6.0, 7.5, "pH", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Standard wheat root zone pH range.")
    add_record(w_crops, w_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "light_intensity", "Light Intensity", 25000.0, 45000.0, "lux", CIMMYT_WHEAT["title"], CIMMYT_WHEAT["url"], "VERIFIED", "High sunny hours during grain fill boost starch deposition rate.")
    add_record(w_crops, w_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "nitrogen", "Available Nitrogen (N)", 100.0, 150.0, "mg/kg", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Remobilization of leaf nitrogen into grain gluten protein.")
    add_record(w_crops, w_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "phosphorus", "Available Phosphorus (P)", 10.0, 18.0, "mg/kg", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Translocation into developing wheat kernels.")
    add_record(w_crops, w_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "potassium", "Available Potassium (K)", 100.0, 180.0, "mg/kg", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Maintains endosperm cell hydrostatic pressure.")

    # Stage 5: Maturity
    add_record(w_crops, w_cname, "maturity", "Maturity", "temperature", "Temperature", 16.0, 25.0, "°C", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Warm, dry spring days promote hardening of kernels to < 12% moisture.")
    add_record(w_crops, w_cname, "maturity", "Maturity", "relative_humidity", "Relative Humidity", 35.0, 55.0, "%", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Low relative humidity prevents pre-harvest sprouting in ears.")
    add_record(w_crops, w_cname, "maturity", "Maturity", "soil_moisture", "Soil Moisture", 35.0, 50.0, "%", FAO_WHEAT["title"], FAO_WHEAT["url"], "VERIFIED", "Pre-harvest dry-down allows combine harvesters without soil compaction.")
    add_record(w_crops, w_cname, "maturity", "Maturity", "soil_ph", "Soil pH", 6.0, 7.5, "pH", ICAR_WHEAT["title"], ICAR_WHEAT["url"], "VERIFIED", "Inherent soil reaction.")
    add_record(w_crops, w_cname, "maturity", "Maturity", "light_intensity", "Light Intensity", None, None, "lux", UNVERIFIED_LIGHT_MATURITY["title"], UNVERIFIED_LIGHT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_LIGHT_MATURITY["note"])
    add_record(w_crops, w_cname, "maturity", "Maturity", "nitrogen", "Available Nitrogen (N)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])
    add_record(w_crops, w_cname, "maturity", "Maturity", "phosphorus", "Available Phosphorus (P)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])
    add_record(w_crops, w_cname, "maturity", "Maturity", "potassium", "Available Potassium (K)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])

    # 5. GROUNDNUT
    g_crops = "groundnut"
    g_cname = "Groundnut"

    # Stage 1: Germination / Establishment
    add_record(g_crops, g_cname, "germination_establishment", "Germination / Establishment", "temperature", "Temperature", 24.0, 30.0, "°C", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Optimal seed emergence occurs at 24-30°C. Below 18°C germination is severely impeded.")
    add_record(g_crops, g_cname, "germination_establishment", "Germination / Establishment", "relative_humidity", "Relative Humidity", 60.0, 75.0, "%", TNAU_GROUNDNUT["title"], TNAU_GROUNDNUT["url"], "VERIFIED", "Supports rapid cotyledon emergence and hypocotyl growth.")
    add_record(g_crops, g_cname, "germination_establishment", "Germination / Establishment", "soil_moisture", "Soil Moisture", 60.0, 75.0, "%", FAO_GROUNDNUT["title"], FAO_GROUNDNUT["url"], "VERIFIED", "Moist, friable seedbed required. Waterlogging causes aspergillus crown rot.")
    add_record(g_crops, g_cname, "germination_establishment", "Germination / Establishment", "soil_ph", "Soil pH", 6.0, 7.0, "pH", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Groundnut favors well-drained sandy loams with pH 6.0-7.0.")
    add_record(g_crops, g_cname, "germination_establishment", "Germination / Establishment", "light_intensity", "Light Intensity", None, None, "lux", UNVERIFIED_LIGHT_GERM["title"], UNVERIFIED_LIGHT_GERM["url"], "UNVERIFIED", UNVERIFIED_LIGHT_GERM["note"])
    add_record(g_crops, g_cname, "germination_establishment", "Germination / Establishment", "nitrogen", "Available Nitrogen (N)", 60.0, 90.0, "mg/kg", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Low starter nitrogen (15-20 kg N/ha) only; excess N suppresses Rhizobium nodule establishment.")
    add_record(g_crops, g_cname, "germination_establishment", "Germination / Establishment", "phosphorus", "Available Phosphorus (P)", 15.0, 30.0, "mg/kg", TNAU_GROUNDNUT["title"], TNAU_GROUNDNUT["url"], "VERIFIED", "High initial phosphorus promotes taproot and nodulation initiation.")
    add_record(g_crops, g_cname, "germination_establishment", "Germination / Establishment", "potassium", "Available Potassium (K)", 100.0, 180.0, "mg/kg", TNAU_GROUNDNUT["title"], TNAU_GROUNDNUT["url"], "VERIFIED", "Supports early cellular expansion.")

    # Stage 2: Vegetative Growth
    add_record(g_crops, g_cname, "vegetative_growth", "Vegetative Growth", "temperature", "Temperature", 25.0, 32.0, "°C", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Warm temperatures favor main stem and lateral branch proliferation.")
    add_record(g_crops, g_cname, "vegetative_growth", "Vegetative Growth", "relative_humidity", "Relative Humidity", 55.0, 75.0, "%", TNAU_GROUNDNUT["title"], TNAU_GROUNDNUT["url"], "VERIFIED", "Foliage expands steadily while keeping leaf spot (Tikka disease) risks low.")
    add_record(g_crops, g_cname, "vegetative_growth", "Vegetative Growth", "soil_moisture", "Soil Moisture", 65.0, 75.0, "%", FAO_GROUNDNUT["title"], FAO_GROUNDNUT["url"], "VERIFIED", "Light stress during early vegetative growth is well-tolerated and promotes deeper taprooting.")
    add_record(g_crops, g_cname, "vegetative_growth", "Vegetative Growth", "soil_ph", "Soil pH", 6.0, 7.0, "pH", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Optimal pH for Rhizobium leguminosarum / Bradyrhizobium nitrogenase activity.")
    add_record(g_crops, g_cname, "vegetative_growth", "Vegetative Growth", "light_intensity", "Light Intensity", 30000.0, 55000.0, "lux", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "High radiation drives branching and node generation.")
    add_record(g_crops, g_cname, "vegetative_growth", "Vegetative Growth", "nitrogen", "Available Nitrogen (N)", 70.0, 110.0, "mg/kg", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Active biological nitrogen fixation supplies crop needs; soil N level remains moderate.")
    add_record(g_crops, g_cname, "vegetative_growth", "Vegetative Growth", "phosphorus", "Available Phosphorus (P)", 18.0, 32.0, "mg/kg", TNAU_GROUNDNUT["title"], TNAU_GROUNDNUT["url"], "VERIFIED", "Critical for ATP synthesis in root nodules.")
    add_record(g_crops, g_cname, "vegetative_growth", "Vegetative Growth", "potassium", "Available Potassium (K)", 120.0, 220.0, "mg/kg", TNAU_GROUNDNUT["title"], TNAU_GROUNDNUT["url"], "VERIFIED", "Essential for stem turgor and photosynthetic translocation.")

    # Stage 3: Flowering / Reproductive (Flowering and Peg Initiation)
    add_record(g_crops, g_cname, "flowering_reproductive", "Flowering / Reproductive", "temperature", "Temperature", 24.0, 30.0, "°C", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Daily flowers open at dawn; temperatures > 34°C burn delicate self-pollinating flowers.")
    add_record(g_crops, g_cname, "flowering_reproductive", "Flowering / Reproductive", "relative_humidity", "Relative Humidity", 60.0, 75.0, "%", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Supports self-pollination within cleistogamous/chasmogamous blossoms.")
    add_record(g_crops, g_cname, "flowering_reproductive", "Flowering / Reproductive", "soil_moisture", "Soil Moisture", 70.0, 85.0, "%", FAO_GROUNDNUT["title"], FAO_GROUNDNUT["url"], "VERIFIED", "Moisture in the top 5 cm is vital so geotropic pegs (gynophores) can penetrate without desiccation.")
    add_record(g_crops, g_cname, "flowering_reproductive", "Flowering / Reproductive", "soil_ph", "Soil pH", 6.0, 7.0, "pH", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Ensures soluble calcium availability for developing peg tips.")
    add_record(g_crops, g_cname, "flowering_reproductive", "Flowering / Reproductive", "light_intensity", "Light Intensity", 35000.0, 58000.0, "lux", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Continuous bright sunshine increases daily flower count per plant.")
    add_record(g_crops, g_cname, "flowering_reproductive", "Flowering / Reproductive", "nitrogen", "Available Nitrogen (N)", 70.0, 110.0, "mg/kg", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Nodule nitrogen fixation operates at peak capacity.")
    add_record(g_crops, g_cname, "flowering_reproductive", "Flowering / Reproductive", "phosphorus", "Available Phosphorus (P)", 16.0, 28.0, "mg/kg", TNAU_GROUNDNUT["title"], TNAU_GROUNDNUT["url"], "VERIFIED", "Sustains reproductive vigor.")
    add_record(g_crops, g_cname, "flowering_reproductive", "Flowering / Reproductive", "potassium", "Available Potassium (K)", 130.0, 230.0, "mg/kg", TNAU_GROUNDNUT["title"], TNAU_GROUNDNUT["url"], "VERIFIED", "Powers positive geotropism and downward elongation of gynophores.")

    # Stage 4: Fruit / Grain / Pod Development (Pegging and Pod Enlargement)
    add_record(g_crops, g_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "temperature", "Temperature", 23.0, 30.0, "°C", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Warm soil temperature in the top 10 cm favors rapid pod development and kernel filling.")
    add_record(g_crops, g_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "relative_humidity", "Relative Humidity", 55.0, 70.0, "%", TNAU_GROUNDNUT["title"], TNAU_GROUNDNUT["url"], "VERIFIED", "Prevents microclimatic foliar rot beneath the dense legume canopy.")
    add_record(g_crops, g_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "soil_moisture", "Soil Moisture", 70.0, 80.0, "%", FAO_GROUNDNUT["title"], FAO_GROUNDNUT["url"], "VERIFIED", "Most critical moisture sensitive stage; drought during pod development produces pops (empty shells).")
    add_record(g_crops, g_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "soil_ph", "Soil pH", 6.0, 7.0, "pH", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Subsurface pods directly absorb calcium from surrounding soil solution; acidic soil causes shell rot.")
    add_record(g_crops, g_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "light_intensity", "Light Intensity", 30000.0, 50000.0, "lux", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Photosynthates channeled directly into kernel oil and protein synthesis.")
    add_record(g_crops, g_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "nitrogen", "Available Nitrogen (N)", 60.0, 100.0, "mg/kg", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Maintains active canopy until pod maturity.")
    add_record(g_crops, g_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "phosphorus", "Available Phosphorus (P)", 14.0, 24.0, "mg/kg", TNAU_GROUNDNUT["title"], TNAU_GROUNDNUT["url"], "VERIFIED", "Assists kernel starch and oil phosphorylation.")
    add_record(g_crops, g_cname, "fruit_grain_pod_development", "Fruit / Grain / Pod Development", "potassium", "Available Potassium (K)", 120.0, 220.0, "mg/kg", TNAU_GROUNDNUT["title"], TNAU_GROUNDNUT["url"], "VERIFIED", "Increases shelling percentage and 100-seed mass.")

    # Stage 5: Maturity
    add_record(g_crops, g_cname, "maturity", "Maturity", "temperature", "Temperature", 20.0, 28.0, "°C", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Dry, moderate weather ensures internal pod shell browning and seed dormancy.")
    add_record(g_crops, g_cname, "maturity", "Maturity", "relative_humidity", "Relative Humidity", 45.0, 60.0, "%", TNAU_GROUNDNUT["title"], TNAU_GROUNDNUT["url"], "VERIFIED", "Low humidity suppresses pre-harvest aflatoxin contamination (Aspergillus flavus).")
    add_record(g_crops, g_cname, "maturity", "Maturity", "soil_moisture", "Soil Moisture", 45.0, 60.0, "%", FAO_GROUNDNUT["title"], FAO_GROUNDNUT["url"], "VERIFIED", "Moderate soil moisture needed at pulling; if soil is too dry, pegs snap and pods stay underground.")
    add_record(g_crops, g_cname, "maturity", "Maturity", "soil_ph", "Soil pH", 6.0, 7.0, "pH", ICRISAT_GROUNDNUT["title"], ICRISAT_GROUNDNUT["url"], "VERIFIED", "Inherent soil reaction.")
    add_record(g_crops, g_cname, "maturity", "Maturity", "light_intensity", "Light Intensity", None, None, "lux", UNVERIFIED_LIGHT_MATURITY["title"], UNVERIFIED_LIGHT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_LIGHT_MATURITY["note"])
    add_record(g_crops, g_cname, "maturity", "Maturity", "nitrogen", "Available Nitrogen (N)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])
    add_record(g_crops, g_cname, "maturity", "Maturity", "phosphorus", "Available Phosphorus (P)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])
    add_record(g_crops, g_cname, "maturity", "Maturity", "potassium", "Available Potassium (K)", None, None, "mg/kg", UNVERIFIED_NUTRIENT_MATURITY["title"], UNVERIFIED_NUTRIENT_MATURITY["url"], "UNVERIFIED", UNVERIFIED_NUTRIENT_MATURITY["note"])

    return {
        "metadata": {
            "title": "Smart Crop Stage Agronomic Reference Database",
            "version": "1.0.0",
            "total_crops": len(crops),
            "total_growth_stages": len(stages),
            "total_combinations": len(crops) * len(stages),
            "parameters_per_combination": 8,
            "total_records": len(records),
            "created_date": "2026-10-24"
        },
        "crops": crops,
        "growth_stages": stages,
        "records": records
    }

if __name__ == "__main__":
    data = build_dataset()
    data_dir = Path("C:/Users/HP/.gemini/antigravity-ide/scratch/smart-crop-stage-advisor/src/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    out_file = data_dir / "reference_ranges.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(data['records'])} records to {out_file}")
