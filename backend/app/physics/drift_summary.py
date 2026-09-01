from app.pipeline.ais_proximity import haversine_distance_km


def summarize_drift(
    spill_lat,
    spill_lon,
    particle_positions,
):
    """
    Calculate summary statistics for the final
    OpenDrift particle positions.
    """

    if not particle_positions:
        return {
            "particle_count": 0,
            "center_latitude": None,
            "center_longitude": None,
            "average_distance_km": None,
            "max_distance_km": None,
        }

    center_latitude = sum(
        particle["latitude"]
        for particle in particle_positions
    ) / len(particle_positions)

    center_longitude = sum(
        particle["longitude"]
        for particle in particle_positions
    ) / len(particle_positions)

    distances = []

    for particle in particle_positions:

        distance = haversine_distance_km(
            spill_lat,
            spill_lon,
            particle["latitude"],
            particle["longitude"],
        )

        distances.append(distance)

    average_distance_km = (
        sum(distances) / len(distances)
    )

    max_distance_km = max(distances)

    return {
        "particle_count": len(particle_positions),
        "center_latitude": round(center_latitude, 6),
        "center_longitude": round(center_longitude, 6),
        "average_distance_km": round(
            average_distance_km,
            3,
        ),
        "max_distance_km": round(
            max_distance_km,
            3,
        ),
    }