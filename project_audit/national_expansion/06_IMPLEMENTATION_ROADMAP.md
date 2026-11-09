# 06 — IMPLEMENTATION ROADMAP & SEQUENTIAL MILESTONES

**Status:** REVISED & EXPANDED  
**Revision Date:** November 8, 2026  
**Objective:** Seven-milestone operational roadmap to transition SAGAR-DRISHTI from a two-case prototype into a verified, nationwide surveillance platform.

---

## Roadmap Overview

```
Milestone 1 ──► Milestone 2 ──► Milestone 3 ──► Milestone 4 ──► Milestone 5 ──► Milestone 6 ──► Milestone 7
National Geo   Durable Data    Scheduled CDSE   Genuine SAR CV   Real CMEMS/AIS  Investigation  Operational
Foundation     & Provenance    Ingestion        Validation       Attribution     Intelligence   Readiness
```

---

## Milestone 1 — National Geographic Foundation

- **Objective**: Implement 11 Indian coastal surveillance sectors and configurable offshore zones across Western, Eastern, and Island sectors.
- **Dependencies**: None.
- **Files/Modules Changing**:
  - `backend/app/regions.py` (New module defining coastal baselines and bounding boxes).
  - `backend/app/routers/cases.py` (Add `/api/regions`).
  - `frontend/src/components/CaseSelector.jsx` (Refactor into National Sector Selector).
  - `frontend/src/components/MapView.jsx` (Add coastal baseline and offshore buffer rendering).
- **Deliverables**:
  - All 11 coastal sectors browsable on map with territorial sea (12 nm) and configurable offshore buffers (24, 50, 100 nm).
  - Preserved functionality of existing Kochi and Mumbai benchmark scenarios.
- **Acceptance Criteria**: Operator can toggle between all 11 Indian coastal states in the UI and see verified geographical boundaries without errors.
- **Tests Required**: Unit tests verifying bounding box calculations and sector coordinate integrity.
- **Estimated Complexity**: Low (3–4 days).
- **Potential Costs**: ₹0.
- **Decisions Requiring Approval**: Approval of authoritative baseline definitions.

---

## Milestone 2 — Persistent National Data Foundation

- **Objective**: Implement durable database persistence, eliminating `/tmp` ephemeral storage and adding strict data provenance tagging.
- **Dependencies**: Milestone 1.
- **Files/Modules Changing**:
  - `backend/app/models.py` (Add `SurveillanceZone`, `Observation`, `Incident`).
  - `backend/app/database.py` (Configure persistent SQLite on VPS or managed PostgreSQL).
  - `backend/app/routers/pipeline.py` (Persist detection and scoring results into DB).
  - `frontend/src/App.jsx` (Add provenance badge indicators).
- **Deliverables**:
  - Fully persistent database storing observation and incident records.
  - Strict provenance tagging (`LIVE_OBSERVATION`, `HISTORICAL_VERIFIED`, `SYNTHETIC_DEMO`).
- **Acceptance Criteria**: Database survives server restarts and instance recycling without data loss. Live incident statistics never count synthetic cases.
- **Tests Required**: Persistence survival test across restart; foreign key integrity tests.
- **Estimated Complexity**: Medium (4–5 days).
- **Potential Costs**: ₹0 (SQLite on VPS or Supabase free tier).
- **Decisions Requiring Approval**: Database technology choice (SQLite on VPS vs. Supabase PostgreSQL).

---

## Milestone 3 — Scheduled Satellite Discovery

- **Objective**: Build automated scheduled ingestion querying Copernicus CDSE OData API for newly available Sentinel-1 SAR observations.
- **Dependencies**: Milestone 2, Copernicus CDSE account.
- **Files/Modules Changing**:
  - `backend/app/ingestion/copernicus_client.py` (New CDSE OData API client).
  - `backend/scripts/poll_sentinel1.py` (Scheduled poller script).
  - `backend/app/routers/cases.py` (Add `/api/observations`).
  - `frontend/src/components/MapView.jsx` (Render satellite swath footprint polygons).
- **Deliverables**:
  - Scheduled background worker polling CDSE every 6–12 hours for Sentinel-1 Level-1 GRD acquisitions over the 11 coastal sectors.
  - Observation catalog populated in database.
- **Acceptance Criteria**: System automatically registers new satellite observation footprints over India within 6 hours of availability on Copernicus.
- **Tests Required**: Mock and live CDSE OData API search tests; footprint geometry parsing tests.
- **Estimated Complexity**: Medium (5–6 days).
- **Potential Costs**: ₹0 (Free CDSE open-access account).
- **Decisions Requiring Approval**: Polling frequency and worker execution environment (VPS cron vs. GitHub Actions).

---

## Milestone 4 — Genuine SAR Detection & Scientific Validation

