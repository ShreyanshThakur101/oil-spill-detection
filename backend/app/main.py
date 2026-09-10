"""
Main FastAPI application entrypoint for Oil Spill Detection and Vessel Attribution.
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .database import init_db
from .pipeline.seed import seed_cases_from_disk
from .routers import cases, health, pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_cases_from_disk()
    yield


app = FastAPI(
    title="SAGAR-DRISHTI API",
    description="Physics-Informed AI for Oil Spill Detection & Vessel Attribution (PCCOE IGC 2026).",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standard /api prefix routes
app.include_router(health.router, prefix="/api")
app.include_router(cases.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")

# Direct routes without /api prefix (supports Vercel path-stripping rewrites)
app.include_router(health.router)
app.include_router(cases.router)
app.include_router(pipeline.router)


@app.get("/api")
@app.get("/api/")
@app.get("/api/index")
@app.get("/api/index.py")
def api_root():
    return {
        "status": "online",
        "system": "SAGAR-DRISHTI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "cases": "/api/cases"
    }


# Frontend static files serving & SPA fallback
def find_frontend_dist() -> Path | None:
    """Locate frontend dist directory across local, packaged, and Vercel serverless environments."""
    candidates = [
        Path(__file__).resolve().parent / "dist",                             # backend/app/dist (bundled with package)
        Path(__file__).resolve().parent.parent.parent / "frontend" / "dist",  # root/frontend/dist (local dev / monorepo)
        Path.cwd() / "backend" / "app" / "dist",
        Path.cwd() / "frontend" / "dist",
        Path("/var/task/backend/app/dist"),
        Path("/var/task/frontend/dist"),
    ]
    for c in candidates:
        if c.exists() and (c / "index.html").exists():
            return c
    return None


frontend_dist = find_frontend_dist()

if frontend_dist:
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/")
    @app.get("/index.html")
    def serve_index():
        return FileResponse(frontend_dist / "index.html")

    @app.exception_handler(404)
    async def spa_404_handler(request: Request, exc):
        # API requests or JSON clients receive a standard JSON 404
        if request.url.path.startswith("/api") or "application/json" in request.headers.get("accept", ""):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        # Browser page navigations fallback to SPA index.html
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/")
    @app.get("/index.html")
    def root():
        return {
            "title": "SAGAR-DRISHTI API",
            "docs": "/docs",
            "health": "/api/health",
            "cases": "/api/cases"
        }


