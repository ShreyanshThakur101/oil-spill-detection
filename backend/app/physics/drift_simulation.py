from datetime import timedelta

from opendrift.models.oceandrift import OceanDrift


def run_drift_simulation(
    spill_lat,
    spill_lon,
    spill_time,
    duration_hours=6,
):
    # Create simulation
    o = OceanDrift(loglevel=20)

    # Temporary constant ocean current
    o.set_config(
        "environment:fallback:x_sea_water_velocity",
        0.2
    )

    o.set_config(
        "environment:fallback:y_sea_water_velocity",
        0.0
    )

    # Release particles at the oil spill location
    o.seed_elements(
        lon=spill_lon,
        lat=spill_lat,
        number=100,
        radius=1000,
        time=spill_time,
    )

    # Run simulation
    o.run(
        duration=timedelta(hours=duration_hours),
        time_step=600,
    )

    return o