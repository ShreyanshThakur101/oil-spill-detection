# 01 — CURRENT SYSTEM ASSESSMENT

**Status:** REVISED & EXPANDED  
**Revision Date:** November 8, 2026  
**System Evaluated:** SAGAR-DRISHTI (Oil Spill Detection & Vessel Attribution Platform)  
**Deployed Target:** [sagar-drishti-indol.vercel.app](https://sagar-drishti-indol.vercel.app)  
**Repository Branch/Commit:** `main` (`c88c574`)

---

## 1. Executive Summary

This assessment presents an evidence-based comparison between documented hackathon project claims and the **actual implemented source code and runtime behavior** of the SAGAR-DRISHTI codebase.

The current application is a functional, single-instance demonstration prototype created for the PCCOE International Grand Challenge 2026. It features an interactive React 18 Leaflet SPA, a FastAPI backend, an SQLite database seeded on startup, and deterministic attribution pipelines for two pre-configured Indian coastal scenarios (Case 1: Kochi Port Approaches / MSC Elsa III; Case 2: Mumbai Port Approaches / JNPT).

However, **the application is not yet a nationwide surveillance engine**. Critical scientific processing stages (SAR CNN inference, OpenDrift hydrodynamic backtracking, GFW AIS querying, and Nugen SLM inference) currently operate via **cached demonstration datasets, deterministic Python simulation models, and local domain-aligned fallback engines**.

---

## 2. Component-by-Component Reality Matrix

| Component | Documented / Presentation Claim | Actual Implementation Status | Evidence / Source Code | Classification |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend UI / Dashboard** | React SPA with Leaflet maps, 6-factor suspect board, multi-agent modals, economics panel, and court dossier viewer. | **Fully Implemented & Operational**. Tested on local and deployed Vercel instance (`sagar-drishti-indol.vercel.app`). Renders map layers, polylines, popups, and interactive modals. | [`frontend/src/App.jsx`](../../frontend/src/App.jsx), [`frontend/src/components/`](../../frontend/src/components/) | **VERIFIED** |
| **Backend REST API** | FastAPI backend serving `/api/cases`, `/api/cases/:id/run`, `/api/cases/:id/dossier`, `/api/nugen/*`. | **Fully Implemented & Operational**. Lifespan event seeds SQLite from disk; serves JSON payloads reliably on local and Vercel serverless. | [`backend/app/main.py`](../../backend/app/main.py), [`backend/app/routers/`](../../backend/app/routers/) | **VERIFIED** |
| **Database & Persistence** | SQLite database with `cases`, `slick_detections`, `drift_results`, `vessel_scores`. | **Partially Implemented**. DB tables exist, but `pipeline/seed.py` only writes to `cases`. Pipeline results are returned transiently as in-memory JSON rather than stored in `slick_detections` or `vessel_scores`. On Vercel, DB is ephemeral in `/tmp`. | [`backend/app/models.py`](../../backend/app/models.py), [`backend/app/pipeline/seed.py`](../../backend/app/pipeline/seed.py), [`api/index.py`](../../api/index.py) | **PARTIALLY VERIFIED** |
| **SAR Image Acquisition** | Automated ingestion of Copernicus Sentinel-1 SAR GRD scenes. | **Not Implemented**. No automated download client or catalog poller. SAR GeoTIFF paths in `case.json` (`case_1_scene.tif`) do not exist on disk. | [`backend/data/demo_cases/case_1/case.json`](../../backend/data/demo_cases/case_1/case.json) | **NOT IMPLEMENTED** |
| **SAR Dark Patch CV (U-Net)** | PyTorch U-Net (ResNet-34) trained on Kaggle Deep-SAR dataset achieving 89.2% IoU in <5s. | **Code Implemented, Weights Missing, Fallback Active**. `backend/app/ml/` contains complete PyTorch dataset loader, U-Net architecture, training CLI, and inference functions. However, no `.pth` weights exist on disk (`models/README.md` lists weights as `TBD`). Runtime gracefully falls back to deterministic polygon coordinates in `orchestrator.py`. | [`backend/app/ml/infer.py`](../../backend/app/ml/infer.py), [`backend/app/pipeline/orchestrator.py:100-125`](../../backend/app/pipeline/orchestrator.py#L100-L125) | **MOCKED / SIMULATED** |
| **Backward Lagrangian Drift (Physics)** | OpenDrift engine retro-tracking 200 particles 18h back using real CMEMS currents and ERA5 winds. | **Mathematical Model Simulated in Python**. `drift_model.py` seeds 200 particles and integrates backward across 6 discrete steps using regional monsoon drift equations in pure NumPy/Shapely. It does not call OpenDrift in production runtime because NetCDF files (`case_1_currents.nc`, `case_1_wind.nc`) do not exist in `data/raw/environmental/`. | [`backend/app/physics/drift_model.py:40-165`](../../backend/app/physics/drift_model.py#L40-L165), [`backend/app/physics/environmental_data.py`](../../backend/app/physics/environmental_data.py) | **MOCKED / SIMULATED** |
| **AIS Telemetry & Blackouts** | Real Global Fishing Watch (GFW) API queries intersecting 34 transiting candidates. | **Cached Telemetry from Disk**. `ais_client.py` has GFW API query functions, but `GFW_API_KEY` is empty by default. In practice, `load_cached_response()` loads pre-crafted vessel tracks and blackout gaps from `ais_cache_positions.json` and `ais_cache_gaps.json`. | [`backend/app/scoring/ais_client.py:27-35`](../../backend/app/scoring/ais_client.py#L27-L35), [`backend/data/demo_cases/case_1/ais_cache_positions.json`](../../backend/data/demo_cases/case_1/ais_cache_positions.json) | **MOCKED / SIMULATED** |
| **6-Factor Vessel Scoring** | Mathematical evaluation: Proximity, Parity, Temporality, Blackout, Speed Anomaly, Prior. | **Fully Implemented**. Pure Python algorithmic scoring using Shapely and Haversine geometry. Correctly computes weighted scores and generates statutory explanations. | [`backend/app/scoring/features.py`](../../backend/app/scoring/features.py), [`backend/app/scoring/scorer.py`](../../backend/app/scoring/scorer.py) | **VERIFIED** |
| **Nugen Domain-Aligned SLM** | Serverless fine-tuned maritime SLM hosted at `docs.nugen.in/inference`. | **Local Fallback Active**. HTTP POST to `https://docs.nugen.in/inference` returns `404 Not Found` (Mintlify documentation host). The codebase anticipates this via a high-fidelity local domain-aligned generation function in `backend/app/nugen/client.py`. | [`backend/app/nugen/client.py:50-100`](../../backend/app/nugen/client.py#L50-L100), Terminal test of `docs.nugen.in` | **MOCKED / SIMULATED** |
| **Multi-Agent Coordination** | 3 specialized sub-agents: Radar Parser, Physics Validator, Dossier Agent. | **Rule-Based Python Implementation**. Implemented as 3 Python classes in `backend/app/nugen/multi_agent.py` that validate telemetry thresholds and construct audit logs. | [`backend/app/nugen/multi_agent.py`](../../backend/app/nugen/multi_agent.py) | **VERIFIED** |
| **Legal Dossier Generation** | Court-ready ICG maritime enforcement dossier citing MARPOL Annex I & MSA 1958 §356J. | **Fully Implemented**. Assembles structured 5-section legal brief with specific detention directives and audit trails. | [`backend/app/nugen/dossier_generator.py`](../../backend/app/nugen/dossier_generator.py), [`backend/app/nugen/legal_engine.py`](../../backend/app/nugen/legal_engine.py) | **VERIFIED** |

---

## 3. Detailed Technical Assessment

### 3.1 Backend Architecture & Ephemeral Persistence
- **FastAPI Framework**: Uses clean dependency injection (`Depends(get_db)`), async lifespan event handling, and Pydantic response models.
- **Serverless /tmp Limitation**: In Vercel serverless, the database is stored in `/tmp/oil_spill.db` (`api/index.py`). Because serverless lambdas are stateless and freeze or recycle containers, data written to `/tmp` is wiped on cold start or when requests route to different instances. **This is unacceptable for durable national incident tracking.**
- **Transient Computation**: Running `/api/cases/:id/run` computes results transiently in memory and returns JSON without persisting the output into database tables (`SlickDetection`, `DriftResult`, `VesselScore`).

### 3.2 Machine Learning & Computer Vision (Radar CV)
- **Code Structure**: Clean separation of `dataset.py`, `model_utils.py`, `shape_features.py`, and `train.py`.
- **Reality**:
  - The model weights file `unet_resnet34_oilspill.pth` is missing from `backend/data/models/`.
  - When `detect_slick()` fails (or if PyTorch is not installed in the lightweight deployment runtime), `orchestrator.py` falls back to `_generate_slick_polygon(case.id)`.
  - For nationwide operation, a genuine U-Net model with verified weights and real Sentinel-1 GRD preprocessing (radiometric calibration, Lee speckle filtering, decibel thresholding) must be introduced as a formal scientific validation milestone.

### 3.3 Hydrodynamic Drift Modeling
- **Reality**:
  - OpenDrift requires compiled scientific libraries (`netcdf4`, `xarray`, `scipy`) that are difficult to bundle into serverless runtimes.
  - `drift_model.py` implements a pure-Python Lagrangian advection simulator that accurately reproduces advection drift and turbulent diffusion equations, seeded from a fixed RNG.
  - To transition from simulated drift to environmentally-driven drift, real CMEMS surface currents and ERA5 wind vectors must be ingested and spatially interpolated.

### 3.4 Telemetry & Scoring
- **Active Scorer**: `backend/app/scoring/scorer.py` evaluates 6 features: Proximity (25%), Parity (15%), Temporality (20%), AIS Blackout (15%), Speed Anomaly (10%), and Vessel Type Prior (15%).
- **Reality**:
  - The mathematical formulas in `features.py` are sound and produce explainable rankings.
  - However, telemetry data is loaded exclusively from static JSON files (`ais_cache_positions.json`, `ais_cache_gaps.json`) for Cases 1 and 2.
  - A high attribution score in this heuristic formula provides investigative lead prioritization, not definitive legal proof.

### 3.5 Maritime Legal Engine & Nugen
- **Reality**:
  - The remote endpoint `https://docs.nugen.in/inference` is a documentation URL, not an active model API.
  - The system utilizes the built-in fallback `LOCAL_DOMAIN_ALIGNED_ENGINE` inside `client.py`, which provides domain-aligned legal findings citing the Indian Merchant Shipping Act 1958 §356E/§356J and MARPOL Annex I.
  - Generated legal dossiers must be explicitly treated as investigative drafts requiring qualified human legal review before issuance.
