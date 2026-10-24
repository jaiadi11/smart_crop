# Wi-Fi Sensor Telemetry Protocol Specification

## 1. Overview
This document specifies the communication contract, data payloads, unit conventions, and networking assumptions between the **Smart Crop Stage Advisor** application and on-field Wi-Fi microcontroller telemetry nodes (such as ESP32, ESP8266, Arduino Nano RP2040 Connect, or Raspberry Pi Pico W).

---

## 2. HTTP Pull Architecture (Default Client Protocol)

In the default configuration, the application acts as an HTTP client that periodically polls an HTTP endpoint hosted on the field microcontroller node.

### A. Polling Request
- **Method**: `GET`
- **Default Endpoint**: `http://192.168.1.100:8080/sensors` (configurable via `SENSOR_HTTP_ENDPOINT` env var or in the UI)
- **Timeout**: Configurable, default `5.0` seconds
- **Polling Interval**: Configurable, default `10.0` seconds
- **Headers**:
  ```http
  Accept: application/json
  User-Agent: SmartCropStageAdvisor/1.0
  ```

---

## 3. Payload Contracts

The application supports two primary payload formats:

### Format 1: Single-Measurement Payload Contract
Used by single-parameter sensor probes (e.g., ambient DHT22, DS18B20, capacitive soil moisture sensor, BH1750 lux meter).

```json
{
  "parameter": "temperature",
  "value": 28.4,
  "unit": "C",
  "timestamp": "2026-10-24T10:00:00Z",
  "device_id": "ESP32-FIELD-NODE-01"
}
```

#### Field Definitions
| Field | Type | Required | Description |
|---|---|---|---|
| `parameter` | String | Yes | Canonical parameter identifier or alias (e.g., `temperature`, `temp`, `humidity`, `rh`, `soil_moisture`, `soil_ph`, `ph`, `light_intensity`, `lux`). |
| `value` | Number | Yes | Numeric reading. Must be a finite number within plausible physical limits. |
| `unit` | String | Yes | Declared unit (e.g., `°C`, `C`, `%`, `%RH`, `pH`, `lux`). |
| `timestamp` | String | Optional | ISO-8601 UTC timestamp of measurement acquisition. |
| `device_id` | String | Optional | Unique hardware device identifier. |

---

### Format 2: NPK Composite Payload Contract
NPK represents a single multi-nutrient measurement category consisting of Nitrogen, Phosphorus, and Potassium. All three nutrients must be reported in one response.

```json
{
  "parameter": "npk",
  "device_id": "SOIL-OPTICAL-NPK-01",
  "timestamp": "2026-10-24T10:00:00Z",
  "nitrogen": {
    "value": 175.0,
    "unit": "mg/kg"
  },
  "phosphorus": {
    "value": 22.0,
    "unit": "mg/kg"
  },
  "potassium": {
    "value": 180.0,
    "unit": "mg/kg"
  }
}
```

*Alternative flat format also accepted:*
```json
{
  "parameter": "npk",
  "device_id": "SOIL-OPTICAL-NPK-01",
  "timestamp": "2026-10-24T10:00:00Z",
  "nitrogen": 175.0,
  "phosphorus": 22.0,
  "potassium": 180.0,
  "unit": "mg/kg"
}
```

---

### Format 3: Multi-Reading Node Payload Contract
For all-in-one integrated weather/soil field stations transmitting all parameters in a single dictionary:

```json
{
  "device_id": "ESP32-ALL-IN-ONE-NODE",
  "timestamp": "2026-10-24T12:00:00Z",
  "readings": {
    "temperature": { "value": 24.5, "unit": "°C" },
    "relative_humidity": { "value": 65.0, "unit": "%" },
    "soil_moisture": { "value": 72.0, "unit": "%" },
    "soil_ph": { "value": 6.4, "unit": "pH" },
    "light_intensity": { "value": 35000, "unit": "lux" },
    "nitrogen": { "value": 175.0, "unit": "mg/kg" },
    "phosphorus": { "value": 22.0, "unit": "mg/kg" },
    "potassium": { "value": 180.0, "unit": "mg/kg" }
  }
}
```

