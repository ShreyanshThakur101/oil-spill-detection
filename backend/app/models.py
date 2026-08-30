"""
SQLAlchemy ORM models for Oil Spill Detection & Attribution.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from .database import Base


class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    sar_image_path = Column(String, nullable=False)
    image_timestamp = Column(DateTime, nullable=False)
    bbox = Column(JSON)  # [min_lon, min_lat, max_lon, max_lat]


class SlickDetection(Base):
    __tablename__ = "slick_detections"
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    polygon_geojson = Column(JSON)
    confidence = Column(Float)
    area_km2 = Column(Float)
    perimeter_km = Column(Float)
    elongation = Column(Float)
    fragment_count = Column(Integer)
    age_class = Column(String)


class DriftResult(Base):
    __tablename__ = "drift_results"
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    detection_id = Column(Integer, ForeignKey("slick_detections.id"))
    origin_polygon_geojson = Column(JSON)
    estimated_origin_time = Column(DateTime)
    uncertainty_radius_km = Column(Float)


class VesselScore(Base):
    __tablename__ = "vessel_scores"
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    mmsi = Column(String)
    vessel_name = Column(String)
    vessel_type = Column(String)
    track_geojson = Column(JSON)
    scores_json = Column(JSON)  # Dict of sub-scores
    final_score = Column(Float)
    explanation = Column(String)
