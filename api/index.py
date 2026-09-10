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
        qs = scope.get("query_string", b"").decode("utf-8")
        current_path = scope.get("path", "")

        # 1. Handle query parameter rewrite from Vercel: /api/index.py?__path=cases
        if "__path=" in qs:
            from urllib.parse import parse_qs, urlencode
            params = parse_qs(qs, keep_blank_values=True)
            if "__path" in params:
                subpath = params.pop("__path")[0]
                # Reconstruct query string without __path
                scope["query_string"] = urlencode(params, doseq=True).encode("utf-8")
                clean_subpath = subpath.lstrip("/")
                scope["path"] = f"/api/{clean_subpath}"
        # 2. Handle x-matched-path or x-forwarded-uri headers
        elif current_path in ("/api/index.py", "/api/index", "/api/index.py/"):
            headers = dict(scope.get("headers", []))
            matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")
            if not matched_path:
                matched_path = headers.get(b"x-forwarded-uri", b"").decode("utf-8")
            if matched_path and matched_path not in ("/api/index.py", "/api/index"):
                scope["path"] = matched_path
            else:
                scope["path"] = "/api"

    await fastapi_app(scope, receive, send)