---

## 4. Parameter and Unit Conventions

The application validates measurement units strictly and prevents silent unit corruption:

| Parameter ID | Standard Unit | Supported / Compatible Units | Normalization Assumption | Physical Validity Range |
|---|---|---|---|---|
| `temperature` | `°C` | `°C`, `degC`, `C`, `°F`, `F` | `T(°C) = (T(°F) - 32) * 5/9` | `-50.0°C` to `80.0°C` |
| `relative_humidity` | `%` | `%`, `%RH`, `percent` | 1:1 | `0.0%` to `100.0%` |
| `soil_moisture` | `%` | `%`, `%VWC`, `percent` | % volumetric water content | `0.0%` to `100.0%` |
| `soil_ph` | `pH` | `pH` | Standard 0–14 scale | `0.0` to `14.0` |
| `light_intensity` | `lux` | `lux`, `lx`, `klux` | `1 klux = 1,000 lux` | `0.0` to `200,000 lux` |
| `nitrogen` | `mg/kg` | `mg/kg`, `ppm`, `kg/ha` | `1 ppm = 1 mg/kg`; `1 mg/kg ≈ 2 kg/ha` (furrow slice) | `>= 0.0 mg/kg` |
| `phosphorus` | `mg/kg` | `mg/kg`, `ppm`, `kg/ha` | `1 ppm = 1 mg/kg`; `1 mg/kg ≈ 2 kg/ha` | `>= 0.0 mg/kg` |
| `potassium` | `mg/kg` | `mg/kg`, `ppm`, `kg/ha` | `1 ppm = 1 mg/kg`; `1 mg/kg ≈ 2 kg/ha` | `>= 0.0 mg/kg` |

> [!WARNING]
> Incompatible units (e.g. pressure units `psi`, electrical units `mV`, or cross-parameter mismatches like `lux` for temperature) are strictly rejected with `INVALID MEASUREMENT` status.

---

## 5. Alternative Protocol Adaptation Guide

### A. HTTP POST (Push Webhook Architecture)
In battery-constrained field deployments where microcontrollers sleep to conserve power, the microcontroller wakes up periodically and pushes telemetry via HTTP `POST /telemetry`.

**How to Adapt:**
1. Stand up a lightweight HTTP receiver (using Python FastAPI or Flask).
2. Direct microcontrollers to `POST http://<gateway-ip>:<port>/telemetry`.
3. Pass the incoming JSON body directly to `HttpSensorReceiver.validate_payload(request_json)`.
4. Store the validated payload in a shared memory buffer or SQLite cache for Streamlit to read.

### B. MQTT Broker (Publish / Subscribe)
For distributed farm networks with low bandwidth:
1. Microcontrollers publish telemetry to topic `farm/field-01/sensors`.
2. A lightweight Python script runs in the background using `paho-mqtt`.
3. Upon receiving a message, it parses the JSON and invokes `validate_payload(json_data)`.
4. Cache the latest valid telemetry object for the UI.

---

## 6. Information Still Required from Hardware Vendor

To transition from the software MVP to full on-field production hardware integration, the following physical hardware specifications must be verified:

1. **Microcontroller Model & Operating Mode**:
   - Exact chip model (e.g., ESP32-S3, ESP8266 ESP-12F, Raspberry Pi Pico W).
   - Deep sleep schedule and wake-up duration.
2. **Local Network Addressing**:
   - Static IP assignment vs DHCP reservation vs mDNS hostname (e.g. `crop-sensor.local`).
   - Wi-Fi authentication standard (WPA2-PSK vs Enterprise).
3. **Sensor Calibration & Transducer Types**:
   - Soil moisture transducer physics: Capacitive frequency vs FDR vs TDR vs electrical resistance.
   - Soil pH probe: Glass electrode calibration buffers (pH 4.01, 7.00, 9.21) and temperature compensation (ATC).
   - NPK measurement method: Commercial RS485 Modbus optical probe vs electrochemical ISFET vs wet chemistry laboratory test.
4. **Data Transmission Security**:
   - Whether local HTTP is sufficient or TLS (`https://`) / API token authentication is required on the local subnet.
