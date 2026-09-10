# PERSON 3 — Drift Modeling & Vessel Scoring (Stages 2 & 3)

Read `docs/ARCHITECTURE.md` in full before starting, especially §2 (AI/ML justification — note that neither of your two stages uses ML), §5.3/§5.4 (your interface contracts), and §9 (dependency table). You own `backend/app/physics/` and `backend/app/scoring/` — nobody else edits files in there.

---

## Your role in one sentence
Stage 2: given a detected slick, estimate where and when it most likely originated using real physics (OpenDrift). Stage 3: given that origin estimate, pull real AIS vessel data and produce a ranked, explained list of suspect vessels. Both are exposed to the rest of the system through exactly two functions: `run_backward_drift()` and `rank_vessels()`.

---

## Prerequisites before you can fully finish (but you can start most of this immediately)

- `backend/app/utils/geo.py` **stub** must exist on `main` (Person 1, Day 1) — `haversine_distance_km` will be real immediately; the polygon functions will be stubs until Day 2. You can start your AIS client and environmental-data downloads without waiting on any of this.
- Person 1 will tell you the exact demo case (date/bbox/timestamp) by end of Day 1 — this is required before you can download the correct CMEMS/ERA5 files or query GFW for the right window.

---

## STEP 1 — Clone and branch

```bash
git clone <repository-url>
cd oil-spill-detection
git checkout -b person3/physics-scoring-setup
```

Only edit files under `backend/app/physics/`, `backend/app/scoring/`, `backend/tests/test_drift.py`, `backend/tests/test_scoring.py`, `backend/data/raw/README.md` (your own section, don't touch Person 2's), and `backend/requirements.txt` (append only, under the "Person 3" marker).

## STEP 2 — Set up environment and dependencies

Add to `backend/requirements.txt` under a "Person 3 (physics/scoring) additions" section:
```
opendrift
xarray
netCDF4
requests
```
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

**De-risk OpenDrift immediately (Day 1-2), before touching real data:** run OpenDrift's own bundled example/tutorial (it ships with sample readers and a "hello world" oil-drift script in its documentation) to confirm the library installs and runs correctly on your machine before you invest time wiring in real CMEMS/ERA5 files. This isolates "is OpenDrift itself working" from "is my real data working," which makes debugging much faster later.

## STEP 3 — Get accounts and API keys

1. **Global Fishing Watch**: register for a free API key at their developer portal. Store it as an environment variable, never commit it: add `GFW_API_KEY=<your key>` to a local `.env` file (already gitignored), and confirm `backend/app/config.py` reads it via `os.environ.get("GFW_API_KEY", "")` (Person 1 already wrote this in config.py — just make sure you export the env var before running your code, e.g. `export GFW_API_KEY=...` or use `python-dotenv` if the team wants that convenience — if you add `python-dotenv`, add it to requirements.txt under your section).
2. **Copernicus Marine Service (CMEMS)**: register for a free account, install/use the Copernicus Marine Toolbox to download current data for the demo case's bbox and date range (see STEP 5).
3. **Copernicus Climate Data Store (ERA5)**: register for a free account, get a CDS API key for downloading wind reanalysis data.

## STEP 4 — `scoring/ais_client.py`

