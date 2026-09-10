# PERSON 1 — Repository Owner / Backend API / Frontend / Integration Lead

Read `docs/ARCHITECTURE.md` in full before starting anything below — this file assumes you already have. You are the first person to act; Person 2 and Person 3 cannot meaningfully start until you complete Steps 1-6.

---

## Your role in one sentence
You own the repository, the database, the API layer, the pipeline orchestrator, the entire frontend, and final integration/testing — you build the "skeleton and nervous system"; Person 2 and Person 3 build two of the "organs" (detection, and drift+scoring) that plug into it.

---

## STEP-BY-STEP SEQUENCE

### STEP 1 — Create the GitHub repository
```bash
mkdir oil-spill-detection && cd oil-spill-detection
git init
git branch -M main
```
Create the repo on GitHub (via the web UI or `gh repo create oil-spill-detection --public --source=. --remote=origin`), then:
```bash
git remote add origin <repository-url>
```

### STEP 2 — Create the directory structure
Create every folder and empty `__init__.py`/placeholder file listed in `docs/ARCHITECTURE.md` §4. Use `.gitkeep` in empty folders that git would otherwise ignore (e.g. `backend/data/demo_cases/.gitkeep`).

```bash
mkdir -p backend/app/{routers,pipeline,utils,ml,physics,scoring}
mkdir -p backend/data/{demo_cases,raw,models}
mkdir -p backend/scripts backend/tests
mkdir -p frontend/src/{api,components,styles}
mkdir -p docs
touch backend/app/__init__.py backend/app/routers/__init__.py backend/app/pipeline/__init__.py \
      backend/app/utils/__init__.py backend/app/ml/__init__.py backend/app/physics/__init__.py \
      backend/app/scoring/__init__.py
touch backend/data/demo_cases/.gitkeep backend/data/raw/.gitkeep backend/data/models/.gitkeep
```

### STEP 3 — Create initial files

**`README.md`** — project name, one-paragraph description, setup instructions (to be filled in fully once the stack is confirmed working — start with a placeholder: "Setup instructions: TBD, see docs/ARCHITECTURE.md for design").

**`.gitignore`**
```
# Python
__pycache__/
*.pyc
.venv/
venv/

# Data (large files, never commit)
backend/data/raw/*
!backend/data/raw/README.md
backend/data/models/*.pth
backend/data/oil_spill.db

# Node
frontend/node_modules/
frontend/dist/

# Env
.env
*.env

# OS
.DS_Store
```

**`backend/requirements.txt`** — start with the shared baseline; Person 2 and Person 3 will append their own sections (clearly marked with a comment header):
```
fastapi>=0.110
uvicorn[standard]>=0.29
sqlalchemy>=2.0
pydantic>=2.0
shapely>=2.0
pyproj
requests
pytest

# --- Person 2 (ML) additions below ---

# --- Person 3 (physics/scoring) additions below ---
```

**`backend/data/raw/README.md`** and **`backend/data/models/README.md`** — create these files with a one-line placeholder each; Person 2 and Person 3 fill in the actual download instructions for their own data.

### STEP 4 — Add dependencies (baseline only)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### STEP 5 — Create configuration and the `utils/geo.py` STUB (highest priority file)

**`backend/app/config.py`**
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent   # backend/
DATA_DIR = BASE_DIR / "data"
DEMO_CASES_DIR = DATA_DIR / "demo_cases"
MODELS_DIR = DATA_DIR / "models"
DATABASE_URL = f"sqlite:///{DATA_DIR / 'oil_spill.db'}"

GFW_API_KEY = os.environ.get("GFW_API_KEY", "")   # Person 3 reads this
```

**`backend/app/utils/geo.py` — write the STUB version now** (exact signatures from ARCHITECTURE.md §5.1, bodies raise `NotImplementedError` for now except trivial ones you can do immediately):

```python
from shapely.geometry import shape, mapping, MultiPoint
from shapely.ops import transform as shapely_transform
import pyproj
from functools import partial
import math

