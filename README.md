# Smart Crop Stage Advisor — Software MVP

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)]()

A local-first, modular agronomic decision-support system built with Python and Streamlit. The application evaluates field measurements—acquired via manual entry or local Wi-Fi telemetry—against scientifically validated agronomic reference ranges for **5 staple crops across 5 distinct developmental stages**, providing real-time physiological status classification and transparent guidance.

---

## 1. Project Overview

The **Smart Crop Stage Advisor** bridges the gap between field IoT telemetry and stage-aware agronomic science. Crop environmental and nutritional requirements change drastically as plants transition through developmental phases (e.g., water deficit during flowering causes irreversible blossom drop, whereas high moisture during ripening induces grain rot).

### Key Features
- **5 Supported Crops**: Maize, Tomato, Rice, Wheat, Groundnut.
- **5 Configurable Growth Stages**:
  1. Germination / Establishment
  2. Vegetative Growth
  3. Flowering / Reproductive
  4. Fruit / Grain / Pod Development
  5. Maturity
- **6 Single-Select Measurement Categories**:
  - Temperature (°C)
  - Humidity (% RH)
  - Soil Moisture (% volumetric water content)
  - pH (0–14 standard scale)
  - Light Intensity (lux)
  - NPK (Nitrogen, Phosphorus, Potassium in mg/kg evaluated together)
- **Scientific Reference Dataset**: 200 records across all 25 crop-stage combinations stored in transparent, editable JSON (`src/data/reference_ranges.json`).
- **Rigorous Agronomic Safety**:
  - Refuses to classify field measurements when reference ranges are unverified or missing (`REFERENCE UNAVAILABLE`).
  - Never prescribes fertilizer quantities or chemical treatments from environmental sensors alone.
  - Distinguishes measurement interpretation from fertilizer advice.
- **Hardware-Independent Architecture**:
  - Live Wi-Fi HTTP adapter with configurable timeouts, polling intervals, and fault recovery.
  - Dedicated, explicitly labeled **Mock Sensor mode** for hardware-free demonstration and automated testing.

---

## 2. Software Prerequisites

- **Operating System**: Windows 10/11 (or Linux/macOS)
- **Python**: Version 3.11 or higher (Python 3.14 compatible)
- **Git**: Installed and available in PATH (for version control)

---

## 3. Windows Setup & Installation

Open PowerShell or Windows Command Prompt and navigate to the project directory:

```powershell
cd C:\Users\HP\.gemini\antigravity-ide\scratch\smart-crop-stage-advisor
```

### Step 1: Create Virtual Environment
```powershell
python -m venv .venv
```

### Step 2: Activate Virtual Environment
In PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```
*Note: If PowerShell execution policy restricts scripts, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, or use `.\.venv\Scripts\activate.bat` in CMD.*

### Step 3: Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Running the Application

Launch the Streamlit web application:

```powershell
streamlit run app.py
```

The application will open in your default browser at:
`http://localhost:8501`

---

## 5. Running Automated Tests

Run the complete automated test suite using `pytest`:

```powershell
python -m pytest
```

To run with verbose output and test names:
```powershell
python -m pytest -v
```

---

## 6. User Workflow & Instructions

Follow this step-by-step workflow:

1. **Select Crop**: Choose exactly one crop from the sidebar (e.g., *Maize*).
2. **Select Growth Stage**: Choose the active physiological stage (e.g., *Flowering / Reproductive*).
3. **Select Measurement Category**: Choose exactly one category from the 6 options. If *NPK* is selected, the application automatically requests Nitrogen, Phosphorus, and Potassium simultaneously.
4. **Choose Input Mode**:
   - **Manual Entry**: Input your hand-held probe or laboratory soil report numbers.
   - **Live Sensor (Wi-Fi)**: Poll real field hardware via local network HTTP.
   - **Mock Sensor (Simulation)**: Generate deterministic synthetic readings for testing.
5. **Click Evaluate / Measure**: Click the prominent button to execute validation and comparison.
6. **Review Results**: View the active status (`WITHIN RANGE`, `BELOW RANGE`, `ABOVE RANGE`, `REFERENCE UNAVAILABLE`, or `INVALID MEASUREMENT`), target bounds, source provenance, and actionable guidance.
7. **Reset Form**: Click **🔄 Reset / New Measurement** in the sidebar or header to clear the state and begin a new measurement session.

---

## 7. Mock Sensor Mode

If physical microcontroller hardware is unavailable:
1. In the sidebar, select **Mock Sensor (Simulation)** under *4. Select Measurement Source*.
2. The UI displays an explicit amber warning banner confirming synthetic simulation mode.
3. Choose a scenario:
   - *Optimal / Within Reference Range*
   - *Stress Deficit / Below Reference Range*
   - *Stress Excess / Above Reference Range*
   - *Random Microclimate Fluctuation*
4. Click **🧪 Generate & Compare Mock Telemetry**.
5. All generated results are stamped with `source: Mock Sensor` and `is_live = False`.

---

## 8. Live Wi-Fi HTTP Sensor Configuration

### Environment Variables
Copy `.env.example` to `.env` (optional) or set environment variables:

```powershell
# In PowerShell:
$env:SENSOR_HTTP_ENDPOINT="http://192.168.1.100:8080/sensors"
$env:SENSOR_TIMEOUT_SECONDS="5.0"
$env:SENSOR_POLLING_INTERVAL_SECONDS="10.0"
```

