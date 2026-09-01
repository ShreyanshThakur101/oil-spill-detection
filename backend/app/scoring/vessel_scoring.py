from datetime import datetime


def calculate_vessel_score(
    candidate,
    spill_time: datetime,
    max_distance_km: float,
    time_window_hours: float,
    drift_consistency_score: float = 0.0,
):
    """
    Calculate the final suspicion score for a candidate vessel.

    The score combines:
    1. Distance from the spill location
    2. Time proximity to the estimated spill time
    3. Consistency with the predicted oil drift
    """

    # -----------------------------------
    # 1. Distance score
    # -----------------------------------

    closest_distance = candidate["closest_distance_km"]

    distance_score = max(
        0.0,
        1 - (
            closest_distance
            / max_distance_km
        ),
    )

    # -----------------------------------
    # 2. Time score
    # -----------------------------------

    closest_time = candidate["closest_time"]

    time_difference_hours = abs(
        (
            closest_time
            - spill_time
        ).total_seconds()
    ) / 3600

    time_score = max(
        0.0,
        1 - (
            time_difference_hours
            / time_window_hours
        ),
    )

    # -----------------------------------
    # 3. Drift consistency score
    # -----------------------------------

    drift_score = max(
        0.0,
        min(
            1.0,
            drift_consistency_score,
        ),
    )

    # -----------------------------------
    # Final weighted score
    # -----------------------------------

    final_score = (
        0.45 * distance_score
        + 0.30 * time_score
        + 0.25 * drift_score
    )

    return {
        "mmsi": candidate["mmsi"],
        "vessel_name": candidate["vessel_name"],
        "distance_score": round(
            distance_score,
            3,
        ),
        "time_score": round(
            time_score,
            3,
        ),
        "drift_score": round(
            drift_score,
            3,
        ),
        "final_score": round(
            final_score,
            3,
        ),
    }