def geojson_polygon_from_mask(mask, transform, crs="EPSG:4326") -> dict:
    raise NotImplementedError  # Person 1 fills in Day 2

def polygon_area_km2(polygon_geojson: dict) -> float:
    raise NotImplementedError  # Person 1 fills in Day 2

def polygon_perimeter_km(polygon_geojson: dict) -> float:
    raise NotImplementedError  # Person 1 fills in Day 2

def polygon_elongation(polygon_geojson: dict) -> float:
    raise NotImplementedError  # Person 1 fills in Day 2

def haversine_distance_km(point_a: tuple, point_b: tuple) -> float:
    # SIMPLE ENOUGH TO IMPLEMENT NOW — do it immediately, Person 3 needs it right away
    lon1, lat1 = point_a
    lon2, lat2 = point_b
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def bbox_from_polygon(polygon_geojson: dict, buffer_km: float) -> tuple:
    raise NotImplementedError  # Person 1 fills in Day 2
```
Commit and push this immediately after writing it — Person 2 and Person 3 are waiting on this exact file existing in `main` before they can write code that imports it.

### STEP 6 — Push the initial skeleton
```bash
git add .
git commit -m "[repo] initial project skeleton, config, geo.py stub"
git push -u origin main
```

### STEP 7 — Tell Person 2 and Person 3 to clone
Message both: "Skeleton is on `main`, `utils/geo.py` stub is in place with real `haversine_distance_km`. Clone now, create your branch, start work — see PERSON_2.md / PERSON_3.md."

They will run:
```bash
git clone <repository-url>
cd oil-spill-detection
git checkout -b person2/detection-setup     # or person3/ais-setup
```

**Files Person 2 may modify:** everything under `backend/app/ml/`, `backend/tests/test_detection.py`, `backend/scripts/download_training_data.py`, `backend/data/models/README.md`, `backend/data/raw/README.md` (their section only), `backend/requirements.txt` (append only, under their marked section).

**Files Person 3 may modify:** everything under `backend/app/physics/` and `backend/app/scoring/`, `backend/tests/test_drift.py`, `backend/tests/test_scoring.py`, `backend/data/raw/README.md` (their section only), `backend/requirements.txt` (append only, under their marked section).

**Files only Person 1 may modify:** `backend/app/main.py`, `config.py`, `database.py`, `models.py`, `schemas.py`, everything in `routers/`, `pipeline/orchestrator.py`, `utils/geo.py`, everything in `frontend/`. If Person 2 or 3 need a change here, they ask Person 1 rather than editing directly.

---

## STEP 8 — Database schema

**`backend/app/database.py`**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from . import models  # noqa: F401 — ensures models are registered before create_all
    Base.metadata.create_all(bind=engine)
```

**`backend/app/models.py`**
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from .database import Base

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    sar_image_path = Column(String, nullable=False)
    image_timestamp = Column(DateTime, nullable=False)
    bbox = Column(JSON)  # [min_lon, min_lat, max_lon, max_lat]

class SlickDetection(Base):
    __tablename__ = "slick_detections"
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    polygon_geojson = Column(JSON)
    confidence = Column(Float)
    area_km2 = Column(Float)
    perimeter_km = Column(Float)
    elongation = Column(Float)
    fragment_count = Column(Integer)
    age_class = Column(String)

class DriftResult(Base):
    __tablename__ = "drift_results"
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    detection_id = Column(Integer, ForeignKey("slick_detections.id"))
    origin_polygon_geojson = Column(JSON)
    estimated_origin_time = Column(DateTime)
    uncertainty_radius_km = Column(Float)

class VesselScore(Base):
    __tablename__ = "vessel_scores"
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    mmsi = Column(String)
    vessel_name = Column(String)
    vessel_type = Column(String)
    track_geojson = Column(JSON)
    scores_json = Column(JSON)   # dict of the six sub-scores
    final_score = Column(Float)
    explanation = Column(String)
