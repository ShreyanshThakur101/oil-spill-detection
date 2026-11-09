"""
Demo router — nationwide simulated demonstration scenarios.

Endpoints
---------
GET  /api/demo/scenarios        List the five demo scenarios with statistics.
GET  /api/demo/scenario/{id}    Full fixture bundle for one scenario.
GET  /api/demo/regions          All 13 Indian coastal states / coastal UTs.
POST /api/demo/reset            Reload fixtures into SQLite (repeatable).

All demo records carry ``provenance: "SIMULATED_DEMO"``.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..demo_data import (
    PROVENANCE,
    compute_stats,
    list_scenarios,
    load_bundle,
    scenario_summary,
    seed_demo_data,
)
from ..regions import get_all_zones

router = APIRouter(tags=["Nationwide Demo"])


@router.get("/demo/scenarios")
def get_scenarios():
    """List the five demonstration scenarios and their aggregate statistics."""
    return list_scenarios()


@router.get("/demo/regions")
def get_regions():
    """All 9 coastal states and 4 coastal Union Territories (13 zones)."""
    zones = []
    for zone in get_all_zones():
        item = dict(zone)
        item["boundary_status"] = "PROVISIONAL_SEARCH_ENVELOPE"
        item["provenance"] = "PROVISIONAL_REFERENCE"
        zones.append(item)
    return {
        "count": len(zones),
        "states": sum(1 for z in zones if z["type"] == "STATE"),
        "union_territories": sum(1 for z in zones if z["type"] == "UNION_TERRITORY"),
        "zones": zones,
    }


@router.get("/demo/scenario/{scenario_id}")
def get_scenario(scenario_id: str):
    """Return all five fixture bundles plus dashboard metadata for a scenario."""
    try:
        bundle = load_bundle(scenario_id)
        summary = scenario_summary(scenario_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "scenario": summary,
        "stats": compute_stats(bundle),
        **bundle,
    }


@router.post("/demo/reset")
def reset_demo(db: Session = Depends(get_db)):
    """
    Reload every demo fixture into the SQLite database.

    Repeatable and transactional. Only rows previously created by the demo
    seeder are removed; genuine project cases are preserved.
    """
    try:
        result = seed_demo_data(db)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid demo fixture: {exc}")
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Demo reset failed: {exc}")

    return {**result, "provenance": PROVENANCE}