```python
"""
Thin wrapper around the Global Fishing Watch REST API. All network calls to GFW live here —
no other file should call `requests` against GFW directly.
"""
import requests
from datetime import datetime
from ..config import GFW_API_KEY

GFW_BASE_URL = "https://gateway.api.globalfishingwatch.org/v3"

def _headers():
    return {"Authorization": f"Bearer {GFW_API_KEY}"}

def fetch_vessel_positions(bbox: tuple, start_time: datetime, end_time: datetime) -> list:
    """
    Input: bbox (min_lon, min_lat, max_lon, max_lat), start_time, end_time (UTC datetimes)
    Output: list of dicts, one per vessel found, e.g.:
        [{"mmsi": "412345678", "vessel_name": "MT EXAMPLE", "vessel_type": "tanker",
          "positions": [{"lat": 9.4, "lon": 75.9, "timestamp": "...", "speed_knots": 8.2}, ...]}, ...]
    Purpose: calls GFW's Vessels/4Wings API filtered to the bbox+time window.
    Errors: raises requests.HTTPError on non-200 response; caller (features.py/scorer.py) should
            catch this and treat it as "no vessel data available" rather than crashing the pipeline.

    NOTE: confirm the exact current endpoint path/parameters against GFW's live API documentation
    when you implement this — API paths and parameter names can change between doc versions, so
    verify against https://globalfishingwatch.org/our-apis/ directly rather than assuming this
    exact URL structure is still correct at build time.
    """
    raise NotImplementedError  # implement against verified current GFW API docs

def fetch_ais_gap_events(bbox: tuple, start_time: datetime, end_time: datetime) -> list:
    """
    Output: list of dicts, one per AIS-disabling ("going dark") event, e.g.:
        [{"mmsi": "412345678", "gap_start": "...", "gap_end": "...", "gap_hours": 2.3}, ...]
    Purpose: calls GFW's Events API filtered to event_type="AIS-disabling" (verify exact
    parameter name in current docs) within the bbox+time window.
    """
    raise NotImplementedError

def get_vessel_identity(mmsi: str) -> dict:
    """
    Output: {"mmsi": ..., "vessel_name": ..., "vessel_type": ..., "flag": ...}
    Purpose: resolve full identity info for a single vessel found in fetch_vessel_positions().
    """
    raise NotImplementedError

def cache_response_to_disk(data: dict, case_id: str, kind: str):
    """
    Input: data — the JSON response to cache; case_id — e.g. "case_1"; kind — "positions" or "gaps"
    Output: none. Writes to backend/data/demo_cases/{case_id}/ais_cache_{kind}.json
    Purpose: THIS IS MANDATORY FOR THE DEMO CASE — the live demo must run from this cached file,
    never from a live API call (see ARCHITECTURE.md §7). Call this once during data prep, after
    verifying the fetched data looks correct for your chosen demo case.
    """
    import json
    from ..config import DEMO_CASES_DIR
    path = DEMO_CASES_DIR / case_id / f"ais_cache_{kind}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, default=str, indent=2))

def load_cached_response(case_id: str, kind: str) -> dict:
    """Loads what cache_response_to_disk() wrote. Use this in the actual pipeline instead of
    live fetch_* calls once the cache exists — see STEP 8."""
    import json
    from ..config import DEMO_CASES_DIR
    path = DEMO_CASES_DIR / case_id / f"ais_cache_{kind}.json"
    return json.loads(path.read_text())
```

**Action item:** write a small standalone script (not part of the app, just a one-off you run yourself) that calls `fetch_vessel_positions()` and `fetch_ais_gap_events()` for the real demo case bbox/time window, inspects the results, and once you're satisfied they're correct, calls `cache_response_to_disk()` to save them. Commit the resulting `ais_cache_positions.json` / `ais_cache_gaps.json` files under `backend/data/demo_cases/case_1/` — these are small JSON files, safe to commit per ARCHITECTURE.md §7.

## STEP 5 — `physics/environmental_data.py`

```python
"""
Loads pre-cached CMEMS (current) and ERA5 (wind) NetCDF files as OpenDrift-compatible readers.
Does NOT hit any live API at pipeline-run time — all files are downloaded once during data prep
and cached under backend/data/raw/environmental/.
"""
from opendrift.readers import reader_netCDF_CF_generic
from pathlib import Path
from ..config import DATA_DIR

ENV_DATA_DIR = DATA_DIR / "raw" / "environmental"

def get_current_reader(case_id: str):
    """
    Output: an opendrift reader object built from the cached CMEMS current NetCDF file for this case.
    Errors: raises FileNotFoundError with a clear message if the expected file
    (ENV_DATA_DIR / f"{case_id}_currents.nc") doesn't exist — tells the caller to run the
    download step first, doesn't fail silently.
    """
    path = ENV_DATA_DIR / f"{case_id}_currents.nc"
    if not path.exists():
        raise FileNotFoundError(f"Missing cached current data: {path}. Run data prep step first.")
    return reader_netCDF_CF_generic.Reader(str(path))

def get_wind_reader(case_id: str):
    """Same pattern as get_current_reader() but for ERA5 wind data, file suffix '_wind.nc'."""
    path = ENV_DATA_DIR / f"{case_id}_wind.nc"
    if not path.exists():
        raise FileNotFoundError(f"Missing cached wind data: {path}. Run data prep step first.")
    return reader_netCDF_CF_generic.Reader(str(path))
```

