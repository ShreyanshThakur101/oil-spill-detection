from datetime import datetime, timedelta
from pathlib import Path

from app.pipeline.ais_loader import load_ais_data


def filter_records_by_time(
    ais_records,
    spill_time,
    time_window_hours,
):
    """
    Keep only AIS records that fall within a time window
    around the estimated oil spill time.
    """

    start_time = spill_time - timedelta(hours=time_window_hours)
    end_time = spill_time + timedelta(hours=time_window_hours)

    filtered_records = []

    for record in ais_records:

        if start_time <= record["timestamp"] <= end_time:
            filtered_records.append(record)

    return filtered_records


if __name__ == "__main__":

    data_path = Path("data/raw/ais/synthetic_ais.csv")

    # Load AIS data
    ais_records = load_ais_data(data_path)

    # Estimated time when the oil spill occurred
    spill_time = datetime(2026, 1, 1, 2, 0, 0)

    # Search 1 hour before and after the spill
    time_window_hours = 1

    filtered_records = filter_records_by_time(
        ais_records,
        spill_time,
        time_window_hours,
    )

    print(f"Total AIS records: {len(ais_records)}")
    print(f"Records within time window: {len(filtered_records)}")

    print("\nRecords:")

    for record in filtered_records:
        print(
            f"{record['timestamp']} | "
            f"{record['vessel_name']} | "
            f"({record['latitude']}, {record['longitude']})"
        )