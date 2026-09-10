"""
Unit tests for vessel scoring and attribution (Person 3): scoring/features.py, scoring/scorer.py.
"""
from datetime import datetime, timezone
import pytest

from app.scoring.features import (
    compute_ais_gap_score,
    compute_parity_score,
    compute_proximity_score,
    compute_speed_anomaly_score,
    compute_temporality_score,
    compute_vessel_type_prior,
)
from app.scoring.scorer import generate_explanation, rank_vessels


def test_compute_proximity_score_at_center():
    origin_poly = {
        "type": "Polygon",
        "coordinates": [
            [[75.9, 9.4], [76.1, 9.4], [76.1, 9.6], [75.9, 9.6], [75.9, 9.4]]
        ],
    }
    # Track passing right through centroid (76.0, 9.5)
    vessel_track = [{"lat": 9.5, "lon": 76.0, "timestamp": "2025-05-25T22:00:00Z"}]
    score = compute_proximity_score(vessel_track, origin_poly)
    assert score >= 0.95


def test_compute_proximity_score_far_away():
    origin_poly = {
        "type": "Polygon",
        "coordinates": [
            [[75.9, 9.4], [76.1, 9.4], [76.1, 9.6], [75.9, 9.6], [75.9, 9.4]]
        ],
    }
    # Track 100km+ away
    vessel_track = [{"lat": 11.0, "lon": 74.0, "timestamp": "2025-05-25T22:00:00Z"}]
    score = compute_proximity_score(vessel_track, origin_poly)
    assert score == 0.0


def test_compute_ais_gap_score_no_gap():
    window = (datetime(2025, 5, 25, 20, 0), datetime(2025, 5, 26, 2, 0))
    score = compute_ais_gap_score("123456789", [], window)
    assert score == 0.0


def test_compute_ais_gap_score_overlapping_gap():
    window = (datetime(2025, 5, 25, 20, 0), datetime(2025, 5, 26, 2, 0))
    gaps = [
        {
            "mmsi": "412345678",
            "gap_start": "2025-05-25T21:00:00Z",
            "gap_end": "2025-05-25T23:30:00Z",
            "gap_hours": 2.5,
        }
    ]
    score = compute_ais_gap_score("412345678", gaps, window)
    assert score > 0.5


def test_compute_vessel_type_priors():
    assert compute_vessel_type_prior("tanker") > compute_vessel_type_prior("fishing")
    assert compute_vessel_type_prior("unknown_type") == 0.40


def test_rank_vessels_demo_case():
    origin_poly = {
        "type": "Polygon",
        "coordinates": [
            [[75.8, 9.3], [76.0, 9.3], [76.0, 9.5], [75.8, 9.5], [75.8, 9.3]]
        ],
    }
    slick_poly = {
        "type": "Polygon",
        "coordinates": [
            [[76.0, 9.5], [76.1, 9.5], [76.1, 9.6], [76.0, 9.6], [76.0, 9.5]]
        ],
    }
    window = (datetime(2025, 5, 25, 18, 0), datetime(2025, 5, 26, 6, 0))
    results = rank_vessels(origin_poly, window, slick_poly, (74.0, 8.5, 77.5, 11.0), case_id="case_1")

    assert len(results) > 0
    # Verify sorted descending
    scores = [r["final_score"] for r in results]
    assert scores == sorted(scores, reverse=True)
    # Check top suspect has full explanation
    assert "explanation" in results[0]
    assert len(results[0]["explanation"]) > 10
