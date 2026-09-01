from pathlib import Path

from app.pipeline.ais_loader import load_ais_data
from app.pipeline.ais_candidates import group_candidate_vessels
from app.pipeline.ais_proximity import find_nearby_records

from app.physics.drift_simulation import run_drift_simulation
from app.physics.drift_results import extract_final_particle_positions
from app.physics.drift_summary import summarize_drift

from app.scoring.drift_consistency import (
    calculate_drift_consistency,
)


# -----------------------------------
# Load AIS data
# -----------------------------------

data_path = Path(
    "data/raw/ais/synthetic_ais.csv"
)

ais_records = load_ais_data(data_path)


# -----------------------------------
# Find candidate vessels
# -----------------------------------

spill_lat = 19.0
spill_lon = 72.0

nearby_records = find_nearby_records(
    ais_records,
    spill_lat,
    spill_lon,
    max_distance_km=15,
)

candidates = group_candidate_vessels(
    nearby_records
)


# -----------------------------------
# Run drift simulation
# -----------------------------------

from datetime import datetime

spill_time = datetime(
    2026,
    1,
    1,
    2,
    0,
    0,
)

simulation = run_drift_simulation(
    spill_lat=spill_lat,
    spill_lon=spill_lon,
    spill_time=spill_time,
    duration_hours=6,
)

particle_positions = (
    extract_final_particle_positions(
        simulation
    )
)

drift_summary = summarize_drift(
    spill_lat,
    spill_lon,
    particle_positions,
)


# -----------------------------------
# Calculate drift consistency
# -----------------------------------

print(
    "\n========== DRIFT CONSISTENCY ==========\n"
)

for candidate in candidates:

    result = calculate_drift_consistency(
        candidate=candidate,
        ais_records=ais_records,
        drift_summary=drift_summary,
    )

    print(
        f"Vessel: "
        f"{candidate['vessel_name']}"
    )

    print(
        f"MMSI: "
        f"{candidate['mmsi']}"
    )

    print(
        f"Closest drift distance: "
        f"{result['drift_distance_km']} km"
    )

    print(
        f"Drift consistency score: "
        f"{result['drift_consistency_score']}"
    )

    print("-" * 40)