from datetime import datetime, timedelta

from opendrift.models.oceandrift import OceanDrift


print("Starting OpenDrift simulation...")

# Create an ocean drift simulation
o = OceanDrift(loglevel=20)

# Add simple constant environmental conditions
o.set_config("environment:fallback:x_sea_water_velocity", 0.2)
o.set_config("environment:fallback:y_sea_water_velocity", 0.0)

# Define when the oil particles are released
start_time = datetime(2026, 1, 1, 0, 0, 0)

# Release 100 particles near a sample location
o.seed_elements(
    lon=72.0,
    lat=18.5,
    number=100,
    radius=1000,
    time=start_time,
)

print("Particles seeded. Running simulation...")

# Run simulation for 6 hours
o.run(
    duration=timedelta(hours=6),
    time_step=600,
)

print("Simulation completed successfully!")
print(o)