"""
Cases router for querying demo cases.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Case

router = APIRouter(tags=["Cases"])


@router.get("/cases")
def list_cases(db: Session = Depends(get_db)):
    cases = db.query(Case).all()
    return [{"id": c.id, "name": c.name, "description": c.description} for c in cases]


@router.get("/cases/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return {
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "sar_image_path": c.sar_image_path,
        "image_timestamp": c.image_timestamp.isoformat() if c.image_timestamp else None,
        "bbox": c.bbox
    }