**Manual data-prep step (do this once per demo case, not at pipeline runtime):** using the Copernicus Marine Toolbox, download the current data for the demo case's exact bbox and a time window spanning from `image_timestamp - 48h` to `image_timestamp`, save as `backend/data/raw/environmental/case_1_currents.nc`. Do the equivalent for ERA5 wind via the CDS API, saving as `case_1_wind.nc`. Document the exact download parameters (bbox, date range, variables selected — e.g. `uo`/`vo` for currents, `u10`/`v10` for wind) in `backend/data/raw/README.md` under your section so this is reproducible.

## STEP 6 — `physics/drift_model.py`

```python
"""
Backward particle-drift simulation using OpenDrift. This is physics, not machine learning —
see ARCHITECTURE.md §2 for why that distinction matters to the project's credibility.
"""
from datetime import timedelta
from opendrift.models.oceandrift import OceanDrift
from shapely.geometry import shape, MultiPoint, mapping
import numpy as np
from .environmental_data import get_current_reader, get_wind_reader

def run_backward_drift(slick_polygon_geojson: dict, image_timestamp, region_bbox: tuple,
                        hours_back: int = 48, case_id: str = "case_1") -> dict:
    """
    See exact contract in ARCHITECTURE.md §5.3.
    Logic:
        1. Seed ~1000 particles uniformly within slick_polygon_geojson.
        2. Build an OceanDrift model, add the current reader and wind reader for this case.
        3. Run the simulation BACKWARD in time (negative time_step) from image_timestamp for
           hours_back hours.
        4. Take the final particle positions (the "cloud").
        5. Compute the convex hull of that cloud as origin_polygon_geojson.
        6. Compute uncertainty_radius_km as the max distance from the cloud's centroid to any
           particle (using utils.geo.haversine_distance_km).
        7. estimated_origin_time = image_timestamp - hours_back (v1; can be refined later to the
           time the cloud's spread rate suggests release began, as a stretch goal).
    """
    from ..utils.geo import haversine_distance_km  # real implementation must exist by the time this runs

    slick_geom = shape(slick_polygon_geojson)
    minx, miny, maxx, maxy = slick_geom.bounds
    rng = np.random.default_rng(seed=42)
    seed_lons, seed_lats = [], []
    while len(seed_lons) < 1000:
        lon = rng.uniform(minx, maxx)
        lat = rng.uniform(miny, maxy)
        if slick_geom.contains(__import__("shapely.geometry", fromlist=["Point"]).Point(lon, lat)):
            seed_lons.append(lon)
            seed_lats.append(lat)

    try:
        current_reader = get_current_reader(case_id)
        wind_reader = get_wind_reader(case_id)
    except FileNotFoundError as e:
        raise RuntimeError(f"Environmental data unavailable for drift run: {e}")

    o = OceanDrift(loglevel=50)
    o.add_reader([current_reader, wind_reader])
    o.seed_elements(lon=seed_lons, lat=seed_lats, time=image_timestamp)
    o.run(time_step=-1800, duration=timedelta(hours=hours_back))  # negative step = backward

    final_lons = o.history["lon"][:, -1]
    final_lats = o.history["lat"][:, -1]
    cloud = MultiPoint(list(zip(final_lons, final_lats)))
    origin_polygon = cloud.convex_hull

    centroid = origin_polygon.centroid
    max_dist = max(
        haversine_distance_km((centroid.x, centroid.y), (lon, lat))
        for lon, lat in zip(final_lons, final_lats)
    )

    return {
        "origin_polygon_geojson": mapping(origin_polygon),
        "estimated_origin_time": image_timestamp - timedelta(hours=hours_back),
        "uncertainty_radius_km": max_dist,
        "particle_trace_geojson": mapping(cloud),
    }
```
**This is the highest-risk file in your two stages — start experimenting with it early (Day 3-4), not late.** OpenDrift's exact API (reader construction, `seed_elements`, `run` parameters) should be double-checked against its current documentation/examples when you implement this — the sketch above is structurally correct but verify exact method signatures against the installed OpenDrift version.

