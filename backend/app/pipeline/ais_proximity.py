from math import radians, sin, cos, sqrt, atan2
from pathlib import Path

from app.pipeline.ais_loader import load_ais_data


def haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two geographic coordinates in kilometres.
    """

    earth_radius_km = 6371.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius_km * c


def find_nearby_records(
    ais_records,
    spill_lat,
    spill_lon,
    max_distance_km,
):
    """
    Find AIS records within max_distance_km of an oil spill location.
    """

    nearby_records = []

    for record in ais_records:

        distance_km = haversine_distance_km(
            record["latitude"],
            record["longitude"],
            spill_lat,
            spill_lon,
        )

        if distance_km <= max_distance_km:

            record_with_distance = record.copy()
            record_with_distance["distance_km"] = round(distance_km, 3)

            nearby_records.append(record_with_distance)

    return nearby_records


if __name__ == "__main__":

    data_path = Path("data/raw/ais/synthetic_ais.csv")

    # Load AIS records
    ais_records = load_ais_data(data_path)

    # Example detected oil spill location
    spill_lat = 19.0
    spill_lon = 72.0

    # Search radius
    max_distance_km = 15

    nearby_records = find_nearby_records(
        ais_records,
        spill_lat,
        spill_lon,
        max_distance_km,
    )

    print(f"Total AIS records: {len(ais_records)}")
    print(f"Nearby AIS records: {len(nearby_records)}")

    print("\nNearby vessels:")

    for record in nearby_records:
        print(
            f"{record['timestamp']} | "
            f"{record['vessel_name']} | "
            f"{record['distance_km']} km"
        )