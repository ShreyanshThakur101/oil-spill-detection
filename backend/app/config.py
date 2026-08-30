import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent   # backend/
DATA_DIR = BASE_DIR / "data"
DEMO_CASES_DIR = DATA_DIR / "demo_cases"
MODELS_DIR = DATA_DIR / "models"
DATABASE_URL = f"sqlite:///{DATA_DIR / 'oil_spill.db'}"

# API Keys & Secrets (loaded from environment, do not hard-code)
GFW_API_KEY = os.environ.get("GFW_API_KEY", "")   # Global Fishing Watch API Key (used by Person 3)
