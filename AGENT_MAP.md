# AGENT MAP — Repository Navigation Index

**Target Repository:** `oil-spill-detection`  
**Application Name:** SAGAR-DRISHTI (Physics-Informed Maritime Oil Spill Detection & Vessel Attribution)  
**Target Domain:** Indian Coastline (7,516 km), Island Territories & Configurable Offshore Monitoring Zones  
**Primary Language/Runtime:** Python 3.11+ (FastAPI Backend), JavaScript ES Modules (React 18 + Vite Frontend)

---

## 1. Repository Identity

- **Purpose**: Automates the detection of illicit offshore marine oil spills from Copernicus Sentinel-1 SAR imagery, computes hydrodynamic backward Lagrangian particle advection (OpenDrift) to locate the precise origin envelope, correlates candidate vessel AIS telemetry using 6 domain features, and produces investigative draft enforcement dossiers under the Indian Merchant Shipping Act 1958 §356E/§356J and MARPOL Annex I Reg 15.
- **Implementation Status**: Full-stack maritime intelligence platform with a National Intelligence dashboard across 13 coastal states and Union Territories, five illustrative case studies, and two pre-cached benchmark cases (Kochi Port Approaches; Mumbai Port Approaches). Integrated with graceful fallbacks for offline or air-gapped operation.
- **Architecture**: Decoupled Client-Server (React SPA frontend + FastAPI REST backend + SQLite database + local domain-aligned legal engine). Supports standalone monolithic serving and Vercel serverless deployment.
- **Important Entry Points**:
  - Root Server Entrypoint: [`run.py`](run.py) (launches FastAPI at `0.0.0.0:8000`).
  - Backend Local Entrypoint: [`backend/run.py`](backend/run.py).
  - Vercel Serverless Function: [`api/index.py`](api/index.py).
  - Frontend Client Entrypoint: [`frontend/src/main.jsx`](frontend/src/main.jsx) & [`frontend/src/App.jsx`](frontend/src/App.jsx).
  - Core Pipeline Orchestrator: [`backend/app/pipeline/orchestrator.py`](backend/app/pipeline/orchestrator.py).

---

## 2. Repository Structure

### 2.1 Root Configuration & Wrappers

