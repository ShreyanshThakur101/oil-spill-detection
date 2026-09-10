"""
Pipeline & Nugen Decision Engine router.
Endpoints for pipeline execution, Nugen inference, scientific benchmarks, and legal dossiers.
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Case
from ..pipeline.orchestrator import run_full_pipeline, _get_case_metadata
from ..nugen.client import invoke_nugen_inference
from ..nugen.benchmarks import get_benchmark_report
from ..nugen.dossier_generator import generate_icg_enforcement_dossier

router = APIRouter(tags=["Pipeline & Nugen Engine"])


@router.post("/cases/{case_id}/run")
def run_pipeline(case_id: int, db: Session = Depends(get_db)):
    """
    Trigger end-to-end SAGAR-DRISHTI pipeline execution for a selected demo case.
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    try:
        result = run_full_pipeline(case_id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@router.post("/cases/{case_id}/dossier")
def get_case_dossier(
    case_id: int,
    mmsi: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generate or export the court-ready ICG maritime enforcement dossier for a specific suspect vessel.
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    try:
        pipeline_res = run_full_pipeline(case_id, db)
        vessels = pipeline_res.get("vessels", [])
        
        target_vessel = None
        if mmsi:
            for v in vessels:
                if str(v.get("mmsi")) == str(mmsi):
                    target_vessel = v
                    break
        if not target_vessel and vessels:
            target_vessel = vessels[0]

        if not target_vessel:
            raise HTTPException(status_code=400, detail="No vessel telemetry available to generate dossier")

        meta = _get_case_metadata(case)
        dossier = generate_icg_enforcement_dossier(
            case_data=meta,
            detection_data=pipeline_res.get("detection", {}),
            drift_data=pipeline_res.get("drift", {}),
            suspect_vessel=target_vessel,
            nugen_inference=pipeline_res.get("nugen", {}).get("inference", {})
        )
        return dossier
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dossier generation failed: {str(e)}")


@router.post("/nugen/inference")
def nugen_inference_endpoint(payload: Dict[str, Any] = Body(...)):
    """
    Direct Nugen Domain-Aligned SLM inference endpoint matching Slide 6 contract.
    Accepts: model, domain, slick_coords, spill_timestamp, suspect_vessel, jurisdiction.
    """
    try:
        slick_coords = payload.get("slick_coords", [9.9312, 76.2673])
        spill_timestamp = payload.get("spill_timestamp", "2025-05-24T14:30:00Z")
        suspect_vessel = payload.get("suspect_vessel", {})
        jurisdiction = payload.get("jurisdiction", "Merchant_Shipping_Act_1958")
        model = payload.get("model", "nugen-maritime-aligned-phi3")
        domain = payload.get("domain", "indian_eez_enforcement")

        res = invoke_nugen_inference(
            slick_coords=slick_coords,
            spill_timestamp=spill_timestamp,
            suspect_vessel=suspect_vessel,
            jurisdiction=jurisdiction,
            model=model,
            domain=domain
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nugen inference call failed: {str(e)}")


@router.get("/nugen/benchmark")
def nugen_benchmark():
    """
    Retrieve Slide 7 Scientific Validation benchmarks: Base Model vs Nugen Aligned Maritime SLM.
    """
    return get_benchmark_report()
