"""
SAGAR-DRISHTI Indian Coastal Surveillance Zones (Provisional Search Envelopes).

IMPORTANT GEOGRAPHIC & LEGAL DISCLAIMER:
-----------------------------------------
1. The bounding boxes [min_lon, min_lat, max_lon, max_lat] in this module are
   PROVISIONAL RECTANGULAR QUERY ENVELOPES designed strictly for filtering
   satellite scene catalogs (e.g. Copernicus Data Space Ecosystem OData API).
2. They ARE NOT authoritative administrative boundaries of Indian States or Union Territories.
3. They ARE NOT sovereign maritime jurisdiction boundaries (Territorial Waters, Contiguous
   Zone, or Exclusive Economic Zone under the Maritime Zones Act 1976 or UNCLOS).
4. They DO NOT establish legal jurisdiction for maritime enforcement or statutory action.
5. In Milestone 2+, these provisional rectangular envelopes will be supplemented by
   verified vector polygon boundaries sourced from official Survey of India (SOI) and
   hydrographic baselines.

Encompasses all 9 coastal states and 4 coastal Union Territories (Daman & Diu as the coastal UT).
"""
from typing import Any, Dict, List, Tuple


COASTAL_ZONES: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # WESTERN COAST (5 States + 1 UT)
    # -------------------------------------------------------------------------
    "IN-GJ": {
        "id": "IN-GJ",
        "name": "Gujarat",
        "type": "STATE",
        "coast": "WEST",
        "coastline_km": 1214.7,  # NCCR/MoES assessment figure
        "ports": ["Kandla (Deendayal)", "Mundra", "Sikka", "Vadinar SPM", "Pipavav", "Dahej"],
        "primary_mrcc": "MRCC Gandhinagar / MRCC Mumbai",
        "bbox": [68.10, 20.00, 73.00, 24.70],  # Provisional search envelope
        "default_offshore_buffer_nm": 50,
        "envelope_notes": "Covers Gulf of Kutch to Gulf of Khambhat. Note: Eastern edge overlaps with IN-DD (Daman/Diu) and northern Maharashtra."
    },
    "IN-DD": {
        "id": "IN-DD",
        "name": "Dadra and Nagar Haveli and Daman and Diu (Coastal: Daman and Diu)",
        "type": "UNION_TERRITORY",
        "coast": "WEST",
        "coastline_km": 42.0,  # NCCR figure for Daman and Diu littoral strips
        "ports": ["Daman Anchorage", "Diu Anchorage"],
        "primary_mrcc": "MRCC Mumbai",
        "bbox": [70.80, 20.30, 72.90, 20.80],  # Provisional search envelope
        "default_offshore_buffer_nm": 24,
        "envelope_notes": "Dadra and Nagar Haveli is an inland district. Littoral surveillance applies strictly to coastal Daman & Diu enclaves. Narrow latitude envelope spans Gulf of Khambhat mouth."
    },
    "IN-MH": {
        "id": "IN-MH",
        "name": "Maharashtra",
        "type": "STATE",
        "coast": "WEST",
        "coastline_km": 652.6,
        "ports": ["Jawaharlal Nehru Port (JNPT)", "Mumbai Port", "Dighi", "Jaigad", "Redi"],
        "primary_mrcc": "MRCC Mumbai",
        "bbox": [72.10, 15.60, 73.50, 20.20],  # Provisional search envelope
        "default_offshore_buffer_nm": 50,
        "envelope_notes": "Western edge extends to 72.10°E. Note: Mumbai High offshore oil field (~71.2°E to 71.9°E) lies WEST of this base box and requires the custom 80 nm offshore monitoring polygon."
    },
    "IN-GA": {
        "id": "IN-GA",
        "name": "Goa",
        "type": "STATE",
        "coast": "WEST",
        "coastline_km": 101.0,
        "ports": ["Mormugao", "Panaji Anchorage"],
        "primary_mrcc": "MRCC Mumbai",
        "bbox": [73.60, 14.80, 74.40, 15.85],  # Provisional search envelope
        "default_offshore_buffer_nm": 24,
        "envelope_notes": "Compact littoral corridor. Overlaps with southern Maharashtra (Redi) and northern Karnataka (Karwar)."
    },
    "IN-KA": {
        "id": "IN-KA",
        "name": "Karnataka",
        "type": "STATE",
        "coast": "WEST",
        "coastline_km": 280.0,
        "ports": ["New Mangalore Port", "Karwar", "Tadadi", "Belekeri"],
        "primary_mrcc": "MRCC Mumbai / MRCC Kochi",
        "bbox": [74.00, 12.70, 75.10, 15.00],  # Provisional search envelope
        "default_offshore_buffer_nm": 30,
        "envelope_notes": "Covers Karwar naval fairway to Mangalore. Bounded between Goa and Kerala envelopes."
    },
    "IN-KL": {
        "id": "IN-KL",
        "name": "Kerala",
        "type": "STATE",
        "coast": "WEST",
        "coastline_km": 569.7,
        "ports": ["Port of Cochin", "Vizhinjam International Seaport", "Beypore", "Kollam"],
        "primary_mrcc": "MRCC Kochi",
        "bbox": [74.80, 8.20, 76.80, 12.85],  # Provisional search envelope
        "default_offshore_buffer_nm": 50,
        "envelope_notes": "Covers entire Malabar coast down to Vizhinjam. Offshore extension intersects high-density Lakshadweep Sea container routes."
    },

    # -------------------------------------------------------------------------
    # EASTERN COAST (4 States + 1 UT)
    # -------------------------------------------------------------------------
    "IN-TN": {
        "id": "IN-TN",
        "name": "Tamil Nadu",
        "type": "STATE",
        "coast": "EAST",
        "coastline_km": 906.9,
        "ports": ["Chennai Port", "Kamarajar (Ennore)", "V.O. Chidambaranar (Tuticorin)", "Kattupalli"],
        "primary_mrcc": "MRCC Chennai",
        "bbox": [77.20, 8.00, 80.50, 13.50],  # Provisional search envelope
        "default_offshore_buffer_nm": 40,
        "envelope_notes": "Spans Cape Comorin to Pulicat Lake. Encompasses Palk Strait and Gulf of Mannar."
    },
    "IN-PY": {
        "id": "IN-PY",
        "name": "Puducherry",
        "type": "UNION_TERRITORY",
        "coast": "EAST",
        "coastline_km": 45.0,
        "ports": ["Puducherry Port", "Karaikal Port"],
        "primary_mrcc": "MRCC Chennai",
        "bbox": [79.70, 10.80, 80.00, 12.10],  # Provisional search envelope
        "default_offshore_buffer_nm": 24,
        "envelope_notes": "Encompasses Puducherry main enclave and Karaikal. Note: Excludes non-contiguous Mahe (Arabian Sea) and Yanam (Godavari estuary), which fall under IN-KL and IN-AP respectively."
    },
    "IN-AP": {
        "id": "IN-AP",
        "name": "Andhra Pradesh",
        "type": "STATE",
        "coast": "EAST",
        "coastline_km": 973.7,
        "ports": ["Visakhapatnam Port", "Gangavaram", "Krishnapatnam", "Kakinada Deepwater"],
        "primary_mrcc": "MRCC Chennai",
        "bbox": [79.90, 13.40, 84.80, 19.20],  # Provisional search envelope
        "default_offshore_buffer_nm": 50,
        "envelope_notes": "Spans Coromandel coast to Kalingapatnam. Krishna-Godavari deepwater offshore gas platforms require the custom 60 nm offshore monitoring polygon."
    },
    "IN-OD": {
        "id": "IN-OD",
        "name": "Odisha",
        "type": "STATE",
        "coast": "EAST",
        "coastline_km": 476.4,
        "ports": ["Paradip Port", "Dhamra Port", "Gopalpur Port"],
        "primary_mrcc": "MRCC Paradip / MRCC Chennai",
        "bbox": [84.70, 19.00, 87.50, 21.80],  # Provisional search envelope
        "default_offshore_buffer_nm": 50,
        "envelope_notes": "Covers Paradip crude tanker anchorages and Gahirmatha marine sanctuary. Overlaps slightly with northern Andhra and southern West Bengal."
    },
    "IN-WB": {
        "id": "IN-WB",
        "name": "West Bengal",
        "type": "STATE",
        "coast": "EAST",
        "coastline_km": 157.5,
        "ports": ["Haldia Dock Complex", "Kolkata (Syama Prasad Mookerjee Port)"],
        "primary_mrcc": "MRCC Haldia / MRCC Kolkata",
        "bbox": [87.40, 21.30, 89.20, 22.50],  # Provisional search envelope
        "default_offshore_buffer_nm": 30,
        "envelope_notes": "Covers Hooghly estuary and Sandheads transshipment zone. North-eastern edge terminates at the international maritime boundary with Bangladesh."
    },

    # -------------------------------------------------------------------------
    # ISLAND TERRITORIES (2 UTs)
    # -------------------------------------------------------------------------
    "IN-AN": {
        "id": "IN-AN",
        "name": "Andaman and Nicobar Islands",
        "type": "UNION_TERRITORY",
        "coast": "ISLANDS",
        "coastline_km": 1962.0,
        "ports": ["Port Blair", "Haddo Anchorage", "Great Nicobar (Galathea Bay transshipment hub)"],
        "primary_mrcc": "MRCC Port Blair",
        "bbox": [92.00, 6.50, 94.50, 13.80],  # Provisional search envelope
        "default_offshore_buffer_nm": 50,
        "envelope_notes": "Elongated north-south archipelagic envelope spanning ~800 km from Landfall Island to Indira Point (Great Nicobar). Intersects Six Degree Channel."
    },
    "IN-LD": {
        "id": "IN-LD",
        "name": "Lakshadweep",
        "type": "UNION_TERRITORY",
        "coast": "ISLANDS",
        "coastline_km": 132.0,
        "ports": ["Kavaratti Anchorage", "Agatti Anchorage", "Minicoy Anchorage"],
        "primary_mrcc": "MRCC Kochi",
        "bbox": [71.50, 8.00, 74.20, 12.50],  # Provisional search envelope
        "default_offshore_buffer_nm": 50,
        "envelope_notes": "Archipelagic envelope spanning Minicoy to Chetlat. Intersects the Nine Degree Channel international tanker route."
    }
}


def get_all_zones() -> List[Dict[str, Any]]:
    """Return list of all 13 coastal surveillance zones."""
    return list(COASTAL_ZONES.values())


def get_zone_by_id(zone_id: str) -> Dict[str, Any] | None:
    """Retrieve zone dictionary by ID (e.g. 'IN-MH')."""
    return COASTAL_ZONES.get(zone_id)


def compute_expanded_bbox(bbox: List[float], buffer_nm: float) -> List[float]:
    """
    Expand a [min_lon, min_lat, max_lon, max_lat] provisional search bounding box by buffer_nm nautical miles.
    1 nautical mile ≈ 1.852 km ≈ (1/60) degrees latitude.
    """
    buffer_deg_lat = buffer_nm / 60.0
    mean_lat = (bbox[1] + bbox[3]) / 2.0
    import math
    cos_lat = max(0.1, math.cos(math.radians(mean_lat)))
    buffer_deg_lon = buffer_deg_lat / cos_lat

    return [
        round(bbox[0] - buffer_deg_lon, 3),
        round(bbox[1] - buffer_deg_lat, 3),
        round(bbox[2] + buffer_deg_lon, 3),
        round(bbox[3] + buffer_deg_lat, 3)
    ]
