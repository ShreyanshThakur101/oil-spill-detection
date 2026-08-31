"""
Deterministic geometric feature extraction — NOT machine learning, plain shapely math.

Note on thresholds: the elongation / fragment_count cutoffs below are starting
placeholders. Before finalizing, visually inspect 10-15 examples from the training
set, compute their actual elongation values, and tune the thresholds to roughly
separate compact (fresh) from elongated (aging/old) shapes in our specific dataset.
"""
from shapely.geometry import shape

from ..utils.geo import polygon_area_km2, polygon_elongation, polygon_perimeter_km

# Threshold tuning placeholders (see module docstring)
OLD_FRAGMENT_COUNT = 1
OLD_ELONGATION = 3.0
AGING_ELONGATION = 1.8


def compute_shape_features(polygon_geojson: dict) -> dict:
    """
    Compute geometric shape features for a detected slick polygon.

    Input:  GeoJSON polygon (or multipolygon) of the detected slick.
    Output: {
              "area_km2": float,
              "perimeter_km": float,
              "elongation": float,
              "fragment_count": int,
              "age_class": str   # "fresh" | "aging" | "old"
            }

    Rule-based thresholds (placeholder values, tune against real data):
      - fragment_count > 1 and elongation > 3.0  -> "old"
      - elongation > 1.8 (and fragment_count == 1) -> "aging"
      - otherwise -> "fresh"
    """
    geom = shape(polygon_geojson)
    fragment_count = len(geom.geoms) if geom.geom_type == "MultiPolygon" else 1

    area = polygon_area_km2(polygon_geojson)
    perimeter = polygon_perimeter_km(polygon_geojson)
    elongation = polygon_elongation(polygon_geojson)

    if fragment_count > OLD_FRAGMENT_COUNT and elongation > OLD_ELONGATION:
        age_class = "old"
    elif elongation > AGING_ELONGATION:
        age_class = "aging"
    else:
        age_class = "fresh"

    return {
        "area_km2": area,
        "perimeter_km": perimeter,
        "elongation": elongation,
        "fragment_count": fragment_count,
        "age_class": age_class,
    }
