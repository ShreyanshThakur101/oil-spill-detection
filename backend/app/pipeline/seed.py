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
        for case_dir in DEMO_CASES_DIR.iterdir():
            if not case_dir.is_dir():
                continue
            case_file = case_dir / "case.json"
            if not case_file.exists():
                continue
            data = json.loads(case_file.read_text(encoding="utf-8"))
            existing = db.query(Case).filter_by(name=data["name"]).first()
            if existing:
                continue
            
            # Parse ISO timestamp if string
            ts = data["image_timestamp"]
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))

            case_obj = Case(
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
