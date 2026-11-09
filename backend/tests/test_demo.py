"""
Integration tests for the nationwide demonstration layer:
  • GET  /api/demo/scenarios
  • GET  /api/demo/scenario/{id}
  • GET  /api/demo/regions
  • POST /api/demo/reset

All scenario records must carry provenance='SIMULATED_DEMO', cross-reference
correctly, and reset repeatedly without duplicating rows or deleting genuine
project cases.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

EXPECTED_SCENARIOS = {
    "mumbai_high": "Mumbai High",
    "gujarat_corridor": "Gujarat Offshore Corridor",
    "paradip": "Paradip",
    "kerala_coast": "Kerala Coast",
    "andaman": "Andaman & Nicobar",
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_list_demo_scenarios(client):
    response = client.get("/api/demo/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

    by_id = {item["id"]: item for item in data}
    assert set(by_id) == set(EXPECTED_SCENARIOS)

    for scenario_id, name in EXPECTED_SCENARIOS.items():
        item = by_id[scenario_id]
        assert item["name"] == name
        assert item["provenance"] == "SIMULATED_DEMO"
        assert item["region_id"].startswith("IN-")
        assert len(item["bbox"]) == 4
        assert len(item["center"]) == 2
        assert item["stats"]["scenes"] > 0
        assert item["stats"]["detections"] > 0
        assert item["stats"]["vessels"] > 0
        assert item["stats"]["incidents"] > 0


def test_regions_endpoint_lists_all_13_coastal_zones(client):
    response = client.get("/api/demo/regions")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 13
    assert payload["states"] == 9
    assert payload["union_territories"] == 4

    zones = payload["zones"]
    assert len(zones) == 13
    ids = {z["id"] for z in zones}
    assert len(ids) == 13
    assert {"IN-GJ", "IN-MH", "IN-KL", "IN-TN", "IN-OD", "IN-WB", "IN-AN"} <= ids

    for zone in zones:
        assert len(zone["bbox"]) == 4
        assert zone["bbox"][0] < zone["bbox"][2]
        assert zone["bbox"][1] < zone["bbox"][3]
        assert zone["boundary_status"] == "PROVISIONAL_SEARCH_ENVELOPE"
        assert zone["name"]


def test_scenario_bundle_cross_references_and_provenance(client):
    for scenario_id in EXPECTED_SCENARIOS:
        response = client.get(f"/api/demo/scenario/{scenario_id}")
        assert response.status_code == 200, scenario_id
        bundle = response.json()

        assert bundle["scenario"]["id"] == scenario_id
        assert bundle["scenario"]["provenance"] == "SIMULATED_DEMO"
        assert bundle["stats"]["scenes"] == len(bundle["scenes"])

        for key in ("scenes", "detections", "vessels", "drift", "incidents"):
            assert bundle[key], f"{scenario_id}/{key} must not be empty"
            for record in bundle[key]:
                assert record["provenance"] == "SIMULATED_DEMO", f"{scenario_id}/{key}"

        scene_ids = {s["id"] for s in bundle["scenes"]}
        detection_ids = {d["id"] for d in bundle["detections"]}
        vessel_ids = {v["vessel_id"] for v in bundle["vessels"]}

        for det in bundle["detections"]:
            assert det["scene_id"] in scene_ids
            assert det["confidence"] > 0
            assert det["area_sqkm"] > 0

        for vessel in bundle["vessels"]:
            assert vessel["detection_id"] in detection_ids
            assert vessel["mmsi"]
            assert 0 < vessel["attribution_score"] <= 1

        for drift in bundle["drift"]:
            assert drift["detection_id"] in detection_ids
            assert len(drift["trajectories"]) >= 2
            assert drift["origin_polygon"]["properties"]["provenance"] == "SIMULATED_DEMO"

        for incident in bundle["incidents"]:
            assert incident["scene_id"] in scene_ids
            assert incident["detection_id"] in detection_ids
            assert incident["vessel_id"] in vessel_ids


def test_scenario_not_found(client):
    response = client.get("/api/demo/scenario/does_not_exist")
    assert response.status_code == 404


def test_reset_is_repeatable_and_preserves_real_cases(client):
    real_before = [
        case
        for case in client.get("/api/cases").json()
        if not case["name"].startswith("scene_")
    ]

    first = client.post("/api/demo/reset")
    assert first.status_code == 200, first.text
    first_payload = first.json()
    assert first_payload["status"] == "ok"
    assert first_payload["provenance"] == "SIMULATED_DEMO"
    assert len(first_payload["scenarios_loaded"]) == 5
    assert first_payload["totals"]["scenarios"] == 5
    assert first_payload["totals"]["scenes"] == 10

    first_counts = first_payload["database"]
    assert first_counts["demo_cases"] == 10
    assert first_counts["demo_detections"] == 10
    assert first_counts["demo_vessels"] == 15
    assert first_counts["demo_drift_results"] == 10

    # A second reset must replace, not duplicate.
    second = client.post("/api/demo/reset")
    assert second.status_code == 200, second.text
    second_payload = second.json()
    assert second_payload["database"] == first_counts

    # Genuine benchmark cases are untouched.
    real_after = [
        case
        for case in client.get("/api/cases").json()
        if not case["name"].startswith("scene_")
    ]
    assert real_after == real_before

    # Simulated demo cases are isolated from the live case pipeline API.
    all_cases = client.get("/api/cases").json()
    assert all(not c["name"].startswith("scene_") for c in all_cases)
    assert all("SIMULATED_DEMO" not in (c.get("description") or "") for c in all_cases)
    assert len(all_cases) == len(real_before)