```

**`backend/app/schemas.py`** — Pydantic mirrors of the above for API responses (one `XxxOut` schema per model, using `model_config = {"from_attributes": True}` for ORM mode). Write these once `models.py` is stable — straightforward field-for-field mapping, no special logic.

Commit: `git commit -m "[db] add SQLAlchemy models and Pydantic schemas"`.

---

## STEP 9 — Pick the demo case(s) (do this Day 1, it blocks Person 3)

1. Research 1-2 real, publicly documented Indian-waters oil-spill/pollution incidents with a specific date and location precise enough to check Sentinel-1 coverage (start with the 2025 Kerala/MSC Elsa III incident; if no usable Sentinel-1 scene exists for that exact date/area, find the nearest well-documented alternative with confirmed SAR coverage).
2. Confirm a Sentinel-1 GRD scene actually exists for that date+area via the Copernicus Data Space Ecosystem browser.
3. Write the case's metadata into `backend/data/demo_cases/case_1/case.json`:
```json
{
  "name": "Case 1 — <incident name>",
  "description": "<one paragraph, cite public reporting>",
  "sar_image_path": "data/raw/sentinel1/case_1_scene.tif",
  "image_timestamp": "2025-05-26T03:00:00Z",
  "bbox": [74.0, 8.5, 77.5, 11.0]
}
```
4. Message Person 2 and Person 3 immediately with the exact date/bbox/timestamp — this is the input both of them need to start their own data downloads (Sentinel-1 scene download is your job; CMEMS/ERA5/AIS downloads for this exact window are Person 3's job; downloading and reviewing the scene for training-relevance is useful info for Person 2).

Write a small script to seed the `cases` table from these JSON files at startup:

**`backend/app/pipeline/seed.py`**
```python
import json
from ..config import DEMO_CASES_DIR
from ..database import SessionLocal
from ..models import Case

def seed_cases_from_disk():
    db = SessionLocal()
    for case_dir in DEMO_CASES_DIR.iterdir():
        case_file = case_dir / "case.json"
        if not case_file.exists():
            continue
        data = json.loads(case_file.read_text())
        existing = db.query(Case).filter_by(name=data["name"]).first()
        if existing:
            continue
        db.add(Case(**data))
    db.commit()
    db.close()
```
Call `seed_cases_from_disk()` from `main.py` on startup (Step 10).

---

## STEP 10 — Backend app entrypoint and routers (build against a MOCK orchestrator first)

**`backend/app/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .pipeline.seed import seed_cases_from_disk
from .routers import cases, pipeline, health

app = FastAPI(title="Oil Spill Detection & Vessel Attribution API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(cases.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")

@app.on_event("startup")
def on_startup():
    init_db()
    seed_cases_from_disk()
```

**`backend/app/routers/health.py`**
```python
from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}
```

**`backend/app/routers/cases.py`**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Case

router = APIRouter()

@router.get("/cases")
def list_cases(db: Session = Depends(get_db)):
    cases = db.query(Case).all()
    return [{"id": c.id, "name": c.name, "description": c.description} for c in cases]

@router.get("/cases/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    c = db.query(Case).get(case_id)
    if not c:
        return {"error": "case not found"}
    return {"id": c.id, "name": c.name, "description": c.description,
            "image_timestamp": c.image_timestamp, "bbox": c.bbox}
```

**`backend/app/routers/pipeline.py`** — this is the one that will eventually call the real orchestrator, but build it against a **mock function first** so the frontend has something to talk to immediately:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter()

