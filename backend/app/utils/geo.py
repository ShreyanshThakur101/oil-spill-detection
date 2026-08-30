import math
from typing import Any, Dict, Tuple


def geojson_polygon_from_mask(mask, transform, crs="EPSG:4326") -> dict:
    """
    Convert a binary segmentation mask and affine geotransform into a GeoJSON Polygon / MultiPolygon dictionary.
    """
    raise NotImplementedError


def polygon_area_km2(polygon_geojson: dict) -> float:
    """
    Compute polygon area in square kilometers using an equal-area projection.
    """
    raise NotImplementedError


def polygon_perimeter_km(polygon_geojson: dict) -> float:
    """
    Compute polygon perimeter length in kilometers.
    """
    raise NotImplementedError


def polygon_elongation(polygon_geojson: dict) -> float:
    """
    Compute ratio of minimum bounding rectangle long side to short side (>= 1.0).
    """
    raise NotImplementedError


def haversine_distance_km(point_a: tuple, point_b: tuple) -> float:
    """
    Compute great-circle distance between two (lon, lat) points in kilometers using the Haversine formula.
    point_a: (lon, lat)
    point_b: (lon, lat)
    """
    lon1, lat1 = point_a
    lon2, lat2 = point_b
    R = 6371.0  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * R * math.asin(math.sqrt(a))


def bbox_from_polygon(polygon_geojson: dict, buffer_km: float) -> tuple:
    """
    Compute a bounding box (min_lon, min_lat, max_lon, max_lat) from a GeoJSON polygon with an optional buffer in km.
    """
    raise NotImplementedError