| Path | Responsibility | Why It Exists | Key Relationships |
| :--- | :--- | :--- | :--- |
| [`run.py`](run.py) | Root local server entrypoint. | Allows launching the full backend from the project root without modifying `PYTHONPATH`. | Appends `backend/` to `sys.path` and runs `app.main:app` via Uvicorn. |
| [`package.json`](package.json) | Root monorepo script runner. | Coordinates frontend building and asset copying into backend static distribution. | Defines `build`, `dev`, `start` scripts. |
| [`requirements.txt`](requirements.txt) | Serverless & base Python requirements. | Root-level dependencies for serverless deployment (`fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `shapely`, `requests`). | Used by root installer and Vercel. |
| [`vercel.json`](vercel.json) | Vercel deployment specification. | Defines routing rewrites and mounts `api/index.py` as a serverless function while serving `frontend/dist`. | Used by Vercel Cloud runtime. |
| [`pytest.ini`](pytest.ini) | Pytest configuration. | Sets `pythonpath = backend` and `testpaths = backend/tests`. | Used by test runners. |
| [`.gitignore`](.gitignore) | Git exclusion specification. | Prevents committing `.env`, virtualenvs, `.db` files, raw satellite GeoTIFFs, and `.pth` binaries. | Enforced by Git. |
| [`README.md`](README.md) | Human-facing project overview. | High-level summary, pipeline overview, case-study positioning, deployment link, and operational economics. | Primary documentation for evaluators. |
| [`api/index.py`](api/index.py) | Serverless ASGI adapter. | Adapts FastAPI to Vercel Serverless Functions, redirects SQLite to `/tmp/oil_spill.db`, and initializes DB seeders on cold start. | Wraps `backend/app/main.py`. |
| [`app/__init__.py`](app/__init__.py) | Package redirect stub. | Maps root `import app.*` calls to `backend/app` for compatibility when run from root. | Redirects `sys.path` to `backend/app`. |

---

### 2.2 Backend Application (`backend/app/`)

| Path | Responsibility | Why It Exists | Key Relationships |
| :--- | :--- | :--- | :--- |
| [`backend/run.py`](backend/run.py) | Backend directory launcher. | Runs Uvicorn directly from inside `backend/`. | Imports `app.main:app`. |
| [`backend/requirements.txt`](backend/requirements.txt) | Comprehensive backend requirements. | Lists full dependencies (Core API, PyTorch, OpenDrift). | Used for local backend environment setup. |
| [`backend/app/main.py`](backend/app/main.py) | FastAPI app factory and lifecycle. | Configures CORS, mounts routers, executes database seeding, and serves static SPA assets. | Loads `routers/`, mounts static dist, triggers `init_db`. |
| [`backend/app/config.py`](backend/app/config.py) | Central path and environment configuration. | Defines `BASE_DIR`, `DEMO_CASES_DIR`, `DATABASE_URL`, and loads `GFW_API_KEY`. | Imported across all backend modules. |
| [`backend/app/database.py`](backend/app/database.py) | Database connection & session factory. | Initializes SQLite engine and provides `get_db` session dependency. | Used by FastAPI routers and `pipeline/seed.py`. |
| [`backend/app/models.py`](backend/app/models.py) | SQLAlchemy ORM models. | Defines `Case`, `SlickDetection`, `DriftResult`, and `VesselScore` tables. | Queried in `database.py`, `routers/`, `pipeline/`. |
| [`backend/app/schemas.py`](backend/app/schemas.py) | Pydantic data schemas. | Validates and serializes API payloads (`CaseOut`, `VesselScoreOut`, etc.). | Used for route input/output typing. |

#### Backend Submodules

- **Routers (`backend/app/routers/`)**:
  - [`health.py`](backend/app/routers/health.py): `GET /api/health` health probe.
  - [`cases.py`](backend/app/routers/cases.py): `GET /api/cases` and `GET /api/cases/{case_id}` endpoints; national illustrative cases are excluded from this live-pipeline API.
  - [`pipeline.py`](backend/app/routers/pipeline.py): `POST /api/cases/{id}/run`, `POST /api/cases/{id}/dossier`, `POST /api/nugen/inference`, `GET /api/nugen/benchmark`.
  - [`demo.py`](backend/app/routers/demo.py): National case-study endpoints under `/api/demo` (legacy path retained) for scenarios, coastal regions, full case bundles, and record refresh.
- **Pipeline Orchestration (`backend/app/pipeline/`)**:
  - [`orchestrator.py`](backend/app/pipeline/orchestrator.py): **Core pipeline workflow** chaining SAR detection, backward drift, 6-factor scoring, and Nugen legal dossier.
  - [`seed.py`](backend/app/pipeline/seed.py): Reads `backend/data/demo_cases/` and populates the SQLite database on startup.
- **Machine Learning & Radar CV (`backend/app/ml/`)**:
  - [`infer.py`](backend/app/ml/infer.py): Public ML interface `detect_slick()`; loads U-Net checkpoint or returns case benchmark fallback.
  - [`dataset.py`](backend/app/ml/dataset.py): PyTorch `Dataset` & `DataLoader` for SAR images and masks.
  - [`model_utils.py`](backend/app/ml/model_utils.py): U-Net ResNet-34 builder (`segmentation_models_pytorch`) and checkpoint loader.
  - [`shape_features.py`](backend/app/ml/shape_features.py): Computes area, perimeter, elongation ratio, and age classification (`fresh`/`aging`/`old`).
  - [`train.py`](backend/app/ml/train.py): Training CLI using combined BCE + Dice loss.
- **Physics & Hydrodynamics (`backend/app/physics/`)**:
  - [`drift_model.py`](backend/app/physics/drift_model.py): **Active 200-particle backward Lagrangian retro-advection engine** calculating origin cone and uncertainty envelope over 18 hours.
  - [`environmental_data.py`](backend/app/physics/environmental_data.py): NetCDF readers for CMEMS ocean currents and ERA5 wind vectors.
- **Scoring & AIS Telemetry (`backend/app/scoring/`)**:
  - [`scorer.py`](backend/app/scoring/scorer.py): **Active 6-factor suspect ranker** and statutory explanation generator.
  - [`features.py`](backend/app/scoring/features.py): Formulations for Proximity, Parity, Temporality, AIS Blackout, Speed Anomaly, and Prior.
  - [`ais_client.py`](backend/app/scoring/ais_client.py): Cache reader for local AIS files (`demo_cases/case_X/`) and optional live Global Fishing Watch API client.
- **Nugen Domain-Aligned Legal Engine (`backend/app/nugen/`)**:
  - [`client.py`](backend/app/nugen/client.py): REST client calling Nugen SLM with resilient local fallback.
  - [`legal_engine.py`](backend/app/nugen/legal_engine.py): Maritime law knowledge base (MARPOL Annex I, Indian Merchant Shipping Act 1958 §356E/§356J, UNCLOS).
  - [`multi_agent.py`](backend/app/nugen/multi_agent.py): Multi-agent coordinator (Radar Agent, Physics Agent, Dossier Agent).
  - [`dossier_generator.py`](backend/app/nugen/dossier_generator.py): Formats investigative draft legal dossiers for Indian Coast Guard MRCC.
  - [`benchmarks.py`](backend/app/nugen/benchmarks.py): Scientific benchmarks comparing Base Model vs. Nugen Maritime SLM.
- **National Case Studies (`backend/app/`)**:
  - [`demo_data.py`](backend/app/demo_data.py): Loads the five nationwide case-study fixtures, computes summary statistics, and seeds isolated SQLite rows with explicit synthetic provenance.
  - [`regions.py`](backend/app/regions.py): Defines the 13 coastal state and Union Territory search envelopes used by the national dashboard.
- **Shared Utilities (`backend/app/utils/`)**:
  - [`geo.py`](backend/app/utils/geo.py): Haversine distance, equal-area projected polygon area (LAEA), perimeter, elongation, and mask-to-GeoJSON converter.

---

### 2.3 Documentation Directory (`docs/` & `project_audit/`)

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Foundational system design and comparison against SkyTruth Cerulean.
- [`docs/CASE_STUDY_WALKTHROUGH.md`](docs/CASE_STUDY_WALKTHROUGH.md): Walkthrough of the National Intelligence dashboard, the five illustrative case studies, and the analysis pipeline for evaluators.
- [`docs/agent-architecture.md`](docs/agent-architecture.md): Implementation mechanics for coding agents (U-Net, drift math, 6-factor formulas).
- [`docs/api-contracts.md`](docs/api-contracts.md): Complete HTTP REST endpoint contracts, query parameters, and JSON payloads.
- [`project_audit/national_expansion/`](project_audit/national_expansion/): The authoritative 9-document nationwide expansion architecture suite.

---

## 3. Critical Agent Modification Rules

1. **Strict Data Provenance**:
   - Every observation and incident must carry explicit provenance (`LIVE_OBSERVATION`, `HISTORICAL_VERIFIED`, `SIMULATED_DEMO`, `SIMULATED_ANALYSIS`).
   - Synthetic benchmark scenarios must be isolated and never count toward operational surveillance metrics or live enforcement evidence.
2. **Coordinate Ordering Conventions**:
   - GeoJSON specifications mandate `[longitude, latitude]`.
   - Leaflet native markers and polylines expect `[latitude, longitude]`.
   - Do not alter GeoJSON coordinate order in backend outputs.
3. **Database Persistence Rule**:
   - Do not rely on serverless `/tmp` storage for durable incident tracking. Operational persistence must use a persistent SQLite database on VPS or a managed cloud PostgreSQL instance.
4. **Human Review Policy**:
   - All generated Section 356J dossiers must be explicitly marked as **INVESTIGATIVE DRAFTS** requiring qualified human review before official issuance.
