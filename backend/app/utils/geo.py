"""
Shared geographic and geometric utilities (Person 1 owned).
"""
import math
from typing import Any, Dict, List, Tuple
import pyproj
from shapely.geometry import MultiPoint, MultiPolygon, Polygon, mapping, shape
from shapely.ops import transform as shapely_transform


def geojson_polygon_from_mask(mask, transform, crs: str = "EPSG:4326") -> dict:
    """
    Convert a binary segmentation mask and affine geotransform into a GeoJSON Polygon / MultiPolygon dictionary.
    mask: 2D numpy array (1 = slick, 0 = background)
    transform: affine transform (e.g. from rasterio or tuple (a, b, c, d, e, f))
    """
    if mask is None:
        raise ValueError("Mask cannot be None")

    import numpy as np

    mask_arr = np.asarray(mask)
    if mask_arr.size == 0 or not np.any(mask_arr > 0):
        raise ValueError("Mask is empty or contains no detected slick pixels")

    # If rasterio is available, use rasterio.features.shapes
    try:
        import rasterio.features
        shapes = list(rasterio.features.shapes(mask_arr.astype(np.uint8), transform=transform))
        polygons = [shape(geom) for geom, val in shapes if val == 1]
        if not polygons:
            raise ValueError("No polygon shapes extracted from mask")
        if len(polygons) == 1:
            return mapping(polygons[0])
        return mapping(MultiPolygon(polygons))
    except ImportError:
        # Fallback using pixel coordinates and shapely
        coords_y, coords_x = np.where(mask_arr > 0)
        points = []
        for x, y in zip(coords_x, coords_y):
            # Apply affine transform: x' = a*x + b*y + c, y' = d*x + e*y + f
            if hasattr(transform, "a"):
                gx = transform.a * x + transform.b * y + transform.c
                gy = transform.d * x + transform.e * y + transform.f
            elif isinstance(transform, (list, tuple)) and len(transform) >= 6:
                gx = transform[0] * x + transform[1] * y + transform[2]
                gy = transform[3] * x + transform[4] * y + transform[5]
            else:
                gx, gy = float(x), float(y)
            points.append((gx, gy))
        
        mp = MultiPoint(points)
        hull = mp.convex_hull
        if hull.geom_type not in ["Polygon", "MultiPolygon"]:
            hull = hull.buffer(0.001)
        return mapping(hull)


def _get_projector_to_equal_area(geom):
    """
    Construct a pyproj coordinate transformation from EPSG:4326 to a local
    Lambert Azimuthal Equal Area (LAEA) projection centered at geometry centroid.
    """
    centroid = geom.centroid
    proj_laea = f"+proj=laea +lat_0={centroid.y} +lon_0={centroid.x} +datum=WGS84 +units=m +no_defs"
    transformer = pyproj.Transformer.from_crs("EPSG:4326", proj_laea, always_xy=True)
    return transformer.transform


def polygon_area_km2(polygon_geojson: dict) -> float:
    """
    Compute polygon area in square kilometers using an equal-area projection.
    """
    if not polygon_geojson or not isinstance(polygon_geojson, dict):
        raise ValueError("Invalid polygon GeoJSON dict")
    geom = shape(polygon_geojson)
    if geom.is_empty:
        return 0.0
    project_fn = _get_projector_to_equal_area(geom)
    projected = shapely_transform(project_fn, geom)
    area_m2 = projected.area
    return float(area_m2 / 1e6)


def polygon_perimeter_km(polygon_geojson: dict) -> float:
    """
    Compute polygon perimeter length in kilometers using an equal-area projection.
    """
    if not polygon_geojson or not isinstance(polygon_geojson, dict):
        raise ValueError("Invalid polygon GeoJSON dict")
    geom = shape(polygon_geojson)
    if geom.is_empty:
        return 0.0
    project_fn = _get_projector_to_equal_area(geom)
    projected = shapely_transform(project_fn, geom)
    length_m = projected.length
    return float(length_m / 1000.0)


def polygon_elongation(polygon_geojson: dict) -> float:
    """
    Compute ratio of minimum bounding rectangle long side to short side (>= 1.0).
    Fresh spills are compact (~1.0), aged/spread spills are elongated.
    """
    if not polygon_geojson or not isinstance(polygon_geojson, dict):
        raise ValueError("Invalid polygon GeoJSON dict")
    geom = shape(polygon_geojson)
    if geom.is_empty:
        return 1.0
    rect = geom.minimum_rotated_rectangle
    if rect.geom_type != "Polygon":
        return 1.0
    coords = list(rect.exterior.coords)
    if len(coords) < 4:
        return 1.0
    side1 = math.hypot(coords[1][0] - coords[0][0], coords[1][1] - coords[0][1])
    side2 = math.hypot(coords[2][0] - coords[1][0], coords[2][1] - coords[1][1])
    short_side = min(side1, side2)
    long_side = max(side1, side2)
    if short_side <= 1e-12:
        return 1.0
    return float(long_side / short_side)


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
    return float(2.0 * R * math.asin(math.sqrt(max(0.0, min(1.0, a)))))


def bbox_from_polygon(polygon_geojson: dict, buffer_km: float = 0.0) -> tuple:
    """
    Compute a bounding box (min_lon, min_lat, max_lon, max_lat) from a GeoJSON polygon with an optional buffer in km.
    """
    if not polygon_geojson or not isinstance(polygon_geojson, dict):
        raise ValueError("Invalid polygon GeoJSON dict")
    geom = shape(polygon_geojson)
    if geom.is_empty:
        raise ValueError("Empty geometry")
    min_lon, min_lat, max_lon, max_lat = geom.bounds
    if buffer_km > 0:
        lat_buffer = buffer_km / 111.0
        mean_lat = (min_lat + max_lat) / 2.0
        cos_lat = max(math.cos(math.radians(mean_lat)), 0.01)
        lon_buffer = buffer_km / (111.0 * cos_lat)
        min_lon -= lon_buffer
        max_lon += lon_buffer
        min_lat -= lat_buffer
        max_lat += lat_buffer
    return (float(min_lon), float(min_lat), float(max_lon), float(max_lat))
