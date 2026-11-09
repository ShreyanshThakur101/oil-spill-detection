"""
Nationwide demo fixture loader and SQLite seeding utility.

Every record in ``backend/data/demo/<scenario>/`` is synthetic and MUST carry
``provenance: "SIMULATED_DEMO"``. This module is the single source of truth for
reading scenarios, computing dashboard statistics, validating cross-references
and loading fixtures into the existing SQLAlchemy models.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from sqlalchemy.orm import Session

from .config import DATA_DIR
from .models import Case, DriftResult, SlickDetection, VesselScore
from .regions import get_zone_by_id

DEMO_BASE: Path = DATA_DIR / "demo"
FIXTURE_FILES: Tuple[str, ...] = (
    "scenes.json",
    "detections.json",
    "vessels.json",
    "drift.json",
    "incidents.json",
)
PROVENANCE = "SIMULATED_DEMO"

# Canonical demo scenarios → Indian coastal surveillance zone.
SCENARIO_META: Dict[str, Dict[str, str]] = {
    "mumbai_high": {
        "name": "Mumbai High",
        "region_id": "IN-MH",
        "summary": "Offshore crude oil field and tanker corridor west of Mumbai.",
    },
    "gujarat_corridor": {
        "name": "Gujarat Offshore Corridor",
        "region_id": "IN-GJ",
        "summary": "Hazira–Vadinar tanker corridor in the Gulf of Khambhat.",
    },
    "paradip": {
        "name": "Paradip",
        "region_id": "IN-OD",
        "summary": "Paradip crude tanker anchorages and approach fairways, Odisha.",
    },
    "kerala_coast": {
        "name": "Kerala Coast",
        "region_id": "IN-KL",
        "summary": "Kochi port approaches and the Malabar coastal shipping lane.",
    },
    "andaman": {
        "name": "Andaman & Nicobar",
        "region_id": "IN-AN",
        "summary": "Port Blair approaches and the Six Degree Channel tanker route.",
    },
}


# ---------------------------------------------------------------------------
# Reading and validation
# ---------------------------------------------------------------------------
def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def scenario_dirs() -> List[Path]:
    if not DEMO_BASE.exists():
        return []
    return sorted(d for d in DEMO_BASE.iterdir() if d.is_dir())


def load_bundle(scenario_id: str) -> Dict[str, Any]:
    """Load the five fixture files for a scenario, raising ValueError if invalid."""
    path = DEMO_BASE / scenario_id
    if not path.is_dir():
        raise FileNotFoundError(scenario_id)

    bundle: Dict[str, Any] = {}
    for fname in FIXTURE_FILES:
        fp = path / fname
        if not fp.is_file():
            raise ValueError(f"Missing {fname} in scenario '{scenario_id}'")
        bundle[fname[:-5]] = read_json(fp)

    validate_bundle(scenario_id, bundle)
    return bundle


def _require_provenance(records: List[Dict[str, Any]], label: str) -> None:
    for record in records:
        if not isinstance(record, dict):
            raise ValueError(f"{label}: every record must be a JSON object")
        if record.get("provenance") != PROVENANCE:
            raise ValueError(
                f"{label}: record {record.get('id') or record.get('incident_id') or '?'} "
                f"must carry provenance='{PROVENANCE}'"
            )


def validate_bundle(scenario_id: str, bundle: Dict[str, Any]) -> None:
    """Ensure every synthetic record has provenance and all IDs resolve."""
    for key in ("scenes", "detections", "vessels", "drift", "incidents"):
        records = bundle.get(key)
        if not isinstance(records, list) or not records:
            raise ValueError(f"Scenario '{scenario_id}' has no {key} records")
        _require_provenance(records, f"{scenario_id}/{key}")

    scene_ids = {s["id"] for s in bundle["scenes"]}
    detection_ids = {d["id"] for d in bundle["detections"]}
    vessel_ids = {v["vessel_id"] for v in bundle["vessels"]}

    for det in bundle["detections"]:
        if det.get("scene_id") not in scene_ids:
            raise ValueError(f"{scenario_id}: detection {det['id']} references unknown scene")
    for vessel in bundle["vessels"]:
        if vessel.get("detection_id") not in detection_ids:
            raise ValueError(f"{scenario_id}: vessel {vessel['vessel_id']} references unknown detection")
    for drift in bundle["drift"]:
        if drift.get("detection_id") not in detection_ids:
            raise ValueError(f"{scenario_id}: drift references unknown detection")
    for incident in bundle["incidents"]:
        if incident.get("scene_id") not in scene_ids:
            raise ValueError(f"{scenario_id}: incident {incident['incident_id']} references unknown scene")
        if incident.get("detection_id") not in detection_ids:
            raise ValueError(f"{scenario_id}: incident {incident['incident_id']} references unknown detection")
        if incident.get("vessel_id") not in vessel_ids:
            raise ValueError(f"{scenario_id}: incident {incident['incident_id']} references unknown vessel")


# ---------------------------------------------------------------------------
# Dashboard metadata & statistics
# ---------------------------------------------------------------------------
def compute_stats(bundle: Dict[str, Any]) -> Dict[str, Any]:
    detections = bundle.get("detections", [])
    vessels = bundle.get("vessels", [])
    incidents = bundle.get("incidents", [])
    scenes = bundle.get("scenes", [])
    drift = bundle.get("drift", [])

    confidences = [d.get("confidence", 0) for d in detections if d.get("confidence") is not None]
    areas = [d.get("area_sqkm", 0) for d in detections if d.get("area_sqkm") is not None]
    scores = [v.get("attribution_score", 0) for v in vessels if v.get("attribution_score") is not None]
    open_incidents = [i for i in incidents if str(i.get("status", "")).upper() == "OPEN"]

    return {
        "scenes": len(scenes),
        "detections": len(detections),
        "vessels": len(vessels),
        "incidents": len(incidents),
        "open_incidents": len(open_incidents),
        "drift_predictions": len(drift),
        "total_area_sqkm": round(sum(areas), 2),
        "max_confidence": round(max(confidences), 3) if confidences else None,
        "top_attribution_score": round(max(scores), 3) if scores else None,
        "provenance": PROVENANCE,
    }


def scenario_summary(scenario_id: str) -> Dict[str, Any]:
    bundle = load_bundle(scenario_id)
    meta = SCENARIO_META.get(scenario_id, {})
    region = get_zone_by_id(meta.get("region_id", "")) if meta.get("region_id") else None

    # Bounding box is the union of scene envelopes so the map can focus.
    bboxes = [s.get("bbox") for s in bundle["scenes"] if s.get("bbox")]
    if bboxes:
        bbox = [
            min(b[0] for b in bboxes),
            min(b[1] for b in bboxes),
            max(b[2] for b in bboxes),
            max(b[3] for b in bboxes),
        ]
    else:
        bbox = region.get("bbox") if region else [68.0, 6.0, 97.0, 24.0]

    center = [round((bbox[1] + bbox[3]) / 2, 4), round((bbox[0] + bbox[2]) / 2, 4)]

    return {
        "id": scenario_id,
        "name": meta.get("name", scenario_id.replace("_", " ").title()),
        "summary": meta.get("summary", ""),
        "region_id": meta.get("region_id"),
        "region_name": region.get("name") if region else None,
        "coast": region.get("coast") if region else None,
        "primary_mrcc": region.get("primary_mrcc") if region else None,
        "bbox": bbox,
        "center": center,  # [lat, lon] for Leaflet
        "stats": compute_stats(bundle),
        "provenance": PROVENANCE,
    }


def list_scenarios() -> List[Dict[str, Any]]:
    summaries = []
    # Present scenarios in the canonical demonstration order first.
    ordered = [
        DEMO_BASE / scenario_id
        for scenario_id in SCENARIO_META
        if (DEMO_BASE / scenario_id).is_dir()
    ]
    extras = [d for d in scenario_dirs() if d.name not in SCENARIO_META]
    for directory in ordered + extras:
        try:
            summaries.append(scenario_summary(directory.name))
        except (ValueError, KeyError) as exc:  # keep the dashboard usable
            summaries.append(
                {
                    "id": directory.name,
                    "name": directory.name.replace("_", " ").title(),
                    "error": str(exc),
                    "provenance": PROVENANCE,
                }
            )
    return summaries


# ---------------------------------------------------------------------------
# SQLite seeding
# ---------------------------------------------------------------------------
def is_simulated_case(case: Case) -> bool:
    """True when a Case row was created by the SIMULATED_DEMO seeder."""
    return (case.description or "").startswith(f"[{PROVENANCE}]")


def _parse_ts(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    text = str(value).replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def _with_provenance(geojson: Dict[str, Any] | None, **extra: Any) -> Dict[str, Any] | None:
    """Return a copy of a GeoJSON Feature with provenance in its properties."""
    if not geojson:
        return geojson
    feature = json.loads(json.dumps(geojson))
    props = feature.setdefault("properties", {})
    props["provenance"] = PROVENANCE
    props.update(extra)
    return feature


def _demo_case_ids(db: Session) -> List[int]:
    """Identify only the synthetic demo cases; real cases are never touched.

    The ``[SIMULATED_DEMO]`` description prefix is written exclusively by this
    seeder, so it is a safer marker than the scenario naming convention.
    """
    demo_cases = (
        db.query(Case)
        .filter(Case.description.like(f"[{PROVENANCE}]%"))
        .all()
    )
    return [c.id for c in demo_cases]


def _delete_demo_rows(db: Session) -> int:
    ids = _demo_case_ids(db)
    if ids:
        db.query(DriftResult).filter(DriftResult.case_id.in_(ids)).delete(synchronize_session=False)
        db.query(VesselScore).filter(VesselScore.case_id.in_(ids)).delete(synchronize_session=False)
        db.query(SlickDetection).filter(SlickDetection.case_id.in_(ids)).delete(synchronize_session=False)
        db.query(Case).filter(Case.id.in_(ids)).delete(synchronize_session=False)
    return len(ids)


def seed_demo_data(db: Session) -> Dict[str, Any]:
    """
    Delete previously seeded demo rows and reload every scenario fixture.

    The operation is repeatable (no duplicate rows), transactional, and scoped
    strictly to records marked ``[SIMULATED_DEMO]`` / ``scene_*`` names.
    All fixtures are validated *before* anything is deleted.
    """
    scenarios: List[Tuple[str, Dict[str, Any]]] = []
    for directory in scenario_dirs():
        scenarios.append((directory.name, load_bundle(directory.name)))
    if not scenarios:
        return {"status": "ok", "scenarios_loaded": [], "totals": {}}

    removed = 0
    loaded: List[Dict[str, Any]] = []
    try:
        removed = _delete_demo_rows(db)

        for scenario_id, bundle in scenarios:
            meta = SCENARIO_META.get(scenario_id, {})
            display_name = meta.get("name", scenario_id)

            scene_to_case: Dict[str, int] = {}
            for scene in bundle["scenes"]:
                case = Case(
                    name=scene["id"],
                    description=f"[{PROVENANCE}] {display_name} / {scenario_id} — {scene['id']}",
                    sar_image_path=f"demo/{scenario_id}/{scene['id']}.tif",
                    image_timestamp=_parse_ts(scene["timestamp"]),
                    bbox=scene.get("bbox"),
                )
                db.add(case)
                db.flush()
                scene_to_case[scene["id"]] = case.id

            detection_to_pk: Dict[str, int] = {}
            detection_to_scene: Dict[str, str] = {}
            for det in bundle["detections"]:
                scene_id = det["scene_id"]
                detection_to_scene[det["id"]] = scene_id
                slick = SlickDetection(
                    case_id=scene_to_case[scene_id],
                    polygon_geojson=_with_provenance(
                        det.get("polygon") or det.get("polygon_geojson"),
                        detection_id=det["id"],
                        scenario_id=scenario_id,
                        sector=det.get("sector"),
                    ),
                    confidence=det.get("confidence"),
                    area_km2=det.get("area_sqkm"),
                    perimeter_km=det.get("perimeter_km"),
                    elongation=det.get("elongation"),
                    fragment_count=det.get("fragment_count"),
                    age_class=det.get("age_class"),
                )
                db.add(slick)
                db.flush()
                detection_to_pk[det["id"]] = slick.id

            for vessel in bundle["vessels"]:
                det_id = vessel["detection_id"]
                case_id = scene_to_case[detection_to_scene[det_id]]
                db.add(
                    VesselScore(
                        case_id=case_id,
                        mmsi=str(vessel.get("mmsi") or vessel.get("vessel_id", "")),
                        vessel_name=vessel.get("name"),
                        vessel_type=vessel.get("type"),
                        track_geojson=_with_provenance(
                            vessel.get("track_geojson"),
                            vessel_id=vessel.get("vessel_id"),
                            scenario_id=scenario_id,
                        ),
                        scores_json={
                            "provenance": PROVENANCE,
                            "scenario_id": scenario_id,
                            "vessel_id": vessel.get("vessel_id"),
                            "detection_id": det_id,
                            "rank": vessel.get("rank"),
                            "flag": vessel.get("flag"),
                            "flag_name": vessel.get("flag_name"),
                            "call_sign": vessel.get("call_sign"),
                            "drift_overlap_confidence": vessel.get("drift_overlap_confidence"),
                            "ais_gap_minutes": vessel.get("ais_gap_minutes"),
                            "speed_drop_knots": vessel.get("speed_drop_knots"),
                            "destination": vessel.get("destination"),
                        },
                        final_score=vessel.get("attribution_score"),
                        explanation=(
                            f"[{PROVENANCE}] Rank {vessel.get('rank')} synthetic attribution for "
                            f"{vessel.get('name')} ({vessel.get('flag_name') or vessel.get('flag') or 'unknown flag'}) "
                            f"based on drift-cone overlap, AIS gap and speed anomaly."
                        ),
                    )
                )

            for drift in bundle["drift"]:
                det_id = drift["detection_id"]
                trajectories = drift.get("trajectories") or []
                origin_time = drift.get("estimated_origin_time") or (
                    trajectories[0]["timestamp"] if trajectories else "2025-01-01T00:00:00Z"
                )
                db.add(
                    DriftResult(
                        case_id=scene_to_case[detection_to_scene[det_id]],
                        detection_id=detection_to_pk[det_id],
                        origin_polygon_geojson=_with_provenance(
                            drift.get("origin_polygon"),
                            detection_id=det_id,
                            scenario_id=scenario_id,
                        ),
                        estimated_origin_time=_parse_ts(origin_time),
                        uncertainty_radius_km=drift.get("uncertainty_km"),
                    )
                )

            db.flush()
            loaded.append(
                {
                    "id": scenario_id,
                    "name": display_name,
                    "scenes": len(bundle["scenes"]),
                    "detections": len(bundle["detections"]),
                    "vessels": len(bundle["vessels"]),
                    "drift": len(bundle["drift"]),
                    "incidents": len(bundle["incidents"]),
                }
            )

        db.commit()
    except Exception:
        db.rollback()
        raise

    demo_filter = Case.description.like(f"[{PROVENANCE}]%")
    db_counts = {
        "demo_cases": db.query(Case).filter(demo_filter).count(),
        "demo_detections": (
            db.query(SlickDetection)
            .join(Case, SlickDetection.case_id == Case.id)
            .filter(demo_filter)
            .count()
        ),
        "demo_vessels": (
            db.query(VesselScore)
            .join(Case, VesselScore.case_id == Case.id)
            .filter(demo_filter)
            .count()
        ),
        "demo_drift_results": (
            db.query(DriftResult)
            .join(Case, DriftResult.case_id == Case.id)
            .filter(demo_filter)
            .count()
        ),
    }

    return {
        "status": "ok",
        "provenance": PROVENANCE,
        "removed_demo_cases": removed,
        "scenarios_loaded": loaded,
        "totals": {
            "scenarios": len(loaded),
            "scenes": sum(item["scenes"] for item in loaded),
            "detections": sum(item["detections"] for item in loaded),
            "vessels": sum(item["vessels"] for item in loaded),
            "drift": sum(item["drift"] for item in loaded),
            "incidents": sum(item["incidents"] for item in loaded),
        },
        "database": db_counts,
    }
