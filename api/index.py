"""
Vercel Serverless Function entrypoint for SAGAR-DRISHTI FastAPI Backend.
Handles /api/* routes on Vercel.
"""
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# On Vercel serverless, filesystem is read-only except for /tmp
if os.environ.get("VERCEL") or not os.path.exists(root_dir / "backend" / "data"):
    tmp_db_path = "/tmp/oil_spill.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_db_path}"

from app.main import app as fastapi_app
from app.database import init_db
from app.pipeline.seed import seed_cases_from_disk

# Pre-initialize and seed SQLite on cold start
try:
    init_db()
    seed_cases_from_disk()
except Exception as e:
    print(f"Notice: Serverless DB init: {e}")


# ASGI middleware wrapper to normalize Vercel serverless paths
async def app(scope, receive, send):
    if scope.get("type") == "http":
        headers = dict(scope.get("headers", []))
        matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")
        current_path = scope.get("path", "")
        # If Vercel rewrote the path to /api/index.py or /api/index, restore original matched path
        if matched_path and current_path in ("/api/index.py", "/api/index", "/api/index.py/"):
            scope["path"] = matched_path
    await fastapi_app(scope, receive, send)