## STEP 7 — `scoring/features.py`

```python
"""
Individual scoring features — each returns a float in [0.0, 1.0]. Pure functions, no I/O,
easy to unit test in isolation.
"""
from ..utils.geo import haversine_distance_km
from shapely.geometry import shape, LineString

def compute_proximity_score(vessel_track: list, origin_polygon_geojson: dict) -> float:
    """
    Input: vessel_track — list of {"lat":.., "lon":.., "timestamp":..}; origin_polygon_geojson.
    Output: 1.0 if the vessel's closest approach is at/inside the origin polygon, decaying to 0.0
    at a configurable max distance (e.g. 20km) — linear decay is fine for v1.
    """
    origin_geom = shape(origin_polygon_geojson)
    centroid = origin_geom.centroid
    min_dist = min(
        haversine_distance_km((centroid.x, centroid.y), (p["lon"], p["lat"]))
        for p in vessel_track
    )
    MAX_DIST_KM = 20.0
    return max(0.0, 1.0 - min_dist / MAX_DIST_KM)

def compute_parity_score(vessel_track: list, slick_polygon_geojson: dict) -> float:
    """
    Output: how parallel the vessel's heading is to the slick's long axis, 1.0 = perfectly
    parallel, 0.0 = perpendicular. Compute the vessel track's dominant bearing and the slick
    polygon's minimum-rotated-rectangle long-axis bearing, take cos(angle difference).
    """
    if len(vessel_track) < 2:
        return 0.0
    import math
    p0, p1 = vessel_track[0], vessel_track[-1]
    vessel_bearing = math.atan2(p1["lon"] - p0["lon"], p1["lat"] - p0["lat"])

    slick_geom = shape(slick_polygon_geojson)
    mrr = slick_geom.minimum_rotated_rectangle
    coords = list(mrr.exterior.coords)
    edge = max(
        [(coords[i], coords[i+1]) for i in range(len(coords)-1)],
        key=lambda e: LineString(e).length
    )
    slick_bearing = math.atan2(edge[1][0] - edge[0][0], edge[1][1] - edge[0][1])

    angle_diff = abs(vessel_bearing - slick_bearing)
    return abs(math.cos(angle_diff))

def compute_temporality_score(vessel_track: list, origin_time_window: tuple) -> float:
    """
    Input: vessel_track; origin_time_window = (start_datetime, end_datetime).
    Output: 1.0 if any vessel position timestamp falls inside the window, decaying linearly
    to 0.0 at +/- 6 hours outside the window.
    """
    start, end = origin_time_window
    for p in vessel_track:
        t = p["timestamp"]
        if start <= t <= end:
            return 1.0
    nearest_gap_hours = min(
        abs((p["timestamp"] - start).total_seconds()) / 3600
        if p["timestamp"] < start else
        abs((p["timestamp"] - end).total_seconds()) / 3600
        for p in vessel_track
    )
    return max(0.0, 1.0 - nearest_gap_hours / 6.0)

def compute_ais_gap_score(mmsi: str, gap_events: list, origin_time_window: tuple) -> float:
    """
    Output: 1.0 if this vessel has a logged AIS-disabling event overlapping origin_time_window,
    scaled down slightly for shorter gaps, 0.0 if no gap event found for this vessel.
    """
    start, end = origin_time_window
    relevant = [g for g in gap_events if g["mmsi"] == mmsi
                and g["gap_end"] >= start and g["gap_start"] <= end]
    if not relevant:
        return 0.0
    longest_gap_hours = max(g["gap_hours"] for g in relevant)
    return min(1.0, longest_gap_hours / 4.0)  # gaps of 4+ hours score full 1.0

def compute_speed_anomaly_score(vessel_track: list) -> float:
    """
    Output: 1.0 if the vessel shows a sudden, significant slowdown (possible discharge event)
    within the track, 0.0 if speed is steady. Simple rule: if any consecutive-position speed
    drop exceeds 50% of the vessel's median speed in this window, score 1.0, else scale down.
    """
    speeds = [p.get("speed_knots", 0) for p in vessel_track if p.get("speed_knots") is not None]
    if len(speeds) < 2:
        return 0.0
    median_speed = sorted(speeds)[len(speeds)//2]
    if median_speed == 0:
        return 0.0
    max_drop_ratio = max(
        max(0.0, speeds[i] - speeds[i+1]) / median_speed
        for i in range(len(speeds)-1)
    )
    return min(1.0, max_drop_ratio)

def compute_vessel_type_prior(vessel_type: str) -> float:
    """
    Output: fixed lookup table, NOT a learned model. Tankers/cargo score higher than passenger/other.
    """
    priors = {"tanker": 0.9, "cargo": 0.7, "fishing": 0.3, "passenger": 0.1}
    return priors.get(vessel_type.lower(), 0.4)  # unknown types get a neutral-ish default
```

