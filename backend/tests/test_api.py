"""
Integration tests for FastAPI endpoints.
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
    assert len(data) >= 1
    assert "name" in data[0]


def test_get_case_detail(client):
    cases = client.get("/api/cases").json()
    case_id = cases[0]["id"]
    response = client.get(f"/api/cases/{case_id}")
    assert response.status_code == 200
    case_data = response.json()
    assert case_data["id"] == case_id
    assert "bbox" in case_data


def test_run_pipeline_mock(client):
    cases = client.get("/api/cases").json()
    case_id = cases[0]["id"]
    response = client.post(f"/api/cases/{case_id}/run")
    assert response.status_code == 200
    payload = response.json()
    assert "detection" in payload
    assert "drift" in payload
    assert "vessels" in payload

    # Detection structure check
    assert "polygon_geojson" in payload["detection"]
    assert "confidence" in payload["detection"]
    assert "shape_features" in payload["detection"]

    # Drift structure check
    assert "origin_polygon_geojson" in payload["drift"]
    assert "uncertainty_radius_km" in payload["drift"]

    # Vessels list check
    vessels = payload["vessels"]
    assert isinstance(vessels, list)
    assert len(vessels) > 0
    top_vessel = vessels[0]
    assert "mmsi" in top_vessel
    assert "final_score" in top_vessel
    assert "scores" in top_vessel
    assert "explanation" in top_vessel
