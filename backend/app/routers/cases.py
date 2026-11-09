"""
Cases router for querying demo cases.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..demo_data import is_simulated_case
from ..models import Case

router = APIRouter(tags=["Cases"])


@router.get("/cases")
def list_cases(db: Session = Depends(get_db)):
    # Synthetic demo scenarios are served by /api/demo and must never appear in
    # the live benchmark case pipeline.
    cases = [c for c in db.query(Case).all() if not is_simulated_case(c)]
    return [{"id": c.id, "name": c.name, "description": c.description} for c in cases]


@router.get("/cases/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c or is_simulated_case(c):
        raise HTTPException(status_code=404, detail="Case not found")
    return {
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "sar_image_path": c.sar_image_path,
        "image_timestamp": c.image_timestamp.isoformat() if c.image_timestamp else None,
        "bbox": c.bbox
    }
