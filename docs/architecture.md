# Smart Crop Stage Advisor — System Architecture

## 1. Overview
The **Smart Crop Stage Advisor** is a modular, database-driven decision-support application built in Python and Streamlit. It compares user-entered or Wi-Fi-received agricultural sensor measurements against scientifically validated reference ranges for five staple crops across five distinct growth stages.

## 2. High-Level Architecture

```mermaid
graph TD
    UI[Streamlit User Interface (app.py)] --> Sel[UI Selectors (selectors.py)]
    UI --> Form[Measurement Form (measurement_form.py)]
    
    Sel --> MS[Measurement Service (measurement_service.py)]
    Form --> MS
    
    MS --> CS[Comparison Service (comparison_service.py)]
    MS --> RS[Recommendation Service (recommendation_service.py)]
    
    MS --> Live[HTTP Sensor Receiver (http_receiver.py)]
    MS --> Mock[Mock Sensor Simulator (mock_sensor.py)]
    
    Live -.-> HW[ESP32 / Arduino Wi-Fi Microcontroller]
    
    CS --> DL[Dataset Loader (dataset_loader.py)]
    DL --> DB[(reference_ranges.json)]
    DL --> VR[(validation_report.json)]
```

## 3. Core Modules

### A. Data Layer (`src/data/`)
- `reference_ranges.json`: The database containing all 200 records (5 crops × 5 growth stages × 8 parameters).
- `dataset_loader.py`: Indexes the database into primary and composite lookup maps `(crop_id, stage_id, parameter_id)`. Performs integrity audits, provenance checks, and produces validation reports.
- `validation_report.json`: Machine-readable summary of verified vs unverified ranges, integrity flags, and provenance sources.

### B. Domain Models (`src/models.py`)
- `ReferenceRangeRecord`: Data structure holding parameter thresholds, units, provenance, and validation flags.
- `ComparisonResult`: Rich outcome containing measured value, normalized value, reference thresholds, status enum, source link, and explanation.
- `ComparisonStatus`: Enum with five explicit outcomes:
  - `WITHIN RANGE`
  - `BELOW RANGE`
  - `ABOVE RANGE`
  - `REFERENCE UNAVAILABLE`
  - `INVALID MEASUREMENT`
- `SensorPayload`: Validated telemetry payload with device ID, timestamps, source type (`LIVE_HARDWARE` vs `MOCK_SIMULATION`), and readings dictionary.

### C. Services (`src/services/`)
- `comparison_service.py`: Shared comparison engine with inclusive boundary testing `(min <= x <= max)`, physical limit validation, and unit normalization (e.g., °F to °C, klux to lux, ppm to mg/kg).
- `measurement_service.py`: Orchestrates acquisition from manual input or sensor interfaces, delegates to the comparison engine, and attaches agronomic guidance.
- `recommendation_service.py`: Maps stage-specific stress or optimal status into actionable agricultural guidance (e.g., immediate reproductive irrigation, aeration, liming, split fertilization).

### D. Hardware Integration (`src/hardware/`)
- `sensor_interface.py`: Abstract base contract `SensorInterface`.
- `http_receiver.py`: Configurable HTTP adapter for live Wi-Fi microcontrollers. Implements timeout controls, network fault handling, and schema validation. Strictly flagged as `is_live = True`.
- `mock_sensor.py`: Synthetic data generator for test and demo environments without hardware. Strictly flagged as `is_live = False` and `source_type = "MOCK_SIMULATION"`.

### E. User Interface (`src/ui/` & `app.py`)
- `selectors.py`: Single crop, single stage, single category, and source mode selectors. Automatically clears stale comparison results upon any selection modification.
- `measurement_form.py`: Dynamic forms for Manual Entry (with unified NPK inputs), Live Wi-Fi connection, and Mock simulation.
- `app.py`: Streamlit dashboard with 4 tabs:
  1. Stage Advisor & Comparison Engine
  2. Reference Database Browser (searchable 200 records)
  3. Agronomic Validation & Provenance Report
  4. Hardware Protocol & REST API Documentation
