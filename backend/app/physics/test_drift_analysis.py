from datetime import datetime

from app.physics.drift_simulation import (
    run_drift_simulation,
)

from app.physics.drift_results import (
    extract_final_particle_positions,
)

from app.physics.drift_analysis import (
    calculate_drift_summary,
)


spill_lat = 19.0
spill_lon = 72.0

simulation = run_drift_simulation(
    spill_lat=spill_lat,
    spill_lon=spill_lon,
    spill_time=datetime(
        2026,
        1,
        1,
        2,
        0,
        0,
    ),
    duration_hours=6,
)

particle_positions = (
    extract_final_particle_positions(
        simulation
    )
)

summary = calculate_drift_summary(
    spill_lat=spill_lat,
    spill_lon=spill_lon,
    particle_positions=particle_positions,
)

print(
    "\n========== DRIFT SUMMARY ==========\n"
)

for key, value in summary.items():

    print(
        f"{key}: {value}"
    )