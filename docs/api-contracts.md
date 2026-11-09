# Backend & Frontend API Contracts

This document formalizes the HTTP REST interface between the React SPA frontend and the FastAPI backend. Coding agents modifying endpoints, serialization schemas, or frontend clients should reference this document.

---

## 1. Base Configuration

- **Development Port**: `8000` (FastAPI backend), `5173` (Vite dev server).
- **Production Monolith**: Port `8000` serves both `/api/*` and SPA static assets.
- **Frontend Client**: [`frontend/src/api/client.js`](../frontend/src/api/client.js) adapts to `import.meta.env.VITE_API_BASE` or falls back to `/api` (production) and `http://localhost:8000/api` (development).

---

## 2. API Endpoints

### 2.1 Health Check
- **Endpoint**: `GET /api/health`
- **Controller**: [`backend/app/routers/health.py`](../backend/app/routers/health.py)
- **Response**: `200 OK`
```json
{
  "status": "ok"
}
```

---

### 2.2 List Analysis Cases
- **Endpoint**: `GET /api/cases`
- **Controller**: [`backend/app/routers/cases.py`](../backend/app/routers/cases.py)
- **Response**: `200 OK`
```json
[
  {
    "id": 1,
    "name": "Case 1 — Kochi Port Approaches (MSC Elsa III)",
    "description": "Bunker oil spill incident off Kochi port approach, Kerala (May 2025)..."
  },
  {
    "id": 2,
    "name": "Case 2 — Mumbai Port Approaches (JNPT / Mumbai High)",
    "description": "Crude oil bunker discharge detected along the primary crude tanker transit fairway..."
  }
]
```

---

### 2.3 Get Case Details
- **Endpoint**: `GET /api/cases/{case_id}`
- **Parameters**: `case_id: int`
- **Controller**: [`backend/app/routers/cases.py`](../backend/app/routers/cases.py)
- **Response**: `200 OK`
```json
{
  "id": 1,
  "name": "Case 1 — Kochi Port Approaches (MSC Elsa III)",
  "description": "Bunker oil spill incident...",
  "sar_image_path": "data/raw/sentinel1/case_1_scene.tif",
  "image_timestamp": "2025-05-25T08:30:00Z",
  "bbox": [75.40, 9.20, 76.50, 10.30]
}
```

---

### 2.4 Run Pipeline Execution
- **Endpoint**: `POST /api/cases/{case_id}/run`
- **Parameters**: `case_id: int`
- **Controller**: [`backend/app/routers/pipeline.py`](../backend/app/routers/pipeline.py) -> [`backend/app/pipeline/orchestrator.py`](../backend/app/pipeline/orchestrator.py)
- **Response**: `200 OK`
```json
{
  "case_metadata": {
    "name": "Case 1 — Kochi Port Approaches (MSC Elsa III)",
    "incident_ref": "ICG-MRCC-KCH-2025-0526-SD01",
    "port_of_detention": "Port of Cochin"
  },
  "detection": {
    "polygon_geojson": { "type": "Polygon", "coordinates": [...] },
    "confidence": 0.892,
    "inference_time_sec": 3.8,
    "shape_features": {
      "area_km2": 14.8,
      "perimeter_km": 18.2,
      "elongation": 2.6,
      "fragment_count": 1,
      "age_class": "fresh"
    },
    "satellite_metadata": {
      "platform": "Sentinel-1A C-Band SAR",
      "mode": "Interferometric Wide (IW) GRD",
      "polarization": "VV + VH Dual-Pol",
      "acquisition_time": "2025-05-25T08:30:00Z"
    }
  },
  "drift": {
    "origin_polygon_geojson": { "type": "Polygon", "coordinates": [...] },
    "estimated_origin_time": "2025-05-24T14:30:00Z",
    "origin_window_start": "2025-05-24T14:15:00Z",
    "origin_window_end": "2025-05-24T14:45:00Z",
    "uncertainty_radius_km": 4.8,
    "particle_count": 200,
    "particle_cloud_geojson": { "type": "FeatureCollection", "features": [...] },
    "particle_trajectories_geojson": { "type": "FeatureCollection", "features": [...] },
    "hydrodynamics": {
      "surface_current_mps": 0.58,
      "current_heading_deg": 215.0,
      "wind_speed_knots": 14.2,
      "wind_heading_deg": 230.0
    }
  },
  "vessels": [
    {
      "mmsi": "354892000",
      "vessel_name": "MSC ELSA III",
      "vessel_type": "cargo",
      "flag": "LR",
      "flag_name": "Liberia",
      "final_score": 0.942,
      "explanation": "Directly intersected backward Lagrangian drift cone; 42-min deliberate AIS transponder blackout...",
      "scores": {
        "proximity": 0.98,
        "parity": 0.91,
        "temporality": 1.0,
        "ais_gap": 0.70,
        "speed_anomaly": 1.0,
        "vessel_type_prior": 0.80
      },
      "track_geojson": { "type": "Feature", "geometry": { "type": "LineString", "coordinates": [...] } }
    }
  ],
  "nugen": {
    "multi_agent": { ... },
    "inference": { ... }
  },
  "dossier": { ... }
}
```