def _mock_pipeline_result(case_id: int) -> dict:
    """TEMPORARY — matches the exact shape orchestrator.run_full_pipeline() will return.
    Delete this and swap in the real call once ml/, physics/, scoring/ are ready (see STEP 13)."""
    return {
        "detection": {"polygon_geojson": {"type": "Polygon", "coordinates": [[[76.0,9.5],[76.1,9.5],[76.1,9.6],[76.0,9.6],[76.0,9.5]]]},
                      "confidence": 0.87, "shape_features": {"area_km2": 12.3, "perimeter_km": 8.1, "elongation": 2.4, "fragment_count": 1, "age_class": "fresh"}},
        "drift": {"origin_polygon_geojson": {"type": "Polygon", "coordinates": [[[75.9,9.4],[76.05,9.4],[76.05,9.55],[75.9,9.55],[75.9,9.4]]]},
                  "estimated_origin_time": "2025-05-25T22:00:00Z", "uncertainty_radius_km": 6.2},
        "vessels": [
            {"mmsi": "412345678", "vessel_name": "MT EXAMPLE", "vessel_type": "tanker",
             "track_geojson": {"type": "LineString", "coordinates": [[75.8,9.3],[76.0,9.45]]},
             "scores": {"proximity": 0.82, "parity": 0.55, "temporality": 0.71, "ais_gap": 0.9, "speed_anomaly": 0.1, "vessel_type_prior": 0.8},
             "final_score": 0.74, "explanation": "Mock explanation — replace with real ranked output."}
        ]
    }

@router.post("/cases/{case_id}/run")
def run_pipeline(case_id: int, db: Session = Depends(get_db)):
    return _mock_pipeline_result(case_id)   # STEP 13 replaces this line
```

Commit: `git commit -m "[api] add cases/pipeline/health routers with mock pipeline result"`.

---

## STEP 11 — Frontend shell (build against the mock endpoint)

```bash
cd frontend
npm create vite@latest . -- --template react
npm install react-leaflet leaflet axios
```

**`frontend/src/api/client.js`**
```javascript
import axios from "axios";
const API_BASE = "http://localhost:8000/api";

export async function listCases() {
  const res = await axios.get(`${API_BASE}/cases`);
  return res.data;
}

export async function runPipeline(caseId) {
  const res = await axios.post(`${API_BASE}/cases/${caseId}/run`);
  return res.data;   // shape: { detection, drift, vessels } — see ARCHITECTURE.md §5.5
}
```

**`frontend/src/App.jsx`** — top-level state: selected case, pipeline result (null until "Run" clicked). Renders `<CaseSelector>`, `<MapView>` (passing `detection`/`drift`/`vessels` down), `<SuspectList>`.

**`frontend/src/components/CaseSelector.jsx`** — dropdown populated from `listCases()`, calls `runPipeline(caseId)` on selection/button click, passes result up via a prop callback.

**`frontend/src/components/MapView.jsx`** — wraps `react-leaflet`'s `<MapContainer>`, renders `<SlickLayer>`, `<DriftLayer>`, `<AISTrackLayer>` as children, each taking the relevant GeoJSON as a prop and rendering via `<GeoJSON data={...} />`.

**`frontend/src/components/SlickLayer.jsx` / `DriftLayer.jsx` / `AISTrackLayer.jsx`** — each is a thin wrapper: `<GeoJSON data={polygon_geojson} style={{...}} />`, with distinct colors (e.g. slick = dark red, drift cloud = translucent blue, AIS tracks = green lines).

**`frontend/src/components/SuspectList.jsx`** — renders `vessels` array as a ranked list: name, type, `final_score` as a percentage/bar, `explanation` text, and a click handler that highlights the corresponding `track_geojson` on the map (lift the "selected vessel" state up to `App.jsx`).

**`frontend/src/components/ConfidencePanel.jsx`** — small panel showing `detection.confidence`, `drift.uncertainty_radius_km`, and a one-line "this is decision support, not proof" disclaimer — build this now, it directly supports the project's stated design principle and costs almost nothing.

Get this fully working against the mock endpoint before Person 2/3 are done — verify the whole click-through (select case → run → see slick, drift cloud, AIS tracks, ranked list) works with fake data.

Commit and push regularly as each component works.

---

## STEP 12 — Write your tests

**`backend/tests/test_geo_utils.py`** — test each function in `utils/geo.py` once implemented: known polygon → known area/perimeter/elongation; known point pair → known haversine distance (check against a hand-calculated value); malformed input → correct exception raised.

**`backend/tests/test_api.py`** — use FastAPI's `TestClient`: `GET /api/health` returns 200; `GET /api/cases` returns a list; `POST /api/cases/{id}/run` returns a dict with keys `detection`, `drift`, `vessels` (structure check, not exact values, since by the time this runs against real data the numbers will vary).

---

## STEP 13 — Integration (do this only once Person 2's `ml/infer.py` and Person 3's `physics/drift_model.py` + `scoring/scorer.py` are on `main` and return real (non-stub) data matching their contracts)

1. Pull latest `main`.
2. Finish `utils/geo.py` real implementations (if not already done in Step 5/Day 2) — `geojson_polygon_from_mask`, `polygon_area_km2`, `polygon_perimeter_km`, `polygon_elongation`, `bbox_from_polygon`, using `shapely` and an equal-area projection (e.g. reproject to a local UTM zone via `pyproj` before computing area/perimeter, since raw lat/lon degrees give wrong distances).
3. Write **`backend/app/pipeline/orchestrator.py`** per the exact contract in ARCHITECTURE.md §5.5 — call `ml.infer.detect_slick()`, then `physics.drift_model.run_backward_drift()`, then `scoring.scorer.rank_vessels()`, store each result as DB rows, wrap each stage in try/except so a single stage failure doesn't kill the whole response (return partial results with an `"error"` key for that stage).
4. In `routers/pipeline.py`, delete `_mock_pipeline_result` and its call, replace with:
```python
from ..pipeline.orchestrator import run_full_pipeline

