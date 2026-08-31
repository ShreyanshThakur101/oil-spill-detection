"""
Pipeline router executing detection, backward drift, and vessel attribution.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Case

router = APIRouter(tags=["Pipeline"])


def _mock_pipeline_result(case_id: int) -> dict:
    """
    TEMPORARY Mock result matching the exact shape orchestrator.run_full_pipeline() returns
    (ARCHITECTURE.md section 5.5).
    """
    return {
        "detection": {
            "polygon_geojson": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [76.02, 9.51],
                        [76.12, 9.53],
                        [76.15, 9.62],
                        [76.04, 9.60],
                        [76.02, 9.51]
                    ]
                ]
            },
            "confidence": 0.89,
            "shape_features": {
                "area_km2": 12.3,
                "perimeter_km": 8.1,
                "elongation": 2.4,
                "fragment_count": 1,
                "age_class": "fresh"
            }
        },
        "drift": {
            "origin_polygon_geojson": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [75.88, 9.38],
                        [76.04, 9.40],
                        [76.06, 9.54],
                        [75.90, 9.52],
                        [75.88, 9.38]
                    ]
                ]
            },
            "estimated_origin_time": "2025-05-25T22:00:00Z",
            "uncertainty_radius_km": 6.2
        },
        "vessels": [
            {
                "mmsi": "412345678",
                "vessel_name": "MT OCEAN PIONEER",
                "vessel_type": "Tanker",
                "track_geojson": {
                    "type": "LineString",
                    "coordinates": [
                        [75.75, 9.25],
                        [75.88, 9.38],
                        [75.96, 9.46],
                        [76.08, 9.58]
                    ]
                },
                "scores": {
                    "proximity": 0.92,
                    "parity": 0.78,
                    "temporality": 0.85,
                    "ais_gap": 0.90,
                    "speed_anomaly": 0.20,
                    "vessel_type_prior": 0.85
                },
                "final_score": 0.82,
                "explanation": "High proximity (2.1 km) to backward drift origin; 2.4 hr AIS transmission gap overlapping release window; Tanker class has elevated prior likelihood."
            },
            {
                "mmsi": "563987123",
                "vessel_name": "MV PACIFIC BREEZE",
                "vessel_type": "Cargo",
                "track_geojson": {
                    "type": "LineString",
                    "coordinates": [
                        [75.60, 9.15],
                        [75.78, 9.30],
                        [75.92, 9.42],
                        [76.10, 9.52]
                    ]
                },
                "scores": {
                    "proximity": 0.65,
                    "parity": 0.50,
                    "temporality": 0.60,
                    "ais_gap": 0.10,
                    "speed_anomaly": 0.15,
                    "vessel_type_prior": 0.40
                },
                "final_score": 0.46,
                "explanation": "Transited through secondary boundary of search bbox; constant speed; no AIS broadcast gap."
            },
            {
                "mmsi": "235112449",
                "vessel_name": "FV SEA FALCON",
                "vessel_type": "Fishing",
                "track_geojson": {
                    "type": "LineString",
                    "coordinates": [
                        [76.05, 9.60],
                        [76.12, 9.65],
                        [76.08, 9.70]
                    ]
                },
                "scores": {
                    "proximity": 0.30,
                    "parity": 0.20,
                    "temporality": 0.35,
                    "ais_gap": 0.05,
                    "speed_anomaly": 0.45,
                    "vessel_type_prior": 0.15
                },
                "final_score": 0.24,
                "explanation": "Fishing vessel located downstream of origin; low correlation with estimated discharge time."
            }
        ]
    }


@router.post("/cases/{case_id}/run")
def run_pipeline(case_id: int, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return _mock_pipeline_result(case_id)
