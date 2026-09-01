import csv
from datetime import datetime, timedelta
from pathlib import Path


OUTPUT_FILE = Path(
    "data/raw/ais/synthetic_ais.csv"
)


def generate_vessel_records(
    writer,
    mmsi,
    vessel_name,
    start_lat,
    start_lon,
    lat_step,
    lon_step,
    speed,
    course,
):
    """
    Generate 12 AIS records for one vessel.
    """

    start_time = datetime(
        2026,
        1,
        1,
        0,
        0,
        0,
    )

    for step in range(12):

        timestamp = (
            start_time
            + timedelta(minutes=30 * step)
        )

        latitude = (
            start_lat
            + lat_step * step
        )

        longitude = (
            start_lon
            + lon_step * step
        )

        writer.writerow(
            {
                "timestamp": timestamp.isoformat(),
                "mmsi": mmsi,
                "vessel_name": vessel_name,
                "latitude": round(latitude, 6),
                "longitude": round(longitude, 6),
                "speed": speed,
                "course": course,
            }
        )


def generate_synthetic_ais_dataset():

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    vessels = [

        # -----------------------------------
        # MAIN SUSPECT
        # Passes exactly through spill location
        # at approximately 02:00
        # -----------------------------------

        {
            "mmsi": "111000111",
            "vessel_name": "Suspect_Vessel_A",
            "start_lat": 19.0,
            "start_lon": 71.8,
            "lat_step": 0.0,
            "lon_step": 0.05,
            "speed": 12.5,
            "course": 90.0,
        },

        # -----------------------------------
        # VERY CLOSE VESSELS
        # -----------------------------------

        {
            "mmsi": "222000222",
            "vessel_name": "Vessel_B",
            "start_lat": 19.05,
            "start_lon": 71.8,
            "lat_step": 0.0,
            "lon_step": 0.05,
            "speed": 11.0,
            "course": 90.0,
        },

        {
            "mmsi": "333000333",
            "vessel_name": "Vessel_C",
            "start_lat": 18.93,
            "start_lon": 71.8,
            "lat_step": 0.0,
            "lon_step": 0.05,
            "speed": 13.0,
            "course": 90.0,
        },

        {
            "mmsi": "444000444",
            "vessel_name": "Vessel_D",
            "start_lat": 19.08,
            "start_lon": 71.75,
            "lat_step": 0.0,
            "lon_step": 0.05,
            "speed": 10.5,
            "course": 90.0,
        },

        # -----------------------------------
        # MODERATELY CLOSE VESSELS
        # -----------------------------------

        {
            "mmsi": "555000555",
            "vessel_name": "Vessel_E",
            "start_lat": 19.15,
            "start_lon": 71.8,
            "lat_step": 0.0,
            "lon_step": 0.05,
            "speed": 14.0,
            "course": 90.0,
        },

        {
            "mmsi": "666000666",
            "vessel_name": "Vessel_F",
            "start_lat": 18.82,
            "start_lon": 71.8,
            "lat_step": 0.0,
            "lon_step": 0.05,
            "speed": 12.0,
            "course": 90.0,
        },

        {
            "mmsi": "777000777",
            "vessel_name": "Vessel_G",
            "start_lat": 19.2,
            "start_lon": 71.7,
            "lat_step": 0.0,
            "lon_step": 0.05,
            "speed": 9.5,
            "course": 90.0,
        },

        {
            "mmsi": "888000888",
            "vessel_name": "Vessel_H",
            "start_lat": 18.78,
            "start_lon": 71.7,
            "lat_step": 0.0,
            "lon_step": 0.05,
            "speed": 15.0,
            "course": 90.0,
        },

        # -----------------------------------
        # FAR VESSELS
        # These should mostly be removed
        # by proximity filtering
        # -----------------------------------

        {
            "mmsi": "999000999",
            "vessel_name": "Vessel_I",
            "start_lat": 20.0,
            "start_lon": 71.8,
            "lat_step": 0.0,
            "lon_step": 0.05,
            "speed": 12.0,
            "course": 90.0,
        },

        {
            "mmsi": "101000101",
            "vessel_name": "Vessel_J",
            "start_lat": 18.0,
            "start_lon": 71.8,
            "lat_step": 0.0,
            "lon_step": 0.05,
            "speed": 10.0,
            "course": 90.0,
        },

        {
            "mmsi": "102000102",
            "vessel_name": "Vessel_K",
            "start_lat": 19.8,
            "start_lon": 71.5,
            "lat_step": 0.0,
            "lon_step": 0.04,
            "speed": 11.0,
            "course": 90.0,
        },

        {
            "mmsi": "103000103",
            "vessel_name": "Vessel_L",
            "start_lat": 18.2,
            "start_lon": 71.5,
            "lat_step": 0.0,
            "lon_step": 0.04,
            "speed": 13.0,
            "course": 90.0,
        },

        {
            "mmsi": "104000104",
            "vessel_name": "Vessel_M",
            "start_lat": 20.2,
            "start_lon": 72.0,
            "lat_step": 0.0,
            "lon_step": 0.03,
            "speed": 9.0,
            "course": 90.0,
        },

        {
            "mmsi": "105000105",
            "vessel_name": "Vessel_N",
            "start_lat": 17.9,
            "start_lon": 72.0,
            "lat_step": 0.0,
            "lon_step": 0.03,
            "speed": 14.0,
            "course": 90.0,
        },

        {
            "mmsi": "106000106",
            "vessel_name": "Vessel_O",
            "start_lat": 19.6,
            "start_lon": 73.0,
            "lat_step": 0.0,
            "lon_step": 0.02,
            "speed": 10.0,
            "course": 90.0,
        },
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "timestamp",
            "mmsi",
            "vessel_name",
            "latitude",
            "longitude",
            "speed",
            "course",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for vessel in vessels:

            generate_vessel_records(
                writer=writer,
                mmsi=vessel["mmsi"],
                vessel_name=vessel[
                    "vessel_name"
                ],
                start_lat=vessel[
                    "start_lat"
                ],
                start_lon=vessel[
                    "start_lon"
                ],
                lat_step=vessel[
                    "lat_step"
                ],
                lon_step=vessel[
                    "lon_step"
                ],
                speed=vessel["speed"],
                course=vessel["course"],
            )

    print(
        "Synthetic AIS dataset generated "
        f"successfully!"
    )

    print(
        f"Total vessels: {len(vessels)}"
    )

    print(
        f"Records per vessel: 12"
    )

    print(
        f"Total AIS records: "
        f"{len(vessels) * 12}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":

    generate_synthetic_ais_dataset()