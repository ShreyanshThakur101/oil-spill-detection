"""
Seed demo cases into the SQLite database from disk.
"""
import json
from datetime import datetime
from ..config import DEMO_CASES_DIR
from ..database import SessionLocal
from ..models import Case


def seed_cases_from_disk():
    db = SessionLocal()
    try:
        if not DEMO_CASES_DIR.exists():
            return
        
        # Sort by directory name so case_1 precedes case_2
        case_dirs = sorted([d for d in DEMO_CASES_DIR.iterdir() if d.is_dir()], key=lambda x: x.name)
        
        for case_dir in case_dirs:
            case_file = case_dir / "case.json"
            if not case_file.exists():
                continue
            data = json.loads(case_file.read_text(encoding="utf-8"))
            
            # Parse ISO timestamp if string
            ts = data["image_timestamp"]
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))

            # Check if case exists by ID derived from folder or matching name prefix
            dir_num = "".join(filter(str.isdigit, case_dir.name))
            case_id = int(dir_num) if dir_num else None

            existing = None
            if case_id:
                existing = db.query(Case).filter(Case.id == case_id).first()
            if not existing:
                existing = db.query(Case).filter(Case.name == data["name"]).first()

            if existing:
                existing.name = data["name"]
                existing.description = data.get("description")
                existing.sar_image_path = data["sar_image_path"]
                existing.image_timestamp = ts
                existing.bbox = data.get("bbox")
            else:
                case_obj = Case(
                    id=case_id,
                    name=data["name"],
                    description=data.get("description"),
                    sar_image_path=data["sar_image_path"],
                    image_timestamp=ts,
                    bbox=data.get("bbox")
                )
                db.add(case_obj)
        db.commit()
    finally:
        db.close()