@router.post("/cases/{case_id}/run")
def run_pipeline(case_id: int, db: Session = Depends(get_db)):
    return run_full_pipeline(case_id, db)
```
5. Run the full stack locally (`uvicorn app.main:app --reload` + `npm run dev`), click through the real demo case, verify the map and suspect list render with real data.
6. Run `pytest backend/tests` — everything must pass.
7. Fix bugs — since each module (ml/, physics/, scoring/) is owned by its author, route bugs to the right person rather than fixing their code yourself unless they're unavailable.

---

## STEP 14 — Final testing and demo prep

1. **Offline test**: disconnect from the internet (or block the relevant domains), re-run the full demo case end-to-end. It must work entirely from cached data (SAR scene, NetCDF files, AIS JSON cache) per ARCHITECTURE.md §7's non-negotiable rule. If it doesn't, find what's still hitting the network and cache it.
2. Write **`docs/DEMO_SCRIPT.md`**: exact click-by-click sequence for the live demo, including which case to select, what to say at each screen, and the honest "vs. Cerulean" talking points (pull directly from the differentiation analysis in ARCHITECTURE.md §0).
3. Rehearse the demo at least twice with the full team.
4. Finalize `README.md` with real, verified setup instructions — test them yourself on a fresh clone in a clean directory to make sure they actually work.

---

## Completion Checklist

- [ ] Repository created, skeleton pushed
- [ ] `utils/geo.py` fully implemented and tested
- [ ] Database models + schemas complete
- [ ] Demo case(s) selected, seeded, metadata committed
- [ ] All routers implemented and working
- [ ] Orchestrator wired to real ml/physics/scoring modules
- [ ] Frontend fully functional against real backend data
- [ ] `test_geo_utils.py` and `test_api.py` passing
- [ ] Full offline demo verified
- [ ] `DEMO_SCRIPT.md` written, rehearsed twice
- [ ] README verified on a clean clone
- [ ] All PRs from Person 2 and Person 3 reviewed and merged
- [ ] Final `main` branch is stable and demo-ready
