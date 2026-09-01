from pathlib import Path

from app.pipeline.ais_loader import load_ais_data
from app.pipeline.ais_proximity import find_nearby_records


def group_candidate_vessels(nearby_records):
    """
    Group nearby AIS records into unique candidate vessels.
    """

    candidates = {}

    for record in nearby_records:

        mmsi = record["mmsi"]

        if mmsi not in candidates:
            candidates[mmsi] = {
                "mmsi": mmsi,
                "vessel_name": record["vessel_name"],
                "nearby_points": 0,
                "closest_distance_km": record["distance_km"],
                "closest_time": record["timestamp"],
            }

        candidate = candidates[mmsi]

        candidate["nearby_points"] += 1

        if record["distance_km"] < candidate["closest_distance_km"]:
            candidate["closest_distance_km"] = record["distance_km"]
            candidate["closest_time"] = record["timestamp"]

    return list(candidates.values())


if __name__ == "__main__":

    data_path = Path("data/raw/ais/synthetic_ais.csv")

    ais_records = load_ais_data(data_path)

    spill_lat = 19.0
    spill_lon = 72.0
    max_distance_km = 15

    nearby_records = find_nearby_records(
        ais_records,
        spill_lat,
        spill_lon,
        max_distance_km,
    )

    candidates = group_candidate_vessels(nearby_records)

    print(f"Candidate vessels: {len(candidates)}\n")

    for candidate in candidates:
        print(f"Vessel: {candidate['vessel_name']}")
        print(f"MMSI: {candidate['mmsi']}")
        print(f"Nearby AIS points: {candidate['nearby_points']}")
        print(f"Closest distance: {candidate['closest_distance_km']} km")
        print(f"Closest approach: {candidate['closest_time']}")
        print("-" * 40)