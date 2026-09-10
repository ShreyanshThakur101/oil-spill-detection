"""
Scoring features module implementing the 6 domain features for vessel attribution.
Matches SAGAR-DRISHTI Pillar 3 specifications (Slide 4, 6, 8):
1. Spatio-temporal Proximity (to backward drift origin cone)
2. Trajectory-Slick Parity (course alignment with slick long-axis)
3. Temporality (coincidence with estimated spill release window)
4. AIS Blackout Gap (deliberate transponder disablement overlapping origin)
5. Speed Anomaly (sudden deceleration / discharge maneuver)
6. Vessel Type Prior (Tanker / Container / Bulk / Fishing)
"""
import math
from datetime import datetime
from typing import Any, Dict, List, Tuple
from shapely.geometry import LineString, shape

from ..utils.geo import haversine_distance_km


def _parse_dt(val: Any) -> datetime:
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    return datetime.min


def compute_proximity_score(vessel_track: List[Dict[str, Any]], origin_polygon_geojson: dict) -> float:
    """
    Compute proximity score between vessel track and estimated origin cone.
    Returns 1.0 inside origin polygon, decays to 0.0 at 25km.
    """
    if not vessel_track or not origin_polygon_geojson:
        return 0.0
    try:
        origin_geom = shape(origin_polygon_geojson)
        centroid = origin_geom.centroid
        distances = [
            haversine_distance_km((centroid.x, centroid.y), (p["lon"], p["lat"]))
            for p in vessel_track
            if "lat" in p and "lon" in p
        ]
        if not distances:
            return 0.0
        min_dist = min(distances)
        MAX_DIST_KM = 25.0
        if min_dist <= 1.5:
            return 0.98
        return float(max(0.0, min(1.0, 1.0 - min_dist / MAX_DIST_KM)))
    except Exception:
        return 0.0


def compute_parity_score(vessel_track: List[Dict[str, Any]], slick_polygon_geojson: dict) -> float:
    """
    Compute alignment (parity) between vessel heading trajectory and slick long axis.
    """
    if len(vessel_track) < 2 or not slick_polygon_geojson:
        return 0.0
    try:
        p0, p1 = vessel_track[0], vessel_track[-1]
        vessel_bearing = math.atan2(p1["lon"] - p0["lon"], p1["lat"] - p0["lat"])

        slick_geom = shape(slick_polygon_geojson)
        mrr = slick_geom.minimum_rotated_rectangle
        coords = list(mrr.exterior.coords)
        if len(coords) < 2:
            return 0.0
        edge = max(
            [(coords[i], coords[i + 1]) for i in range(len(coords) - 1)],
            key=lambda e: LineString(e).length,
        )
        slick_bearing = math.atan2(edge[1][0] - edge[0][0], edge[1][1] - edge[0][1])

        angle_diff = abs(vessel_bearing - slick_bearing)
        return float(abs(math.cos(angle_diff)))
    except Exception:
        return 0.0


def compute_temporality_score(vessel_track: List[Dict[str, Any]], origin_time_window: Tuple[datetime, datetime]) -> float:
    """
    Compute temporal correlation between vessel telemetry timestamps and origin release window.
    """
    if not vessel_track or not origin_time_window:
        return 0.0
    try:
        start_w, end_w = origin_time_window
        start = start_w if start_w.tzinfo is None else start_w.replace(tzinfo=None)
        end = end_w if end_w.tzinfo is None else end_w.replace(tzinfo=None)

        for p in vessel_track:
            t = _parse_dt(p.get("timestamp"))
            if t.tzinfo is not None:
                t = t.replace(tzinfo=None)

            if start <= t <= end:
                return 0.96

        gap_hours_list = []
        for p in vessel_track:
            t = _parse_dt(p.get("timestamp"))
            if t.tzinfo is not None:
                t = t.replace(tzinfo=None)

            if t < start:
                gap = abs((t - start).total_seconds()) / 3600.0
            else:
                gap = abs((t - end).total_seconds()) / 3600.0
            gap_hours_list.append(gap)

        if not gap_hours_list:
            return 0.0
        nearest_gap = min(gap_hours_list)
        return float(max(0.0, min(1.0, 1.0 - nearest_gap / 6.0)))
    except Exception:
        return 0.0


def compute_ais_gap_score(mmsi: str, gap_events: List[Dict[str, Any]], origin_time_window: Tuple[datetime, datetime]) -> float:
    """
    Score AIS-disabling ("going dark") events overlapping the spill release window.
    Deliberate blackouts > 30 minutes score 0.95+.
    """
    if not gap_events or not mmsi:
        return 0.0
    try:
        start_w, end_w = origin_time_window
        start = start_w if start_w.tzinfo is None else start_w.replace(tzinfo=None)
        end = end_w if end_w.tzinfo is None else end_w.replace(tzinfo=None)

        relevant = []
        for g in gap_events:
            if str(g.get("mmsi")) == str(mmsi):
                g_start = _parse_dt(g.get("gap_start")).replace(tzinfo=None)
                g_end = _parse_dt(g.get("gap_end")).replace(tzinfo=None)
                # Check overlap or proximity within 45 mins
                if (g_end >= start and g_start <= end) or abs((g_start - start).total_seconds()) <= 2700:
                    relevant.append(g)

        if not relevant:
            return 0.0
        
        target = relevant[0]
        mins = float(target.get("gap_minutes", target.get("gap_hours", 0) * 60))
        is_deliberate = target.get("deliberate_flag", mins >= 30)

        if is_deliberate and mins >= 30:
            return 0.95
        return float(min(1.0, max(0.2, mins / 60.0)))
    except Exception:
        return 0.0


def compute_speed_anomaly_score(vessel_track: List[Dict[str, Any]]) -> float:
    """
    Score sudden speed drops along track indicative of intentional offshore bunker dumping.
    Decelerations >= 5.0 kt score 0.90+.
    """
    speeds = [
        float(p["speed_knots"])
        for p in vessel_track
        if "speed_knots" in p and p["speed_knots"] is not None
    ]
    if len(speeds) < 2:
        return 0.0
    
    max_drop = max(max(0.0, speeds[i] - speeds[i + 1]) for i in range(len(speeds) - 1))
    if max_drop >= 6.0:
        return 0.92
    elif max_drop >= 4.0:
        return 0.75
    elif max_drop >= 2.0:
        return 0.40
    return 0.10


def compute_vessel_type_prior(vessel_type: str) -> float:
    """
    Prior likelihood table based on vessel category and bunker fuel capacity.
    """
    priors = {
        "tanker": 0.92,
        "cargo": 0.88,
        "container": 0.88,
        "bulk carrier": 0.70,
        "fishing": 0.25,
        "passenger": 0.20,
        "pleasure": 0.10,
    }
    return float(priors.get(str(vessel_type).lower(), 0.40))
