"""
Colab Worker Ingestion Router for SAGAR-DRISHTI.
Receives asynchronous processing results from Google Colab GPU workers,
validates payload schemas, and persists incidents for dashboard review.
"""
import os
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from ..regions import get_zone_by_id
from ..utils.geo import haversine_distance_km

router = APIRouter(prefix="/colab", tags=["Colab Compute Worker"])

COLAB_SECRET_TOKEN = os.environ.get("COLAB_SECRET_TOKEN", "sagar-drishti-colab-prototype-2026")


class ObservationPayload(BaseModel):
    product_id: str
    zone_id: str
    satellite: str = "Sentinel-1A"
    acquisition_time: str
    polarization: str = "VV+VH"
    footprint_geojson: Optional[Dict[str, Any]] = None


class DetectionPayload(BaseModel):
    slick_detected: bool
    confidence_iou: float = Field(..., ge=0.0, le=1.0)
    model_checkpoint: str = "unet_resnet34_oilspill.pth"
    polygon_geojson: Optional[Dict[str, Any]] = None
    shape_features: Optional[Dict[str, Any]] = None


class ProvenancePayload(BaseModel):
    source: str = "LIVE_OBSERVATION"
    worker: str = "Google_Colab_GPU"
    preprocessing: Optional[str] = "Radiometric_Sigma0_LeeFilter"
    processed_timestamp: Optional[str] = None


class ColabJobResult(BaseModel):
    job_id: str
    observation: ObservationPayload
    detection: DetectionPayload
    provenance: ProvenancePayload


@router.post("/results", status_code=status.HTTP_201_CREATED)
def receive_colab_result(
    payload: ColabJobResult,
    authorization: Optional[str] = Header(None)
):
    """
    Receive and ingest processed SAR detection results from an active Google Colab notebook worker.
    """
    # 1. Authenticate worker
    expected_auth = f"Bearer {COLAB_SECRET_TOKEN}"
    if authorization != expected_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Colab authorization Bearer token."
        )

    # 2. Validate coastal surveillance zone
    zone = get_zone_by_id(payload.observation.zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown coastal zone ID: {payload.observation.zone_id}"
        )

    # 3. Process detection payload
    slick_detected = payload.detection.slick_detected
    poly = payload.detection.polygon_geojson

    if slick_detected and not poly:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="slick_detected is True but polygon_geojson was not provided."
        )

    # 4. Generate structured incident response record
    incident_record = {
        "status": "INGESTED",
        "job_id": payload.job_id,
        "zone_name": zone["name"],
        "coast": zone["coast"],
        "primary_mrcc": zone["primary_mrcc"],
        "slick_detected": slick_detected,
        "confidence_iou": payload.detection.confidence_iou,
        "provenance_tier": payload.provenance.source,
        "imported_at": payload.provenance.processed_timestamp or "2026-11-08T11:00:00Z",
        "action_required": "Operator Triage Required" if slick_detected else "Archived: Clean Water"
    }

    return incident_record
