"""
Main FastAPI application entrypoint for Oil Spill Detection and Vessel Attribution.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .pipeline.seed import seed_cases_from_disk
from .routers import cases, health, pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_cases_from_disk()
    yield


app = FastAPI(
    title="Oil Spill Detection and Vessel Attribution API",
    description="Decision-support system combining SAR segmentation, backward drift modeling, and AIS vessel attribution.",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(cases.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")


@app.get("/")
def root():
    return {
        "title": "Oil Spill Detection and Vessel Attribution API",
        "docs": "/docs",
        "health": "/api/health"
    }