## STEP 8 — `scoring/scorer.py`

```python
"""
Combines the six features into one ranked, explained list. This is a HAND-REASONED HEURISTIC,
not a trained/calibrated model — see ARCHITECTURE.md §2, do not present it otherwise.
"""
from datetime import timedelta
from .ais_client import load_cached_response
from .features import (compute_proximity_score, compute_parity_score, compute_temporality_score,
                        compute_ais_gap_score, compute_speed_anomaly_score, compute_vessel_type_prior)

WEIGHTS = {
    "proximity": 0.20, "parity": 0.15, "temporality": 0.15,
    "ais_gap": 0.20, "speed_anomaly": 0.10, "vessel_type_prior": 0.20,
}
# NOTE: these weights are v1 domain-reasoned heuristics, explicitly not learned from data
# (we have no labeled ground-truth dataset — see ARCHITECTURE.md §2 and the accompanying
# critical evaluation report). Do not describe this as "calibrated" in the pitch or UI copy.

def generate_explanation(features: dict, vessel: dict) -> str:
    """Builds a short plain-English sentence from the highest-contributing features."""
    parts = []
    if features["ais_gap"] > 0.3:
        parts.append("AIS signal gap overlapping the estimated origin window")
    if features["proximity"] > 0.6:
        parts.append("passed close to the estimated origin point")
    if features["speed_anomaly"] > 0.5:
        parts.append("showed a sudden unexplained slowdown")
    if features["vessel_type_prior"] >= 0.7:
        parts.append(f"vessel type ({vessel.get('vessel_type','unknown')}) has an elevated prior likelihood")
    if not parts:
        parts.append("weak overall match on all criteria")
    return "; ".join(parts).capitalize() + "."

def rank_vessels(origin_polygon_geojson: dict, origin_time_window: tuple,
                  slick_polygon_geojson: dict, region_bbox: tuple, case_id: str = "case_1") -> list:
    """
    See exact contract in ARCHITECTURE.md §5.4.
    Uses load_cached_response() — NOT a live fetch — so the demo never depends on network access.
    """
    positions_data = load_cached_response(case_id, "positions")
    gap_events = load_cached_response(case_id, "gaps")

    results = []
    for vessel in positions_data:
        track = vessel["positions"]
        f = {
            "proximity": compute_proximity_score(track, origin_polygon_geojson),
            "parity": compute_parity_score(track, slick_polygon_geojson),
            "temporality": compute_temporality_score(track, origin_time_window),
            "ais_gap": compute_ais_gap_score(vessel["mmsi"], gap_events, origin_time_window),
            "speed_anomaly": compute_speed_anomaly_score(track),
            "vessel_type_prior": compute_vessel_type_prior(vessel.get("vessel_type", "unknown")),
        }
        final_score = sum(WEIGHTS[k] * v for k, v in f.items())
        results.append({
            "mmsi": vessel["mmsi"],
            "vessel_name": vessel.get("vessel_name", "UNKNOWN"),
            "vessel_type": vessel.get("vessel_type", "unknown"),
            "track_geojson": {"type": "LineString",
                               "coordinates": [[p["lon"], p["lat"]] for p in track]},
            "scores": f,
            "final_score": round(final_score, 3),
            "explanation": generate_explanation(f, vessel),
        })

    results.sort(key=lambda r: r["final_score"], reverse=True)
    return results
```

