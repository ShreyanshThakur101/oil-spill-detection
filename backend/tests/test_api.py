"""
Integration tests for FastAPI endpoints.
Tests health, cases, pipeline execution, Nugen inference, scientific benchmarks, and legal dossiers.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.pipeline.seed import seed_cases_from_disk


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    seed_cases_from_disk()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_cases(client):
    response = client.get("/api/cases")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Both Kochi (Case 1) and Mumbai (Case 2) must be present per presentation Slide 10
    assert len(data) >= 2
    names = [c["name"] for c in data]
    assert any("Kochi" in n or "MSC Elsa" in n for n in names)
    assert any("Mumbai" in n for n in names)


def test_get_case_detail(client):
    cases = client.get("/api/cases").json()
    case_id = cases[0]["id"]
    response = client.get(f"/api/cases/{case_id}")
    assert response.status_code == 200
    case_data = response.json()
    assert case_data["id"] == case_id
    assert "bbox" in case_data


def test_run_pipeline_kochi(client):
    cases = client.get("/api/cases").json()
    case_id = cases[0]["id"]
    response = client.post(f"/api/cases/{case_id}/run")
    assert response.status_code == 200
    payload = response.json()
    assert "detection" in payload
    assert "drift" in payload
    assert "vessels" in payload
    assert "nugen" in payload
    assert "dossier" in payload

    # Detection structure check
    assert "polygon_geojson" in payload["detection"]
    assert "confidence" in payload["detection"]
    assert "shape_features" in payload["detection"]

    # Drift structure check (200 particles, 18 hours)
    assert "origin_polygon_geojson" in payload["drift"]
    assert "uncertainty_radius_km" in payload["drift"]
    assert payload["drift"]["particle_count"] == 200
    assert "particle_cloud_geojson" in payload["drift"]
    assert "particle_trajectories_geojson" in payload["drift"]

    # Vessels list check (MSC Elsa III primary suspect)
    vessels = payload["vessels"]
    assert isinstance(vessels, list)
    assert len(vessels) > 0
    top_vessel = vessels[0]
    assert top_vessel["mmsi"] == "354892000"
    assert top_vessel["vessel_name"] == "MSC ELSA III"
    assert top_vessel["final_score"] >= 0.90
    assert top_vessel["ais_gap_duration_mins"] == 42
    assert top_vessel["speed_drop_knots"] == 6.8
    assert "explanation" in top_vessel


def test_nugen_benchmark_endpoint(client):
    response = client.get("/api/nugen/benchmark")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert data["metrics"]["statutory_hallucination"]["nugen_aligned_pct"] == 0.0
    assert data["metrics"]["attribution_specificity"]["delta_pct"] == 38.5
    assert "comparative_prompt_example" in data


def test_nugen_inference_endpoint(client):
    payload = {
        "model": "nugen-maritime-aligned-phi3",
        "domain": "indian_eez_enforcement",
        "slick_coords": [9.9312, 76.2673],
        "spill_timestamp": "2025-05-24T14:30:00Z",
        "suspect_vessel": {
            "mmsi": 354892000,
            "name": "CARGO_ALPHA",
            "ais_gap_duration_mins": 42,
            "speed_drop_knots": 6.8,
            "drift_overlap_confidence": 0.942
        },
        "jurisdiction": "Merchant_Shipping_Act_1958"
    }
    response = client.post("/api/nugen/inference", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert "output_text" in res
    assert "356E" in res["output_text"]
    assert "356J" in res["output_text"]


def test_get_case_dossier(client):
    cases = client.get("/api/cases").json()
    case_id = cases[0]["id"]
    response = client.post(f"/api/cases/{case_id}/dossier")
    assert response.status_code == 200
    dossier = response.json()
    assert "dossier_id" in dossier
    assert "section_1_satellite_radar" in dossier
    assert "section_2_drift_physics" in dossier
    assert "section_3_vessel_behavioral_telemetry" in dossier
    assert "section_4_statutory_citations" in dossier
    assert "section_5_enforcement_orders" in dossier
