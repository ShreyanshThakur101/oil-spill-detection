from datetime import datetime

from app.physics.drift_simulation import run_drift_simulation
from app.physics.drift_results import extract_final_particle_positions


print("Starting reusable OpenDrift simulation...")

simulation = run_drift_simulation(
    spill_lat=19.0,
    spill_lon=72.0,
    spill_time=datetime(2026, 1, 1, 2, 0, 0),
    duration_hours=6,
)

print("Simulation completed!")

# Extract final positions
positions = extract_final_particle_positions(simulation)

print(f"\nFinal particle positions: {len(positions)}")

print("\nFirst 5 particles:")

for position in positions[:5]:
    print(position)