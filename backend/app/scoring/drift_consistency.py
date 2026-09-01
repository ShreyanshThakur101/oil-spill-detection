from app.pipeline.ais_proximity import haversine_distance_km


def calculate_drift_consistency(
    candidate,
    ais_records,
    drift_summary,
    max_drift_distance_km=20,
):
    """
    Calculate how consistent a vessel's AIS track is with
    the predicted oil drift region.

    The vessel receives a higher score when its AIS positions
    are closer to the predicted drift center.
    """

    vessel_mmsi = candidate["mmsi"]

    # Get predicted center of the oil particles
    drift_lat = drift_summary["center_latitude"]
    drift_lon = drift_summary["center_longitude"]

    # Find AIS records belonging to this vessel
    vessel_records = [
        record
        for record in ais_records
        if record["mmsi"] == vessel_mmsi
    ]

    if not vessel_records:
        return {
            "drift_distance_km": None,
            "drift_consistency_score": 0.0,
        }

    # Calculate distance from every vessel position
    # to the predicted drift center
    distances = []

    for record in vessel_records:

        distance = haversine_distance_km(
            record["latitude"],
            record["longitude"],
            drift_lat,
            drift_lon,
        )

        distances.append(distance)

    # Use closest approach to drift center
    closest_drift_distance = min(distances)

    # Convert distance to a score between 0 and 1
    drift_consistency_score = max(
        0.0,
        1 - (
            closest_drift_distance
            / max_drift_distance_km
        ),
    )

    return {
        "drift_distance_km": round(
            closest_drift_distance,
            3,
        ),
        "drift_consistency_score": round(
            drift_consistency_score,
            3,
        ),
    }