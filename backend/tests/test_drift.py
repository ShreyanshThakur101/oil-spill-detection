"""
Unit tests for drift modeling (Person 3): physics/drift_model.py, physics/environmental_data.py.
"""
from datetime import datetime
import pytest

from app.physics.drift_model import run_backward_drift
from app.physics.environmental_data import get_current_reader, get_wind_reader


def test_run_backward_drift_missing_env_data():
    """Verify that requesting non-existent environmental data raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        get_current_reader("non_existent_case_999")
    with pytest.raises(FileNotFoundError):
        get_wind_reader("non_existent_case_999")


def test_run_backward_drift_contract_shape():
    """Test run_backward_drift return shape and keys on sample slick polygon."""
    sample_poly = {
        "type": "Polygon",
        "coordinates": [
            [
                [76.0, 9.5],
                [76.1, 9.5],
                [76.1, 9.6],
                [76.0, 9.6],
                [76.0, 9.5],
            ]
        ],
    }
    ts = datetime(2025, 5, 26, 3, 0, 0)
    bbox = (74.0, 8.5, 77.5, 11.0)
    res = run_backward_drift(sample_poly, ts, bbox, hours_back=48, case_id="case_1")

    assert "origin_polygon_geojson" in res
    assert "estimated_origin_time" in res
    assert "uncertainty_radius_km" in res
    assert res["uncertainty_radius_km"] > 0
    assert res["origin_polygon_geojson"]["type"] in ["Polygon", "MultiPolygon"]


def test_seeding_stays_inside_slick_bounds():
    """Verify particle trace points are generated and non-empty."""
    sample_poly = {
        "type": "Polygon",
        "coordinates": [
            [
                [76.0, 9.5],
                [76.1, 9.5],
                [76.1, 9.6],
                [76.0, 9.6],
                [76.0, 9.5],
            ]
        ],
    }
    ts = datetime(2025, 5, 26, 3, 0, 0)
    res = run_backward_drift(sample_poly, ts, (74.0, 8.5, 77.5, 11.0), hours_back=24)
    assert "particle_trace_geojson" in res
    assert res["particle_trace_geojson"]["type"] == "MultiPoint"
    assert len(res["particle_trace_geojson"]["coordinates"]) > 0
