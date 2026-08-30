"""
Main FastAPI application entrypoint for Oil Spill Detection & Vessel Attribution.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Oil Spill Detection & Vessel Attribution API",
    description="Backend API for SAR-based oil spill detection, drift backtracking, and vessel attribution.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Oil Spill Detection & Vessel Attribution API"}


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
