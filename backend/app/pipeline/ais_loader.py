from pathlib import Path
import csv
from datetime import datetime


def load_ais_data(file_path: str):
    """
    Load AIS vessel data from a CSV file.

    Returns a list of dictionaries containing AIS records.
    """

    records = []

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            record = {
                "timestamp": datetime.fromisoformat(row["timestamp"]),
                "mmsi": row["mmsi"],
                "vessel_name": row["vessel_name"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "speed": float(row["speed"]),
                "course": float(row["course"]),
            }

            records.append(record)

    return records


if __name__ == "__main__":

    data_path = Path("data/raw/ais/synthetic_ais.csv")

    ais_records = load_ais_data(data_path)

    print(f"Loaded {len(ais_records)} AIS records")

    print("\nFirst 3 records:")

    for record in ais_records[:3]:
        print(record)