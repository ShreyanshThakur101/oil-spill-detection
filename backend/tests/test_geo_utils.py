"""
Unit tests for backend.app.utils.geo.
"""
import pytest
from app.utils.geo import (
    bbox_from_polygon,
    geojson_polygon_from_mask,
    haversine_distance_km,
    polygon_area_km2,
    polygon_elongation,
    polygon_perimeter_km,
)


def test_haversine_distance():
    # Mumbai (72.8777, 19.0760) to Goa (73.8180, 15.2993)
    dist = haversine_distance_km((72.8777, 19.0760), (73.8180, 15.2993))
    assert 420.0 < dist < 450.0
    # Zero distance
    assert haversine_distance_km((75.0, 10.0), (75.0, 10.0)) == 0.0


def test_polygon_metrics():
    # Synthetic square near equator ~0.1 deg (~11.1 km x 11.1 km)
    square_geojson = {
        "type": "Polygon",
        "coordinates": [
            [
                [75.0, 10.0],
                [75.1, 10.0],
                [75.1, 10.1],
                [75.0, 10.1],
                [75.0, 10.0]
            ]
        ]
    }
    area = polygon_area_km2(square_geojson)
    assert 110.0 < area < 130.0  # ~120 km^2

    perim = polygon_perimeter_km(square_geojson)
    assert 40.0 < perim < 50.0   # ~44 km

    elongation = polygon_elongation(square_geojson)
    assert 1.0 <= elongation < 1.15  # Square is close to 1.0


def test_elongated_polygon():
    # Long rectangle
    elongated_geojson = {
        "type": "Polygon",
        "coordinates": [
            [
                [75.0, 10.0],
                [75.5, 10.0],
                [75.5, 10.05],
                [75.0, 10.05],
                [75.0, 10.0]
            ]
        ]
    }
    elongation = polygon_elongation(elongated_geojson)
    assert elongation > 5.0


def test_bbox_from_polygon():
    poly = {
        "type": "Polygon",
        "coordinates": [
            [
                [75.0, 10.0],
                [75.2, 10.0],
                [75.2, 10.2],
                [75.0, 10.2],
                [75.0, 10.0]
            ]
        ]
    }
    min_lon, min_lat, max_lon, max_lat = bbox_from_polygon(poly, buffer_km=10.0)
    assert min_lon < 75.0
    assert max_lon > 75.2
    assert min_lat < 10.0
    assert max_lat > 10.2


def test_empty_mask_raises():
    with pytest.raises(ValueError):
        geojson_polygon_from_mask([], (1, 0, 0, 0, 1, 0))