- **Objective**: Establish real SAR image preprocessing, obtain or train verified U-Net model weights, and validate detection metrics on ground-truth scenes.
- **Dependencies**: Milestone 3, Kaggle Deep-SAR dataset or trained weights.
- **Files/Modules Changing**:
  - `backend/app/ml/preprocess.py` (Radiometric calibration, Lee speckle filtering, decibel thresholding).
  - `backend/app/ml/model_utils.py` (Load validated weights `unet_resnet34_oilspill.pth`).
  - `backend/app/ml/infer.py` (Real inference pipeline replacing mock fallback).
  - `backend/tests/test_detection.py` (Ground-truth validation benchmarks).
- **Deliverables**:
  - Operational U-Net model executing real pixel-level inference on Sentinel-1 GeoTIFF patches.
  - Formally documented scientific validation report with verified IoU, precision, recall, and false-positive rates.
- **Acceptance Criteria**: Model accurately segments verified oil spill patches from real Sentinel-1 imagery without falling back to mock polygons.
- **Tests Required**: IoU benchmark validation test against 15+ labeled Kaggle SAR test patches.
- **Estimated Complexity**: High (8–10 days).
- **Potential Costs**: ₹0 to ₹1,500 (if GPU compute is rented for model training, otherwise ₹0 on free Google Colab/Kaggle GPU).
- **Decisions Requiring Approval**: Decision whether to train weights in-house or source validated public weights.

---

## Milestone 5 — Environmental & Vessel Attribution

- **Objective**: Connect real-world CMEMS surface currents, ERA5 winds, and Global Fishing Watch AIS API for arbitrary bounding boxes.
- **Dependencies**: Milestone 4, CMEMS and GFW API credentials.
- **Files/Modules Changing**:
  - `backend/app/physics/environmental_data.py` (Live CMEMS current and ERA5 wind retrieval).
  - `backend/app/physics/drift_model.py` (Dynamic spatial-temporal environmental interpolation).
  - `backend/app/scoring/ais_client.py` (Live GFW API query activation).
  - `backend/app/scoring/scorer.py` (Dynamic vessel candidate ranking).
- **Deliverables**:
  - Environmentally driven backward Lagrangian advection using actual ocean current and wind vectors.
  - Live candidate vessel extraction from GFW AIS within the spill window.
- **Acceptance Criteria**: System backtracks real ocean currents and identifies actual AIS vessels transiting the spill origin cone.
- **Tests Required**: Hydrodynamic particle integration tests; GFW query rate-limiting tests.
- **Estimated Complexity**: High (8–10 days).
- **Potential Costs**: ₹0 (Free CMEMS and GFW developer accounts).
- **Decisions Requiring Approval**: GFW API key activation and rate-limit quotas.

---

## Milestone 6 — National Investigation & Intelligence

- **Objective**: Complete the national incident triage workflow and generate investigative draft legal dossiers citing jurisdiction-specific ports.
- **Dependencies**: Milestone 5.
- **Files/Modules Changing**:
  - `frontend/src/components/SuspectList.jsx` (Add multi-incident triage view).
  - `backend/app/nugen/dossier_generator.py` (Port-specific jurisdiction detention directives).
  - `frontend/src/components/LegalDossierModal.jsx` (Add 'INVESTIGATIVE DRAFT' watermark and officer sign-off fields).
- **Deliverables**:
  - Central incident registry with severity grading (Tier-1, Tier-2, Tier-3) and status tracking (`INVESTIGATING`, `VERIFIED`, `CLOSED`).
  - Investigative draft dossiers customized for local ports (Paradip, JNPT, Cochin, Port Blair).
- **Acceptance Criteria**: Operator can manage multiple nationwide incidents and export formal Section 356J briefs.
- **Tests Required**: Dossier generation unit tests across multiple port jurisdictions.
- **Estimated Complexity**: Medium (4–5 days).
- **Potential Costs**: ₹0.
- **Decisions Requiring Approval**: Formal approval of investigative legal wording.

---

## Milestone 7 — Operational Readiness

- **Objective**: Hardening, security audit, monitoring, automated backups, and production deployment on low-cost infrastructure.
- **Dependencies**: Milestones 1–6.
- **Files/Modules Changing**:
  - Deployment configuration (VPS setup / Dockerfile).
  - Database backup scripts (Daily automated SQLite/PostgreSQL snapshots).
  - Automated integration test suite across all 11 sectors.
- **Deliverables**:
  - Hardened, 24/7 operational surveillance platform deployed within a low-cost budget (< ₹450/month).
  - Complete operational documentation and monitoring dashboard.
- **Acceptance Criteria**: System operates autonomously for 7 days without crashes, unhandled errors, or database corruption.
- **Tests Required**: Load testing, failover testing, automated daily snapshot recovery verification.
- **Estimated Complexity**: Medium (5–6 days).
- **Potential Costs**: ₹350–₹450 / month (VPS hosting).
- **Decisions Requiring Approval**: Final production VPS provider selection.