---

### 2.5 Generate Enforcement Dossier
- **Endpoint**: `POST /api/cases/{case_id}/dossier?mmsi={mmsi}`
- **Parameters**: `case_id: int` (path), `mmsi: Optional[str]` (query)
- **Controller**: [`backend/app/routers/pipeline.py`](../backend/app/routers/pipeline.py) -> [`backend/app/nugen/dossier_generator.py`](../backend/app/nugen/dossier_generator.py)
- **Response**: `200 OK`
```json
{
  "dossier_title": "STATUTORY MARITIME POLLUTION ENFORCEMENT DOSSIER",
  "issuing_authority": "Indian Coast Guard (ICG) — Maritime Rescue Coordination Centre (MRCC)",
  "case_summary": {
    "incident_name": "Case 1 — Kochi Port Approaches (MSC Elsa III)",
    "target_vessel_name": "MSC ELSA III",
    "target_mmsi": "354892000",
    "composite_attribution_confidence": "94.2%",
    "enforcement_order": "IMMEDIATE STATUTORY DETENTION AT PORT OF COCHIN"
  },
  "section_1_satellite_radar": { ... },
  "section_2_drift_physics": { ... },
  "section_3_vessel_behavioral_telemetry": { ... },
  "section_4_statutory_citations": [ ... ],
  "section_5_enforcement_orders": {
    "empowered_statute": "Indian Merchant Shipping Act 1958, Section 356J",
    "directives": [ ... ]
  }
}
```

---

### 2.6 Nugen Direct Inference
- **Endpoint**: `POST /api/nugen/inference`
- **Body**:
```json
{
  "model": "nugen-maritime-aligned-phi3",
  "domain": "indian_eez_enforcement",
  "slick_coords": [9.9312, 76.2673],
  "spill_timestamp": "2025-05-24T14:30:00Z",
  "suspect_vessel": {
    "mmsi": "354892000",
    "vessel_name": "MSC ELSA III",
    "ais_gap_duration_mins": 42,
    "speed_drop_knots": 6.8
  },
  "jurisdiction": "Merchant_Shipping_Act_1958"
}
```
- **Response**: `200 OK` with generated legal findings, citations, and detention orders.

---

### 2.7 Scientific Benchmarks
- **Endpoint**: `GET /api/nugen/benchmark`
- **Controller**: [`backend/app/routers/pipeline.py`](../backend/app/routers/pipeline.py) -> [`backend/app/nugen/benchmarks.py`](../backend/app/nugen/benchmarks.py)
- **Response**: `200 OK` containing side-by-side comparative metrics (Base Model vs. Nugen Aligned SLM).

---

### 2.8 National Case Studies

These endpoints serve the National Intelligence dashboard. The `/api/demo` path is retained for compatibility with existing clients; in the product interface these records are presented as case studies. National illustrative cases are isolated from `/api/cases` and never enter the live analysis pipeline.

#### List Case Studies
- **Endpoint**: `GET /api/demo/scenarios`
- **Controller**: [`backend/app/routers/demo.py`](../backend/app/routers/demo.py)
- **Response**: `200 OK`
```json
[
  {
    "id": "mumbai_high",
    "name": "Mumbai High",
    "summary": "Offshore crude oil field and tanker corridor west of Mumbai.",
    "region_id": "IN-MH",
    "region_name": "Maharashtra",
    "coast": "WEST",
    "primary_mrcc": "MRCC Mumbai",
    "stats": { "scenes": 2, "detections": 2, "vessels": 3, "incidents": 2 },
    "provenance": "SIMULATED_DEMO"
  }
]
```

#### Coastal Regions and Search Envelopes
- **Endpoint**: `GET /api/demo/regions`
- **Response**: `200 OK` with `count`, `states`, `union_territories`, and a `zones` array. Zone `boundary_status` is `PROVISIONAL_SEARCH_ENVELOPE`.

#### Full Case-Study Bundle
- **Endpoint**: `GET /api/demo/scenario/{scenario_id}`
- **Response**: `200 OK` with `scenario`, `stats`, `scenes`, `detections`, `vessels`, `drift`, and `incidents`. All illustrative records carry `provenance: "SIMULATED_DEMO"`.
- **Errors**: `404` for an unknown case study.

#### Reset Case Records
- **Endpoint**: `POST /api/demo/reset`
- **Behavior**: Transactionally reloads the five case-study fixtures into SQLite. Only rows previously created by the case-study seeder are removed; unrelated project cases are preserved.
- **Response**: `200 OK` with `scenarios_loaded`, per-record `totals`, database counts, and `provenance: "SIMULATED_DEMO"`.
- **Errors**: `422` for an invalid fixture; `500` for an unexpected refresh failure.
