def extract_final_particle_positions(simulation):
    """
    Extract the final longitude and latitude
    of all particles from an OpenDrift simulation.
    """

    positions = []

    for lon, lat in zip(
        simulation.elements.lon,
        simulation.elements.lat,
    ):
        positions.append(
            {
                "longitude": float(lon),
                "latitude": float(lat),
            }
        )

    return positions