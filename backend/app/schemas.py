"""
Pydantic schemas for API request and response data models.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class CaseBase(BaseModel):
    name: str
    description: Optional[str] = None
    sar_image_path: str
    image_timestamp: datetime
    bbox: Optional[List[float]] = None


class CaseOut(CaseBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SlickDetectionOut(BaseModel):
    id: int
    case_id: int
    polygon_geojson: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    area_km2: Optional[float] = None
    perimeter_km: Optional[float] = None
    elongation: Optional[float] = None
    fragment_count: Optional[int] = None
    age_class: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DriftResultOut(BaseModel):
    id: int
    case_id: int
    detection_id: Optional[int] = None
    origin_polygon_geojson: Optional[Dict[str, Any]] = None
    estimated_origin_time: Optional[datetime] = None
    uncertainty_radius_km: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class VesselScoreOut(BaseModel):
    id: int
    case_id: int
    mmsi: Optional[str] = None
    vessel_name: Optional[str] = None
    vessel_type: Optional[str] = None
    track_geojson: Optional[Dict[str, Any]] = None
    scores_json: Optional[Dict[str, Any]] = None
    final_score: Optional[float] = None
    explanation: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
