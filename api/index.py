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
if os.environ.get("VERCEL"):
    tmp_db_path = "/tmp/oil_spill.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_db_path}"

from app.main import app

# Export app instance for Vercel's Python ASGI runtime
app = app
