# 05 — API & INTEGRATION DESIGN

**Status:** REVISED & EXPANDED  
**Revision Date:** November 8, 2026  
**Scope:** Specification of existing REST endpoints, nationwide multi-region endpoints, provenance filtering, and error handling contracts.

---

## 1. Existing Endpoints (Preserved for Backward Compatibility)

All current endpoints remain active and continue serving the existing dashboard:

| Endpoint | Method | Status | Purpose |
| :--- | :--- | :--- | :--- |
| `/api/health` | `GET` | Active | Liveness and health probe. |
| `/api/cases` | `GET` | Active | Returns list of benchmark demo cases. |
| `/api/cases/{case_id}` | `GET` | Active | Returns specific benchmark case details. |
| `/api/cases/{case_id}/run` | `POST` | Active | Executes end-to-end detection, drift, AIS scoring, and Nugen dossier. |
| `/api/cases/{case_id}/dossier` | `POST` | Active | Exports formal court-ready legal brief for a suspect vessel. |
| `/api/nugen/inference` | `POST` | Active | Direct inference against Nugen domain-aligned maritime legal SLM. |
| `/api/nugen/benchmark` | `GET` | Active | Retrieves scientific validation metrics (Base vs Nugen SLM). |

---

## 2. Nationwide Endpoints Specification

### 2.1 Regional Surveillance Sectors
- **`GET /api/regions`**
  - **Description**: Returns all 11 monitored coastal zones across Western, Eastern, and Island sectors.
  - **Query Parameters**: `coast: Optional[str]` (`WEST`, `EAST`, `ISLANDS`).
  - **Response Payload**:
    ```json
    [
      {
        "id": "IN-MH",
        "name": "Maharashtra (Mumbai / JNPT)",
        "coast": "WEST",
        "active_incidents": 2,
        "monitoring_status": "SCHEDULED_ACTIVE",
        "last_pass_time": "2026-11-08T02:15:00Z",
        "territorial_sea_nm": 12,
        "offshore_buffer_nm": 50,
        "bbox": [72.10, 18.20, 73.10, 19.30]
      }
    ]
    ```

### 2.2 Satellite Observations Catalog
- **`GET /api/observations`**
  - **Query Parameters**: 
    - `zone_id: Optional[str]`
    - `provenance: Optional[str]` (Default: excludes `SYNTHETIC_DEMO`)
    - `status: Optional[str]` (`DISCOVERED`, `DOWNLOADED`, `PROCESSED`, `NO_SLICK`)
    - `limit: int = 50`
  - **Response Payload**:
    ```json
    [
      {
        "id": "S1A_IW_GRDH_1SDV_20261108T021512",
        "zone_id": "IN-MH",
        "satellite": "Sentinel-1A",
        "acquisition_time": "2026-11-08T02:15:12Z",
        "polarization": "VV+VH",
        "status": "PROCESSED",
        "provenance": "LIVE_OBSERVATION",
        "slick_detected": true,
        "footprint_geojson": { "type": "Polygon", "coordinates": [...] }
      }
    ]
    ```

### 2.3 Central Incident Registry
- **`GET /api/incidents`**
  - **Query Parameters**:
    - `zone_id: Optional[str]`
    - `provenance: Optional[str]` (Default: `LIVE_OBSERVATION,HISTORICAL_VERIFIED`)
    - `status: Optional[str]` (`CANDIDATE`, `INVESTIGATING`, `VERIFIED`, `CLOSED`)
    - `severity: Optional[str]` (`TIER_1`, `TIER_2`, `TIER_3`)
  - **Response Payload**:
    ```json
    [
      {
        "id": 104,
        "observation_id": "S1A_IW_GRDH_1SDV_20261108T021512",
        "zone_id": "IN-MH",
        "title": "Mumbai High Offshore Fairway Discharge",
        "detected_at": "2026-11-08T02:15:12Z",
        "severity": "TIER_2",
        "status": "INVESTIGATING",
        "provenance": "LIVE_OBSERVATION",
        "slick_area_km2": 18.4,
        "primary_suspect": {
          "mmsi": "538009871",
          "vessel_name": "MT ARABIAN GLORY",
          "composite_score": 0.892,
          "attribution_confidence": "89.2%"
        }
      }
    ]
    ```

### 2.4 Incident Detail & Attribution Analysis
- **`GET /api/incidents/{incident_id}`**
  - **Response**: Full incident telemetry, including GeoJSON slick geometry, Lagrangian backward retro-advection trajectory, 6-factor suspect scoreboard, and frozen investigative draft legal brief.

---

## 3. Provenance & Security Enforcement

1. **Header-Based Provenance Separation**:
   - Live endpoints automatically filter out synthetic data unless the query parameter `include_synthetic=true` is explicitly provided.
   - The UI displays an amber badge (`[SYNTHETIC BENCHMARK CASE]`) whenever non-live data is viewed.
2. **Standardized Error Handling**:
   - `404 Not Found`: Standardized JSON detailing missing entities.
   - `422 Unprocessable Entity`: Detailed Pydantic validation error lists.
   - `503 Service Unavailable`: Triggered when an external service (CDSE or GFW) is down, including a `retry_after_sec` header.
