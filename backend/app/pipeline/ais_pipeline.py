from datetime import datetime
from pathlib import Path

from app.pipeline.ais_loader import load_ais_data
from app.pipeline.ais_time_filter import filter_records_by_time
from app.pipeline.ais_proximity import find_nearby_records
from app.pipeline.ais_candidates import group_candidate_vessels


def run_ais_pipeline(
    file_path,
    spill_lat,
    spill_lon,
    spill_time,
    time_window_hours,
    max_distance_km,
):
    """
    Run the complete AIS candidate vessel detection pipeline.
    """

    # Step 1: Load all AIS records
    ais_records = load_ais_data(file_path)

    # Step 2: Filter records by time
    time_filtered_records = filter_records_by_time(
        ais_records,
        spill_time,
        time_window_hours,
    )

    # Step 3: Filter remaining records by distance
    nearby_records = find_nearby_records(
        time_filtered_records,
        spill_lat,
        spill_lon,
        max_distance_km,
    )

    # Step 4: Group records into unique candidate vessels
    candidates = group_candidate_vessels(nearby_records)

    return {
        "total_records": len(ais_records),
        "time_filtered_records": len(time_filtered_records),
        "nearby_records": len(nearby_records),
        "candidates": candidates,
    }


if __name__ == "__main__":

    data_path = Path("data/raw/ais/synthetic_ais.csv")

    # Oil spill information
    spill_lat = 19.0
    spill_lon = 72.0
    spill_time = datetime(2026, 1, 1, 2, 0, 0)

    # Investigation parameters
    time_window_hours = 1
    max_distance_km = 15

    result = run_ais_pipeline(
        file_path=data_path,
        spill_lat=spill_lat,
        spill_lon=spill_lon,
        spill_time=spill_time,
        time_window_hours=time_window_hours,
        max_distance_km=max_distance_km,
    )

    print("AIS SUSPECT DETECTION PIPELINE")
    print("=" * 40)

    print(f"Total AIS records: {result['total_records']}")
    print(f"After time filtering: {result['time_filtered_records']}")
    print(f"After proximity filtering: {result['nearby_records']}")

    print("\nCandidate vessels:")

    for candidate in result["candidates"]:
        print()
        print(f"Vessel: {candidate['vessel_name']}")
        print(f"MMSI: {candidate['mmsi']}")
        print(f"Nearby points: {candidate['nearby_points']}")
        print(
            f"Closest distance: "
            f"{candidate['closest_distance_km']} km"
        )
        print(f"Closest time: {candidate['closest_time']}")