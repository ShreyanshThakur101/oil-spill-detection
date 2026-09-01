from app.pipeline.ais_proximity import haversine_distance_km


def calculate_drift_summary(
    spill_lat,
    spill_lon,
    particle_positions,
):
    """
    Analyse the final positions of OpenDrift particles.

    Calculates:
    - Number of particles
    - Centre of the final oil particle cloud
    - Average distance travelled from spill origin
    - Maximum distance travelled from spill origin
    """

    if not particle_positions:
        return {
            "particle_count": 0,
            "center_latitude": None,
            "center_longitude": None,
            "average_distance_km": 0.0,
            "max_distance_km": 0.0,
        }

    particle_count = len(
        particle_positions
    )

    # Calculate centre of the particle cloud

    center_latitude = sum(
        position["latitude"]
        for position in particle_positions
    ) / particle_count

    center_longitude = sum(
        position["longitude"]
        for position in particle_positions
    ) / particle_count

    # Calculate distance travelled by each particle

    distances = []

    for position in particle_positions:

        distance_km = (
            haversine_distance_km(
                spill_lat,
                spill_lon,
                position["latitude"],
                position["longitude"],
            )
        )

        distances.append(
            distance_km
        )

    average_distance_km = (
        sum(distances)
        / len(distances)
    )

    max_distance_km = max(
        distances
    )

    return {
        "particle_count": particle_count,
        "center_latitude": round(
            center_latitude,
            6,
        ),
        "center_longitude": round(
            center_longitude,
            6,
        ),
        "average_distance_km": round(
            average_distance_km,
            3,
        ),
        "max_distance_km": round(
            max_distance_km,
            3,
        ),
    }