## STEP 9 — Tests

**`backend/tests/test_drift.py`**
- `test_run_backward_drift_missing_env_data` — call with a `case_id` that has no cached NetCDF files, assert `RuntimeError` is raised (not a crash with an unrelated stack trace).
- `test_run_backward_drift_on_demo_case` — (once real env data is cached) run against the actual demo case, assert the return dict has all required keys, `origin_polygon_geojson` is a valid GeoJSON polygon, `uncertainty_radius_km > 0`.
- `test_seeding_stays_inside_slick` — verify the particle seeding logic produces points that are actually inside the given slick polygon (regression test for the `while` loop in `run_backward_drift`).

**`backend/tests/test_scoring.py`**
- `test_compute_proximity_score_at_center` — vessel track passing exactly through the origin polygon's centroid should score close to 1.0.
- `test_compute_proximity_score_far_away` — vessel track 50km away should score 0.0.
- `test_compute_ais_gap_score_no_gap` — empty `gap_events` list returns 0.0.
- `test_compute_ais_gap_score_overlapping_gap` — a gap event overlapping the time window returns > 0.
- `test_compute_vessel_type_prior_known_and_unknown` — check both a known type ("tanker") and an unrecognized string default to sensible values.
- `test_rank_vessels_sorted_descending` — build a small fake cached response (2-3 vessels), assert `rank_vessels()` output is sorted by `final_score` descending.
- `test_rank_vessels_empty_data` — empty cached vessel list returns `[]`, not an exception.

---

## STEP 10 — Git workflow for your branch

```bash
git add app/physics/ app/scoring/ tests/test_drift.py tests/test_scoring.py requirements.txt data/raw/README.md data/demo_cases/case_1/ais_cache_positions.json data/demo_cases/case_1/ais_cache_gaps.json
git commit -m "[physics+scoring] add drift model and vessel scoring pipeline"
git push -u origin person3/physics-scoring-setup
```
Open PRs incrementally (AIS client → environmental data → drift model → features → scorer) rather than one giant PR. Title each `[physics]` or `[scoring]` accordingly. Person 1 reviews and merges.

Before starting new work each day: `git checkout main && git pull origin main && git checkout person3/physics-scoring-setup && git rebase main`.

---

## Completion Checklist

- [ ] Repository cloned, branch created
- [ ] GFW, CMEMS, CDS accounts set up, API keys stored (never committed)
- [ ] OpenDrift "hello world" tutorial run successfully before touching real data
- [ ] `scoring/ais_client.py` implemented against verified current GFW API docs
- [ ] Real AIS positions + gap events fetched for the demo case and cached to disk, committed
- [ ] `physics/environmental_data.py` implemented; CMEMS + ERA5 files downloaded and cached for the demo case
- [ ] `physics/drift_model.py` implemented, verified to return the exact §5.3 contract shape on the real demo case
- [ ] `scoring/features.py` — all six scoring functions implemented
- [ ] `scoring/scorer.py` implemented, verified to return the exact §5.4 contract shape, uses cached (not live) data
- [ ] `tests/test_drift.py` and `tests/test_scoring.py` written and passing
- [ ] Code committed, branch pushed, PR(s) created and merged
- [ ] Person 1 notified that `physics/drift_model.py` and `scoring/scorer.py` are ready for orchestrator integration (STEP 13 in PERSON_1.md)