### UI Configuration
You can also adjust the endpoint URL, timeout, and polling interval directly in the Streamlit UI in the **Live Sensor (Wi-Fi)** panel.

### Example Single-Measurement Sensor Payload
When polled via `GET`, the microcontroller should respond with `200 OK` and a JSON body:

```json
{
  "parameter": "temperature",
  "value": 28.4,
  "unit": "C",
  "timestamp": "2026-10-24T10:00:00Z"
}
```

### Example NPK Multi-Nutrient Payload
```json
{
  "parameter": "npk",
  "nitrogen": { "value": 175.0, "unit": "mg/kg" },
  "phosphorus": { "value": 22.0, "unit": "mg/kg" },
  "potassium": { "value": 180.0, "unit": "mg/kg" },
  "timestamp": "2026-10-24T10:00:00Z"
}
```

For full communication schemas and adaptation for HTTP POST push or MQTT brokers, refer to [`docs/sensor_protocol.md`](docs/sensor_protocol.md).

---

## 9. Hardware Assumptions and Limitations

1. **Hardware Independence**: The software does not presume a specific microcontroller (ESP32, ESP8266, Arduino) or invent a private network IP address. The address must be configured.
2. **Local Network Connectivity**: The microcontroller and the host running Streamlit must reside on the same local network subnet unless routed.
3. **No Fabricated Readings**: If network connection fails or times out, the application displays a clear diagnostic error and refuses to fabricate live readings.
4. **Soil Moisture Sensing Physics**: The app interprets soil moisture as volumetric water content (% VWC). If using electrical resistance sensors, calibration curves must be applied on the microcontroller.
5. **NPK Transducer Reliability**: Direct in-situ real-time NPK probes can be susceptible to salinity interference. Laboratory soil testing remains the agronomic gold standard for nutrient calibration.

---

## 10. Updating the Agronomic Reference Dataset

The reference dataset is decoupled from application code and stored in JSON:
[`src/data/reference_ranges.json`](src/data/reference_ranges.json).

### Record Structure
```json
{
  "record_id": "maize_flowering_temperature",
  "crop_id": "maize",
  "crop_name": "Maize",
  "stage_id": "flowering_reproductive",
  "stage_name": "Flowering / Reproductive",
  "parameter_id": "temperature",
  "parameter_name": "Temperature",
  "min_value": 24.0,
  "max_value": 30.0,
  "unit": "°C",
  "source_title": "FAO Crop Water Management: Maize (Zea mays)",
  "source_url": "https://www.fao.org/land-water/databases-and-software/crop-information/maize/en/",
  "validation_status": "VERIFIED",
  "notes": "Optimal anthesis and silking range; temperatures above 32°C desiccate silks and reduce pollen viability."
}
```

To update or verify an unverified record:
1. Open `src/data/reference_ranges.json`.
2. Locate the specific crop, stage, and parameter record.
3. Set `validation_status` to `"VERIFIED"`.
4. Provide numeric `min_value` and `max_value`.
5. Enter verified scientific literature title and documentation URL in `source_title` and `source_url`.
6. Run `python -m pytest tests/test_dataset.py` to confirm that the integrity audit passes.

---

## 11. Git Commands for Version Control

To commit and push changes:

```powershell
# Check status
git status

# Stage all project files
git add .

# Commit with a descriptive message
git commit -m "feat: complete Smart Crop Stage Advisor software MVP"

# Push to your remote repository (e.g. GitHub)
# git remote add origin https://github.com/<username>/smart-crop-stage-advisor.git
# git branch -M main
# git push -u origin main
```

---

## 12. Project Structure

```
smart-crop-stage-advisor/
    app.py                       # Main Streamlit web application
    requirements.txt             # Python dependencies
    README.md                    # Project documentation and guide
    .gitignore                   # Git ignore patterns
    .env.example                 # Environment configuration template
    src/
        __init__.py
        config.py                # Agronomic and hardware configurations
        models.py                # Domain data models and status enums
        ui/
            __init__.py
            selectors.py         # Crop, stage, category, and mode selectors
            measurement_form.py  # Manual, Live, and Mock input forms
        services/
            __init__.py
            measurement_service.py   # Measurement acquisition and orchestration
            comparison_service.py    # Inclusive boundary comparison engine
            recommendation_service.py # Agronomic guidance rule engine
        data/
            __init__.py
            dataset_loader.py    # Dataset validator and indexer
            reference_ranges.json # 200 reference records (25 crop-stage combinations)
        hardware/
            __init__.py
            sensor_interface.py  # Abstract base sensor contract
            http_receiver.py     # Configurable live Wi-Fi HTTP adapter
            mock_sensor.py       # Explicit synthetic mock simulator
    tests/
        conftest.py              # Pytest deterministic fixtures
        test_selection.py        # Selection and state clearing tests
        test_measurements.py     # Manual input, physical limits, and NPK tests
        test_comparison.py       # Boundary comparison and conversion tests
        test_sensor_interface.py # HTTP adapter, payloads, and mock tests
        test_dataset.py          # Dataset completeness and malformed record tests
    docs/
        architecture.md          # System architecture and data flow diagrams
        sensor_protocol.md       # Microcontroller telemetry communication protocol
```
