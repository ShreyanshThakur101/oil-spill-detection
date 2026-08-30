# Oil Spill Detection & Vessel Attribution — Master Architecture

This document is the single source of truth for the system design. `PERSON_1.md`, `PERSON_2.md`, `PERSON_3.md` all reference this file and must not contradict it. If anything in a person-file seems to conflict with this document, this document wins — flag it to Person 1 immediately rather than silently deviating.

---

## 0. Reference Repository — What We Study, What We Take, What We Reject

**Reference:** SkyTruth's Cerulean (`SkyTruth/ceruleanserver`, `SkyTruth/cerulean-cloud`, `cerulean.skytruth.org`).

| Aspect | What Cerulean does | Our decision | Why |
|---|---|---|---|
| SAR ingestion | Live global polling of new Sentinel-1 scenes via AWS→GCP event chain | **Reject the live pipeline. Reuse the concept of "GeoTIFF in → mask out."** We use a small, curated, pre-downloaded set of scenes. | A live global ingestion pipeline is infrastructure, not a demo feature. It buys us nothing a judge can see and costs days we don't have. |
| Slick detection model | Instance-segmentation deep model, custom-trained at scale | **Retain the approach (CNN, pretrained backbone, fine-tuned), reject their exact model/weights.** We train our own U-Net (ResNet34 encoder) on the public Kaggle Sentinel-1 dataset. | This is the one place a neural net is the right tool (see §2). We must train our own weights — using theirs would not be our work and we couldn't defend it under questioning. |
| Shape/geometry features | Computed server-side in a database | **Retain the concept, reimplement in plain Python (shapely), not in-database.** | A full PostGIS deployment is unnecessary weight for a hackathon. Shapely gives us the same geometry math with zero infrastructure. |
| Infrastructure (offshore platform) source attribution | Distance-decay probability model against a global fixed-infrastructure dataset | **Remove entirely.** | No usable, verified offshore-infrastructure location dataset for Indian waters within our timeframe; this feature was also the lowest-value item in the original scoring formula. |
| AIS correlation | Built on Global Fishing Watch's AIS database (vessel presence, identity, dark-vessel/AIS-disabling events) | **Reuse directly — call the free GFW API rather than building our own AIS ingestion.** | This is the single biggest feasibility win available. Nobody should build an AIS pipeline from scratch in a hackathon when a free, documented, rate-limit-generous API already does it. |
| "Slick confidence" ML score (geometric-feature classifier for <72hr-old detections) | A second, separate ML model | **Remove.** Replaced by a simple deterministic plausibility check (shape features within expected ranges) inside `ml/shape_features.py`. | A second trained model roughly doubles our ML surface area for a feature that mainly buys speed-of-availability, which doesn't matter in a fixed demo. Not worth the training-data and validation burden. |
| Backward-drift / origin estimation | **Cerulean uses a fixed time window (per team's own research), not physics-based backtracking.** | **This is our real point of differentiation — build it.** We integrate OpenDrift for genuine backward particle-advection using real current/wind data. | This is a legitimate capability gap, it's buildable in a hackathon with pre-cached environmental data for chosen demo cases, and it directly answers "why is yours better" with a concrete technical answer, not a vague claim. |
| Vessel scoring formula | Three separate scores (parity, proximity, temporality), not fused | **Retain their three core features, add AIS-gap/speed-anomaly/vessel-type-prior, fuse into one explained ranked score.** Explicitly labeled as a v1 heuristic, not a trained/calibrated model. | Fusing scores with plain-English explanations is real UX value for a reviewer. We must not claim statistical calibration we haven't validated. |
| Deployment | Multi-cloud (AWS + GCP), Pulumi-managed, serverless | **Reject entirely.** Single FastAPI backend, single SQLite file, run locally or on one small VM for the demo. | Zero demo value from multi-cloud infrastructure; enormous time cost and failure surface. |
| API | OGC-compliant REST API | **Reject OGC compliance. Build a plain REST/JSON API (FastAPI) that does the job.** | OGC compliance is a standards-conformance feature for third-party GIS tooling integration — irrelevant to a hackathon demo audience. |
| Frontend | Public global web map | **Retain the concept (map-centric dashboard), rebuild for our own case set and reviewer-oriented UI (ranked suspect panel, explanation text, confidence indicators).** | Cerulean's UI is built for public awareness at global scale; ours needs to look like an operational decision-support tool for a specific reviewer workflow. |

**Net result:** our system is a smaller, single-machine, three-stage-plus-dashboard pipeline that reuses the *scientifically sound components* Cerulean also relies on (Sentinel-1, a CNN segmentation approach, GFW AIS data), replaces their fixed-window origin estimate with real physics-based backward drift, and drops every piece of infrastructure and every ML component that doesn't earn its complexity for a hackathon demo.

---

## 1. Final System Architecture

```
                      ┌─────────────────────────┐
                      │   React Frontend (SPA)   │
                      │  Map + Suspect Panel     │
                      └────────────┬─────────────┘
                                   │ HTTP/JSON (fetch)
                      ┌────────────▼─────────────┐
                      │   FastAPI Backend         │
                      │  routers/ (cases,         │
                      │  detection, drift,        │
                      │  scoring)                 │
                      └──┬───────┬───────┬────────┘
                         │       │       │
             ┌───────────▼┐ ┌────▼────┐ ┌▼─────────────┐
             │ ml/         │ │physics/ │ │scoring/       │
             │ (detection) │ │(drift)  │ │(AIS+ranking)  │
             │ Person 2    │ │Person 3 │ │Person 3       │
             └─────┬───────┘ └────┬────┘ └───────┬───────┘
                   │              │              │
                   └──────┬───────┴──────┬───────┘
                          │              │
                   ┌──────▼──────┐ ┌─────▼─────────┐
                   │ utils/geo.py │ │ SQLite DB      │
                   │ (Person 1)   │ │ (Person 1)     │
                   └──────────────┘ └────────────────┘
```

Data flows one direction per pipeline run: `orchestrator.run_full_pipeline(case_id)` (Person 1, in `pipeline/orchestrator.py`) calls, in order: `ml.infer.detect_slick()` → `physics.drift_model.run_backward_drift()` → `scoring.scorer.rank_vessels()` (which internally calls `scoring.ais_client` and `scoring.features`). Results are written to SQLite and returned as one combined JSON object that the frontend renders.

---

## 2. AI/ML Justification (do not add anything not listed here)

| Component | ML? | Justification |
|---|---|---|
| Slick segmentation (`ml/`) | **Yes — CNN (U-Net + ResNet34 encoder)** | Pixel-level segmentation against visual lookalikes (algae, low-wind cells, rain cells, shear lines) in noisy SAR imagery is a genuine computer-vision problem; simple thresholding demonstrably fails on this task, which is why every serious oil-slick detector (including Cerulean) uses a CNN here. Trained by Person 2 on the Kaggle Sentinel-1 Oil Spill Detection dataset. Lives in `backend/app/ml/`, exposed to the rest of the app only through `ml/infer.py:detect_slick()`. |
| Backward drift (`physics/`) | **No — physics simulation (OpenDrift), not ML.** | This is Lagrangian particle advection using real ocean current + wind fields. Do not use a neural network here under any circumstance — it would be strictly worse (less physically grounded, harder to explain, unnecessary complexity) than the existing, validated OpenDrift physics engine. |
| Vessel scoring (`scoring/`) | **No — rule-based weighted formula, not ML.** | We do not have (and will not fabricate) a labeled "confirmed spill → confirmed vessel" training set. A hand-reasoned, explicitly-labeled-as-heuristic weighted formula is honest, explainable, and defensible. **Do not introduce XGBoost/LightGBM/any trained ranking model for the hackathon build** — there is no valid training data for it. |
| Shape-based age/plausibility features | **No — deterministic geometry (shapely).** | Elongation/compactness/fragment-count thresholds are simple geometric rules, not learned patterns. |

If at any point during the build someone is tempted to add a model "to make it look more advanced" — don't. It weakens the pitch (see the accompanying critical evaluation report) rather than strengthening it.

---

## 3. TECH STACK (final — do not substitute without Person 1's sign-off)

**Languages / runtimes**
- Python 3.11 (backend + ML + physics + scoring)
- Node.js 18+ / npm (frontend)

**Backend**
- FastAPI 0.110+ (REST API)
- Uvicorn (ASGI server)
- SQLAlchemy 2.0 (ORM)
- SQLite (single-file DB, `backend/data/oil_spill.db`) — no PostgreSQL/PostGIS; geospatial math is done in Python with `shapely`, not in the database
- Pydantic v2 (request/response schemas, comes with FastAPI)

**ML (Person 2's domain)**
- PyTorch 2.x
- `segmentation-models-pytorch` (ready-made U-Net + pretrained ResNet34 encoder — do not hand-roll a U-Net from scratch, this library is exactly the right level of abstraction)
- `rasterio` (read Sentinel-1 GeoTIFFs and their geotransform/CRS)
- `opencv-python`, `Pillow`, `numpy`
- `shapely` (mask→polygon, shape metrics)

**Physics (Person 3's domain)**
- `opendrift`
- `xarray`, `netCDF4` (reading cached CMEMS/ERA5 NetCDF files)

**AIS / Scoring (Person 3's domain)**
- `requests` (calling the Global Fishing Watch REST API directly — do not add the `gfw-api-python-client` package unless there's spare time; raw `requests` calls are simpler to debug under time pressure and this is a small number of endpoints)

**Frontend**
- React 18 (via Vite — faster dev server than CRA, fewer moving parts)
- `react-leaflet` + `leaflet` (map rendering — simpler and more predictable than Mapbox GL for a small demo, no API key/billing setup needed)
- `axios` (HTTP calls to backend)
- Plain CSS (no Tailwind/component-library setup — one more dependency we don't need for a 3-person hackathon build)

**Testing**
- `pytest` (all backend/ML/physics/scoring tests)
- No frontend test framework for the hackathon timeline — manual QA only (explicitly a scope cut, not an oversight)

**Version control**
- Git + GitHub (single repository, see §6 for workflow)

**Explicitly excluded:** Docker/Kubernetes, PostgreSQL/PostGIS, AWS/GCP/Azure, Redis, Celery/task queues, GraphQL, Next.js/SSR, authentication/OAuth, Tailwind/UI kits, microservices of any kind, XGBoost/LightGBM, any second neural network.

---

## 4. Complete Repository Structure

```text
oil-spill-detection/
│
├── README.md                          # Person 1 — project overview, setup instructions
├── .gitignore                         # Person 1
├── docs/
│   ├── ARCHITECTURE.md                # this file — Person 1 commits it
│   └── DEMO_SCRIPT.md                 # Person 1 — exact click-by-click demo walkthrough
│
├── backend/
│   ├── requirements.txt               # Person 1 creates skeleton; everyone adds their own libs
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # Person 1 — FastAPI app, includes all routers
│   │   ├── config.py                  # Person 1 — paths, env vars, constants
│   │   ├── database.py                # Person 1 — SQLAlchemy engine/session/Base
│   │   ├── models.py                  # Person 1 — ORM models (Case, SlickDetection, DriftResult, VesselScore)
│   │   ├── schemas.py                 # Person 1 — Pydantic request/response schemas
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── cases.py               # Person 1 — GET /api/cases, GET /api/cases/{id}
│   │   │   ├── pipeline.py            # Person 1 — POST /api/cases/{id}/run (orchestrator trigger)
│   │   │   └── health.py              # Person 1 — GET /api/health
│   │   │
│   │   ├── pipeline/
│   │   │   ├── __init__.py
│   │   │   └── orchestrator.py        # Person 1 — run_full_pipeline(), calls into ml/, physics/, scoring/
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── geo.py                 # Person 1 — SHARED geometry helpers (see §5, build FIRST)
│   │   │   └── logging_config.py      # Person 1
│   │   │
│   │   ├── ml/                        # Person 2 — owns this entire folder
│   │   │   ├── __init__.py
│   │   │   ├── dataset.py
│   │   │   ├── model_utils.py
│   │   │   ├── train.py
│   │   │   ├── infer.py
│   │   │   └── shape_features.py
│   │   │
│   │   ├── physics/                   # Person 3 — owns this folder
│   │   │   ├── __init__.py
│   │   │   ├── environmental_data.py
│   │   │   └── drift_model.py
│   │   │
│   │   └── scoring/                   # Person 3 — owns this folder
│   │       ├── __init__.py
│   │       ├── ais_client.py
│   │       ├── features.py
│   │       └── scorer.py
│   │
│   ├── data/
│   │   ├── demo_cases/                # small GeoJSON/JSON files — COMMITTED to git (see §7)
│   │   ├── raw/                       # gitignored — large raw downloads
│   │   │   └── README.md              # download instructions (Person 2 + Person 3 write their own sections)
│   │   ├── models/                    # gitignored — trained .pth weights, too large for git
│   │   │   └── README.md              # Person 2 — link to hosted weights (Google Drive) + checksum
│   │   └── oil_spill.db               # gitignored — generated at runtime
│   │
│   ├── scripts/
│   │   ├── download_demo_data.py      # Person 1 — fetches/caches the chosen demo case(s)
│   │   └── download_training_data.py  # Person 2 — pulls Kaggle dataset
│   │
│   └── tests/
│       ├── test_geo_utils.py          # Person 1
│       ├── test_api.py                # Person 1
│       ├── test_detection.py          # Person 2
│       ├── test_drift.py              # Person 3
│       └── test_scoring.py            # Person 3
│
└── frontend/
    ├── package.json                   # Person 1
    ├── index.html                     # Person 1
    ├── vite.config.js                 # Person 1
    └── src/
        ├── main.jsx                   # Person 1
        ├── App.jsx                    # Person 1
        ├── api/
        │   └── client.js              # Person 1 — axios wrappers calling backend endpoints
        ├── components/
        │   ├── CaseSelector.jsx       # Person 1
        │   ├── MapView.jsx            # Person 1
        │   ├── SlickLayer.jsx         # Person 1
        │   ├── DriftLayer.jsx         # Person 1
        │   ├── AISTrackLayer.jsx      # Person 1
        │   ├── SuspectList.jsx        # Person 1
        │   └── ConfidencePanel.jsx    # Person 1
        └── styles/
            └── main.css               # Person 1
```

**Note on frontend ownership:** the frontend is entirely Person 1's responsibility because it is the integration surface — it consumes the combined output of Person 2's and Person 3's modules through one well-defined API response shape (§5), so it can only be meaningfully built by whoever also owns the orchestrator and API layer. This is why Person 1's backend+frontend load is larger, matching their role as integration owner.

---

## 5. Cross-Person Interface Contracts (build these signatures exactly — do not deviate)

These are the **only** points where Person 2's and Person 3's code is called by someone else. If you need to change a signature, you must message the other two people before doing it — a silent signature change breaks the whole system.

### 5.1 `backend/app/utils/geo.py` — Person 1 owns, Person 2 & 3 depend on it (BUILD THIS FIRST, DAY 1)

```python
def geojson_polygon_from_mask(mask: "np.ndarray", transform: "affine.Affine", crs: str = "EPSG:4326") -> dict:
    """
    Input:  mask — 2D binary numpy array (1 = slick pixel, 0 = background)
            transform — affine geotransform from the source raster (rasterio-style)
            crs — coordinate reference system string
    Output: GeoJSON Polygon (or MultiPolygon) dict, e.g. {"type": "Polygon", "coordinates": [[[lon, lat], ...]]}
    Purpose: converts the raw pixel mask output of the CNN into a real-world geographic polygon.
    Errors: raises ValueError if mask is empty (no positive pixels).
    Called by: ml/infer.py
    """

def polygon_area_km2(polygon_geojson: dict) -> float:
    """Input: GeoJSON polygon. Output: area in km^2, computed using an equal-area projection (not raw lat/lon degrees)."""

def polygon_perimeter_km(polygon_geojson: dict) -> float:
    """Input: GeoJSON polygon. Output: perimeter length in km."""

def polygon_elongation(polygon_geojson: dict) -> float:
    """
    Output: ratio of the polygon's minimum bounding rectangle's long side to short side (>=1.0).
    Purpose: fresh spills are compact (elongation near 1), old/spread spills are elongated.
    """

def haversine_distance_km(point_a: tuple, point_b: tuple) -> float:
    """Input: (lon, lat) tuples. Output: great-circle distance in km. Used by scoring/features.py."""

def bbox_from_polygon(polygon_geojson: dict, buffer_km: float) -> tuple:
    """
    Output: (min_lon, min_lat, max_lon, max_lat) bounding box, expanded by buffer_km on every side.
    Purpose: used by physics/environmental_data.py and scoring/ais_client.py to define the
             geographic search area around a slick or drift result.
    """
```

Person 1 must publish a **stub version** of this file (functions exist, raise `NotImplementedError`, but have the exact correct signatures) by end of Day 1, so Person 2 and Person 3 can write code against it immediately without waiting for the real implementation. Person 1 fills in real logic by Day 2.

### 5.2 `ml/infer.py:detect_slick()` — Person 2 owns, called by Person 1's `pipeline/orchestrator.py`

```python
def detect_slick(image_path: str, model=None) -> dict:
    """
    Input:
        image_path — path to a Sentinel-1 GeoTIFF (or pre-processed PNG) on local disk
        model — optional pre-loaded model object (if None, loads default weights from data/models/)
    Output:
        {
          "polygon_geojson": dict,      # from utils.geo.geojson_polygon_from_mask()
          "confidence": float,          # 0.0-1.0, mean softmax probability inside the predicted mask
          "shape_features": {           # from ml/shape_features.py
              "area_km2": float,
              "perimeter_km": float,
              "elongation": float,
              "fragment_count": int,
              "age_class": str          # one of "fresh" | "aging" | "old"
          },
          "mask_path": str              # path to saved binary mask PNG, for debugging/display
        }
    Errors: raises FileNotFoundError if image_path doesn't exist;
            raises RuntimeError if no slick-like region is detected above threshold
            (caller — orchestrator.py — must catch this and mark the case as "no detection").
    Example call:
        result = detect_slick("data/demo_cases/case_1/sar_scene.tif")
    """
```

### 5.3 `physics/drift_model.py:run_backward_drift()` — Person 3 owns, called by Person 1's `pipeline/orchestrator.py`

```python
def run_backward_drift(slick_polygon_geojson: dict, image_timestamp: "datetime", region_bbox: tuple, hours_back: int = 48) -> dict:
    """
    Input:
        slick_polygon_geojson — GeoJSON polygon of the detected slick (from detect_slick())
        image_timestamp — datetime the SAR image was captured (UTC)
        region_bbox — (min_lon, min_lat, max_lon, max_lat), from utils.geo.bbox_from_polygon()
        hours_back — how many hours to backtrack (default 48; configurable per demo case)
    Output:
        {
          "origin_polygon_geojson": dict,      # convex hull of backward-advected particle cloud
          "estimated_origin_time": "datetime", # image_timestamp - hours_back, or refined estimate
          "uncertainty_radius_km": float,      # rough spread metric of the particle cloud
          "particle_trace_geojson": dict       # optional — MultiPoint of final particle positions, for animation
        }
    Errors: raises RuntimeError if no environmental data (current/wind) is available for the
            requested bbox/date — caller must catch and fall back to displaying "drift unavailable"
            rather than crashing the whole pipeline.
    Example call:
        result = run_backward_drift(detection["polygon_geojson"], datetime(2025,5,26,3,0), (74.0,8.5,77.5,11.0))
    """
```

### 5.4 `scoring/scorer.py:rank_vessels()` — Person 3 owns, called by Person 1's `pipeline/orchestrator.py`

```python
def rank_vessels(origin_polygon_geojson: dict, origin_time_window: tuple, slick_polygon_geojson: dict, region_bbox: tuple, case_id: str) -> list:
    """
    Input:
        origin_polygon_geojson — from run_backward_drift()
        origin_time_window — (start_datetime, end_datetime) around estimated_origin_time
        slick_polygon_geojson — original detected slick shape (used for Parity scoring)
        region_bbox — search area
        case_id — string identifier of the Case row (e.g. "case_1"), used to load the correct
                   cached AIS JSON files via ais_client.load_cached_response()
    Output: list of dicts, sorted descending by final_score, e.g.:
        [
          {
            "mmsi": "412345678",
            "vessel_name": "MT EXAMPLE",
            "vessel_type": "tanker",
            "track_geojson": {...},          # LineString of vessel's AIS track in the time window
            "scores": {
                "proximity": 0.82, "parity": 0.55, "temporality": 0.71,
                "ais_gap": 0.90, "speed_anomaly": 0.10, "vessel_type_prior": 0.80
            },
            "final_score": 0.74,
            "explanation": "Passed within 3.1km of the estimated origin; AIS signal gap of 2.3 hours overlapping the origin window; vessel type (tanker) has elevated prior likelihood."
          },
          ...
        ]
    Errors: returns an empty list (not an exception) if no vessels are found in the AIS data for
            the given bbox/time window — caller displays "no candidate vessels found" in the UI.
    Called by: pipeline/orchestrator.py
    """
```

### 5.5 `pipeline/orchestrator.py:run_full_pipeline()` — Person 1 owns, called by the `/api/cases/{id}/run` route

```python
def run_full_pipeline(case_id: int, db_session) -> dict:
    """
    Input: case_id — primary key of a Case row already in the DB (created from demo_cases/ JSON at startup)
           db_session — SQLAlchemy session
    Output: combined dict with keys "detection", "drift", "vessels" — matches the shapes returned by
            detect_slick(), run_backward_drift(), and rank_vessels() respectively — and this exact
            dict shape is what routers/pipeline.py returns as JSON, and what the frontend consumes.
    Logic: 1) load Case row, get image path/timestamp/bbox
           2) call ml.infer.detect_slick() -> store SlickDetection row
           3) call physics.drift_model.run_backward_drift() -> store DriftResult row
           4) call scoring.scorer.rank_vessels() -> store VesselScore rows
           5) return combined dict
    Error handling: if any stage raises, catch it, store a partial result with an "error" field for
    that stage, and STILL return whatever stages succeeded — the frontend must be able to show partial
    results rather than a blank screen if e.g. drift fails on a case with bad environmental data.
    """
```

**This is the exact JSON shape the frontend's `api/client.js` and `App.jsx` are built against — Person 1 should treat this contract as fixed once agreed on Day 1.**

---

## 6. Git/GitHub Workflow

- **Single repository**, created and owned by Person 1.
- **`main` branch** is always the last known-good, working state. Nobody commits directly to `main` except Person 1, and only via merging a reviewed branch.
- **Branch naming:** `person2/detection-<short-topic>`, `person3/drift-<short-topic>`, `person3/scoring-<short-topic>`, `person1/<short-topic>`. Example: `person2/unet-training`, `person3/opendrift-integration`.
- **Commit message convention:** `[module] short imperative description`, e.g. `[ml] add U-Net inference function`, `[scoring] implement AIS gap scoring`.
- **Pull request procedure:** open a PR from your branch into `main` as soon as a function/module is testable, even if incomplete — small, frequent PRs, not one giant PR at the end. Title the PR the same as your primary commit message. In the PR description, state which interface contract (§5) it implements or depends on.
- **Merge responsibility:** Person 1 merges all PRs, after checking the PR doesn't break `main` (run `pytest` locally first). Person 2 and Person 3 do not merge their own PRs.
- **Pull/rebase discipline:** before starting new work each day, everyone runs `git checkout main && git pull origin main`, then branches off fresh from there — don't build on top of a week-old `main`.
- **Avoiding overwritten work:** because Person 2 and Person 3 each own entirely separate folders (`ml/` vs `physics/`+`scoring/`) and Person 1 owns everything else, there should be near-zero file-level conflicts. The only shared files are `utils/geo.py` (Person 1-owned, others only call it, never edit it directly — if you need a new geo helper, ask Person 1 to add it) and `requirements.txt` (append-only, don't reorder/remove others' lines).

---

## 7. Data Source Plan (final, no open options)

| Data | Source | Access | Format | Use | Committed to git? |
|---|---|---|---|---|---|
| SAR training imagery + masks | Kaggle "Oil Spill Detection" dataset | Free Kaggle account, `kaggle datasets download` CLI | PNG images + segmentation masks | Fine-tuning the U-Net (Person 2) | **No** — downloaded locally via `scripts/download_training_data.py`, path listed in `.gitignore` |
| SAR demo-case imagery | Copernicus Data Space Ecosystem (Sentinel-1 GRD), manually selected 1-2 scenes matching real, documented Indian-waters incidents (e.g., the 2025 Kerala/MSC Elsa III event window, if a usable scene exists for that date/area — verify availability first; if not, pick the closest well-documented alternative incident with confirmed Sentinel-1 coverage) | Free registration, manual download for the specific date/area | GeoTIFF | Detection input for the live demo | **No, large files** — cached locally, referenced by path in the Case DB row; a small preview PNG (not the full GeoTIFF) may be committed for the frontend "which case is this" thumbnail |
| Ocean currents | Copernicus Marine Service (CMEMS) | Free registration, Copernicus Marine Toolbox | NetCDF | OpenDrift backward drift (Person 3) | **No** — pre-downloaded once per demo case's date/bbox, cached locally |
| Wind | ERA5 (Copernicus Climate Data Store) | Free, CDS API | NetCDF/GRIB | OpenDrift backward drift (Person 3) | **No** — same as above |
| AIS vessel positions + identity + AIS-disabling events | **Global Fishing Watch API** | Free API key, REST calls via `requests` | JSON | Vessel scoring (Person 3) | **Yes for demo cases** — the specific API responses for the chosen demo case's bbox/time-window are fetched once and saved as small JSON files in `backend/data/demo_cases/case_X/ais_cache.json`, committed to git, so the live demo never depends on network access or the API being up during judging |

**Demo-day reliability rule (non-negotiable):** the actual on-stage demo must run **entirely from locally cached data** — cached SAR scene, cached NetCDF current/wind files, cached AIS JSON. Live API calls are used only during development/data preparation, never during the judged demo. Person 1 verifies this explicitly before the final demo (see `PERSON_1.md` final checklist).

**Committing large files:** GeoTIFFs and NetCDF files are excluded via `.gitignore`; each `data/raw/README.md` and `data/models/README.md` documents exactly how to regenerate/download them (exact URLs, exact CLI commands) so any teammate can reproduce the local data folder from a clean clone.

---

## 8. Feature Classification

**MUST HAVE**
- U-Net slick detection on 1-2 pre-selected demo scenes, with shape features
- OpenDrift backward drift on those same demo cases, using pre-cached environmental data
- Rule-based vessel scoring (Proximity, Parity, Temporality, AIS-gap, Speed anomaly, Vessel-type prior) against cached GFW AIS data
- Ranked suspect list with plain-English explanations
- Map dashboard: slick overlay, drift-cloud, AIS tracks, ranked list, click-to-highlight
- Fully offline-capable demo (all data cached)
- One-slide honest "vs. Cerulean" comparison (content, not code — Person 1 prepares this alongside the demo script)

**SHOULD HAVE (only after MUST HAVE is fully working end-to-end)**
- Weight-sensitivity slider on the scoring formula in the UI
- A second demo case, as redundancy against a bad run of the first
- Simple PDF/print view of a case's results

**NICE TO HAVE (only if everything above is done and stable with time to spare)**
- Drift-density heatmap instead of a hard convex-hull polygon
- Basic login gate on the dashboard

**DO NOT BUILD**
- Route Typicality feature
- Infrastructure (offshore platform) source attribution
- Live/global Sentinel-1 polling
- Multi-cloud/serverless deployment
- OGC API compliance
- XGBoost/LightGBM learned scoring model
- Any second neural network
- Authentication beyond a basic gate (no user roles, no OAuth)

---

## 9. Dependency Table

| Task | Owner | Prerequisite | Can start immediately? | Blocks |
|---|---|---|---|---|
| Repo scaffold + skeleton push | Person 1 | none | Yes | Everyone |
| `utils/geo.py` stub (signatures only) | Person 1 | Repo scaffold | Yes (right after scaffold) | Person 2's `ml/infer.py`, Person 3's `physics/` and `scoring/` |
| `models.py` / `schemas.py` (DB schema) | Person 1 | Repo scaffold | Yes | Person 1's own routers/orchestrator |
| Kaggle dataset download + `ml/dataset.py` | Person 2 | Repo scaffold, `requirements.txt` has torch | Yes | `ml/train.py` |
| U-Net training (`ml/train.py`) | Person 2 | `ml/dataset.py` done | No — needs dataset first | `ml/infer.py` real testing |
| `ml/infer.py` (real logic) | Person 2 | trained weights OR at least a partially-trained checkpoint; `utils/geo.py` real implementation | Partially — can write the function body/tests against the stub first | `pipeline/orchestrator.py` full run |
| `ml/shape_features.py` | Person 2 | `utils/geo.py` stub | Yes, in parallel with training | `ml/infer.py` |
| GFW API key + `scoring/ais_client.py` | Person 3 | Repo scaffold | Yes | `scoring/features.py`, `scoring/scorer.py` |
| CMEMS/ERA5 account + cached data for demo case | Person 3 | Person 1 has picked the demo case(s) (Day 1) | Yes, once case chosen | `physics/drift_model.py` |
| `physics/environmental_data.py` | Person 3 | cached NetCDF files downloaded | Yes | `physics/drift_model.py` |
| `physics/drift_model.py` (real OpenDrift run) | Person 3 | `environmental_data.py`, `utils/geo.py` real implementation | No — needs those first | `pipeline/orchestrator.py` full run |
| `scoring/features.py` | Person 3 | `utils/geo.py` real implementation, AIS client working | Partially — can write against stub | `scoring/scorer.py` |
| `scoring/scorer.py` | Person 3 | `scoring/features.py` | No | `pipeline/orchestrator.py` full run |
| `pipeline/orchestrator.py` (full wiring) | Person 1 | `ml/infer.py`, `physics/drift_model.py`, `scoring/scorer.py` all returning real (not stub) data | No — this is the integration point, deliberately last | `routers/pipeline.py`, frontend |
| `routers/` (API endpoints) | Person 1 | `models.py`/`schemas.py` done; can be built against orchestrator stub initially | Yes, in parallel, using a fake/stubbed orchestrator response | Frontend |
| Frontend components | Person 1 | API route shapes agreed (§5.5) — can build against mock JSON before backend is finished | Yes, in parallel | Final demo |
| End-to-end integration test | Person 1 | all of the above real (non-stub) | No — last step | Demo |

---

## 10. Integration Strategy

```
Day 1:  Person 1 creates skeleton + geo.py stub + DB schema + API route stubs
                │
        ┌───────┴────────┐
        ▼                ▼
Person 2 starts ML   Person 3 starts AIS client + env data download
(dataset, training)  (in parallel, fully independent of Person 2)
        │                │
        ▼                ▼
Person 2 finishes    Person 3 finishes drift_model.py + scorer.py
ml/infer.py real          │
        │                ▼
        └──────┬──────────┘
               ▼
   Person 1 wires pipeline/orchestrator.py using REAL Person 2 + Person 3 functions
               ▼
   Person 1 finishes routers/ + frontend, connects to real orchestrator
               ▼
        Full end-to-end test (Person 1 leads, all three participate)
               ▼
        Bug fixing (owner of the broken module fixes it)
               ▼
        Demo rehearsal (all three, using DEMO_SCRIPT.md)
```

**Risk mitigation:** Person 1's API routers and frontend are built against a **mocked orchestrator response** (a hardcoded JSON matching the §5.5 contract) from Day 1 onward, so Person 1 is never blocked waiting on Person 2/3. The moment Person 2's and Person 3's real functions are ready, Person 1 swaps the mock for the real orchestrator call — a small, low-risk change, not a rebuild.

---

## 11. Realistic Timeline

Assume roughly 10 working days of pre-hackathon build time, then a final 36-hour on-site polish/demo window (standard SIH finale format). Adjust day-counts proportionally if your actual available time differs — the **order and dependencies do not change**.

**Day 1**
- Person 1: create repo, push skeleton, `utils/geo.py` stub, DB models, requirements.txt, pick the 1-2 demo incident cases (this choice blocks Person 3's environmental data download, so do it early in the day)
- Person 2: set up ML environment, download Kaggle dataset, start `ml/dataset.py`
- Person 3: register for GFW/CMEMS/CDS accounts, start `scoring/ais_client.py` against real API

**Day 2-3**
- Person 1: fill in real `utils/geo.py`, build API router stubs against mocked orchestrator, start frontend shell (map, empty panels)
- Person 2: finish `ml/dataset.py`, start `ml/train.py`, kick off first training run
- Person 3: finish `ais_client.py`, download cached CMEMS/ERA5 data for the chosen case(s), start `environmental_data.py`

**Day 4-6**
- Person 1: finish frontend components against mock data, write `test_api.py`/`test_geo_utils.py`
- Person 2: iterate on training, implement `shape_features.py`, start `infer.py`, write `test_detection.py`
- Person 3: implement `drift_model.py` against real OpenDrift + cached data, implement `features.py`, write `test_drift.py`

**Day 7-8**
- Person 2: finalize `infer.py`, confirm it returns the exact §5.2 contract shape on the demo case image
- Person 3: finalize `scorer.py`, confirm `rank_vessels()` returns the exact §5.4 contract shape, write `test_scoring.py`
- Person 1: standing by to start integration the moment both are ready

**Day 9**
- Person 1: wire `pipeline/orchestrator.py` with real functions, replace frontend mock calls with real API calls, run first full end-to-end test
- Person 2 & 3: support integration debugging on their own modules

**Day 10**
- All three: bug fixing, polish, write `docs/DEMO_SCRIPT.md`, rehearse demo twice, confirm demo runs fully offline

**Hackathon Day (36hr window):** final polish only — no new features. Re-verify offline demo reliability at the start. Prepare the "vs. Cerulean" honest comparison talking points.

**Critical path:** `geo.py` stub → Person 2's `infer.py` real + Person 3's `drift_model.py`/`scorer.py` real → `orchestrator.py` wiring → routers/frontend real-data swap → end-to-end test. Everything else has slack.

**Biggest risk points and mitigation:**
1. U-Net training taking longer than expected / poor accuracy on the demo scene → Person 2 should pick the demo case's SAR scene *before* finalizing training so it can be sanity-checked against the trained model early, not discovered as a problem on Day 9.
2. OpenDrift + real NetCDF data has a real learning curve → Person 3 should do a "hello world" OpenDrift run with sample/tutorial data on Day 1-2, before touching real CMEMS/ERA5 files, to de-risk the tooling itself separately from the data.
3. Integration surprises on Day 9 → mitigated by the mock-first strategy in §10 — Person 1's side is never a surprise, only the real-data swap is.

---

## 12. Final Project Completion Checklist

- [ ] Architecture doc committed, all three people have read it
- [ ] Repo skeleton pushed, `main` branch protected (Person 1 merges only)
- [ ] `utils/geo.py` fully implemented and tested
- [ ] Backend: all routers implemented, `pipeline/orchestrator.py` wired to real modules
- [ ] Database: schema created, demo case(s) seeded
- [ ] ML: model trained, `ml/infer.py` returns correct contract shape on demo scene(s)
- [ ] Physics: `physics/drift_model.py` returns correct contract shape on demo scene(s), using cached environmental data
- [ ] Scoring: `scoring/scorer.py` returns correct contract shape, ranked list with explanations
- [ ] Frontend: map renders slick, drift cloud, AIS tracks, ranked suspect list, all from real backend data
- [ ] All `tests/` pass (`pytest backend/tests`)
- [ ] Demo runs fully offline (no live API calls during judging)
- [ ] `docs/DEMO_SCRIPT.md` written and rehearsed at least twice by the full team
- [ ] "Vs. Cerulean" honest comparison talking points prepared and every team member can recite them
- [ ] README has exact setup/run instructions verified on a clean clone
