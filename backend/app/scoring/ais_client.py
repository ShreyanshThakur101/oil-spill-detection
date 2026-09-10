"""
AIS Client module for loading cached GFW AIS responses or making live API queries.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import DEMO_CASES_DIR, GFW_API_KEY

GFW_BASE_URL = "https://gateway.api.globalfishingwatch.org/v3"


def _headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {GFW_API_KEY}"}


def cache_response_to_disk(data: Any, case_id: str, kind: str) -> None:
    """
    Save fetched AIS data to local cache under demo_cases/{case_id}/ais_cache_{kind}.json.
    kind: 'positions' or 'gaps'
    """
    path = DEMO_CASES_DIR / case_id / f"ais_cache_{kind}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, default=str, indent=2), encoding="utf-8")


def load_cached_response(case_id: str, kind: str) -> Any:
    """
    Load cached AIS data from demo_cases/{case_id}/ais_cache_{kind}.json.
    """
    path = DEMO_CASES_DIR / case_id / f"ais_cache_{kind}.json"
    if not path.exists():
        # Fallback to empty list if cache doesn't exist
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_vessel_positions(bbox: tuple, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """
    Query Global Fishing Watch API for vessel positions.
    """
    if not GFW_API_KEY:
        return []
    try:
        import requests
        url = f"{GFW_BASE_URL}/vessels/events"
        params = {
            "start-date": start_time.isoformat(),
            "end-date": end_time.isoformat(),
            "confidences": "4",
        }
        res = requests.get(url, headers=_headers(), params=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception:
        return []


def fetch_ais_gap_events(bbox: tuple, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """
    Query Global Fishing Watch API for AIS disabling (gap) events.
    """
    if not GFW_API_KEY:
        return []
    try:
        import requests
        url = f"{GFW_BASE_URL}/events"
        params = {
            "event-types": "ais-disabling",
            "start-date": start_time.isoformat(),
            "end-date": end_time.isoformat(),
        }
        res = requests.get(url, headers=_headers(), params=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception:
        return []
