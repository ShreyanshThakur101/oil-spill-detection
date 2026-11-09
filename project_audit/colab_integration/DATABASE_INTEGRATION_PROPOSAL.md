# Colab Ingestion Router: Database Integration & Persistence Proposal

**Target Application:** SAGAR-DRISHTI  
**Router Status:** Preparation Only (Not Registered in `backend/app/main.py`)  
**Proposed Endpoint:** `POST /api/colab/results`  
**Purpose:** Technical proposal mapping incoming Google Colab detection payloads to persistent database records while preventing duplicate submissions, enforcing bearer token security, and segregating unverified candidate detections from confirmed incidents.

---

## 1. Existing Database Model Inspection

The existing database schema in [`backend/app/models.py`](../../backend/app/models.py) defines:
1. `Case`: Static benchmark demo scenarios (`id`, `name`, `description`, `sar_image_path`, `image_timestamp`, `bbox`).
2. `SlickDetection`: Detected slick geometry (`id`, `case_id`, `polygon_geojson`, `confidence`, `area_km2`, `perimeter_km`, `elongation`, `fragment_count`, `age_class`).
3. `DriftResult`: Hydrodynamic backtracking outputs (`id`, `case_id`, `detection_id`, `origin_polygon_geojson`, `estimated_origin_time`, `uncertainty_radius_km`).
4. `VesselScore`: AIS vessel attribution results (`id`, `case_id`, `mmsi`, `vessel_name`, `vessel_type`, `track_geojson`, `scores_json`, `final_score`, `explanation`).

### Current Gap
There are no tables for:
- Tracking individual satellite observation passes (`observations`).
- Recording external compute worker jobs (`colab_jobs`).
- Storing incident lifecycle states (`CANDIDATE`, `INVESTIGATING`, `VERIFIED`, `CLOSED`).

---

## 2. Proposed Database Schema Evolution

To integrate Colab results durably without disrupting existing demo cases, the following database models are proposed:

```
┌──────────────────────────────────────────────┐
│                  colab_jobs                  │
├──────────────────────────────────────────────┤
│ id: VARCHAR(64) [PK]                         │ ◄─── Unique Colab Job ID (e.g. "JOB-20261108-MH01")
│ status: VARCHAR(32)                          │ ◄─── "SUBMITTED", "VALIDATED", "FAILED"
│ worker_id: VARCHAR(64)                       │ ◄─── e.g. "Google_Colab_T4_Instance"
│ submitted_at: DATETIME                       │
│ payload_json: JSON                           │ ◄─── Full raw JSON audit trail
└──────────────────────┬───────────────────────┘
                       │ 1:1
┌──────────────────────▼───────────────────────┐
│               slick_detections               │
├──────────────────────────────────────────────┤
│ id: INTEGER [PK, Auto]                       │
│ job_id: VARCHAR(64) [FK -> colab_jobs.id]    │ ◄─── Link to worker execution
│ case_id: INTEGER [Nullable FK -> cases.id]   │ ◄─── Null for live satellite passes
│ product_id: VARCHAR(64) [Indexed]            │ ◄─── Sentinel-1 Product ID
│ zone_id: VARCHAR(16)                         │ ◄─── "IN-MH", "IN-GJ", etc.
│ polygon_geojson: JSON                        │ ◄─── Verified WGS84 GeoJSON polygon
│ confidence: FLOAT                            │ ◄─── U-Net IoU / sigmoid confidence
│ area_km2: FLOAT                              │ ◄─── Metric equal-area projected km²
│ perimeter_km: FLOAT                          │
│ elongation: FLOAT                            │
│ fragment_count: INTEGER                      │
│ verification_status: VARCHAR(32)             │ ◄─── "UNVERIFIED_CANDIDATE", "CONFIRMED_SPILL", "FALSE_POSITIVE"
│ provenance: VARCHAR(32)                      │ ◄─── "LIVE_OBSERVATION", "SYNTHETIC_DEMO"
│ created_at: DATETIME                         │
└──────────────────────────────────────────────┘
```

---

## 3. Prevention of Duplicate Submissions & Replay Attacks

1. **Unique Primary Key on `job_id`**:
   - `colab_jobs.id` serves as a unique constraint. If a Colab cell re-runs and submits the same `job_id`, the database raises an `IntegrityError`, and the API returns `409 Conflict: Job ID already processed`.
2. **Product ID Idempotency**:
   - For automated batch runs, the combination of `(product_id, model_version)` is checked. If an observation has already been processed with the current model version, the router can optionally return the existing detection record or flag a re-analysis.

---

## 4. Authentication & Secret Management

1. **Bearer Token Authentication**:
   - The Colab notebook sends: `Authorization: Bearer <COLAB_SECRET_TOKEN>`.
   - The router validates this against `os.environ.get("COLAB_SECRET_TOKEN")`.
2. **Security Hardening**:
   - The default fallback token (`"sagar-drishti-colab-prototype-2026"`) will be disabled in production. If `COLAB_SECRET_TOKEN` is unset in a live environment, the endpoint will raise `503 Service Unavailable` with a log warning, preventing unauthorized submissions.

---

## 5. Strict Separation: Candidate Detections vs. Confirmed Incidents

To prevent model false-positives (e.g., natural biogenic algae slicks, low-wind calm sea surfaces) from contaminating official Coast Guard enforcement logs:

1. **Default State: `UNVERIFIED_CANDIDATE`**:
   - All Colab detections enter the database tagged as `verification_status = "UNVERIFIED_CANDIDATE"`.
2. **Separate Dashboard Triage View**:
   - In the React frontend, unverified candidates appear in a distinct **"Candidate Radar Detections"** triage queue with amber badges.
   - They do not appear in the official Indian Coast Guard Section 356J active detention registry until an operator clicks **"Verify Detection"** or hydrodynamic backtracking confirms high candidate vessel correlation ($>0.80$).
3. **Audit Trail**:
   - The database records the operator ID, timestamp, and verification rationale when transitioning from `UNVERIFIED_CANDIDATE` to `CONFIRMED_SPILL`.

---

## 6. Implementation Sequence (Awaiting Approval)

Once approved, the implementation proceeds in two safe steps:
1. **Step A**: Add `ColabJob` model and expand `SlickDetection` fields in `backend/app/models.py`.
2. **Step B**: Update `backend/app/routers/colab.py` with SQLAlchemy session handling (`db.add(...)`), and register `app.include_router(colab.router, prefix="/api")` in `backend/app/main.py`.
