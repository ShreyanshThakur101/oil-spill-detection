from datetime import datetime
from pathlib import Path

from app.pipeline.ais_loader import load_ais_data
from app.pipeline.ais_time_filter import filter_records_by_time
from app.pipeline.ais_proximity import find_nearby_records
from app.pipeline.ais_candidates import group_candidate_vessels

from app.physics.drift_simulation import run_drift_simulation
from app.physics.drift_results import extract_final_particle_positions
from app.physics.drift_summary import summarize_drift

from app.scoring.drift_consistency import (
    calculate_drift_consistency,
)
from app.scoring.vessel_scoring import (
    calculate_vessel_score,
)


def run_ais_drift_pipeline(
    ais_file_path,
    spill_lat,
    spill_lon,
    spill_time,
    time_window_hours=1,
    max_distance_km=15,
    duration_hours=6,
):
    """
    Run the complete AIS + OpenDrift + vessel scoring pipeline.

    Steps:
    1. Load AIS data
    2. Filter AIS records by spill time
    3. Find vessels near the spill location
    4. Group nearby records into candidate vessels
    5. Run OpenDrift simulation
    6. Extract final particle positions
    7. Calculate drift summary
    8. Calculate drift consistency for each vessel
    9. Calculate final vessel suspicion score
    10. Rank vessels
    """

    # -----------------------------------
    # 1. Load AIS data
    # -----------------------------------

    ais_records = load_ais_data(
        ais_file_path
    )

    # -----------------------------------
    # 2. Filter AIS records by spill time
    # -----------------------------------

    time_filtered_records = (
        filter_records_by_time(
            ais_records,
            spill_time,
            time_window_hours,
        )
    )

    # -----------------------------------
    # 3. Find nearby AIS records
    # -----------------------------------

    nearby_records = (
        find_nearby_records(
            time_filtered_records,
            spill_lat,
            spill_lon,
            max_distance_km,
        )
    )

    # -----------------------------------
    # 4. Group candidate vessels
    # -----------------------------------

    candidates = (
        group_candidate_vessels(
            nearby_records
        )
    )

    # -----------------------------------
    # 5. Run OpenDrift simulation
    # -----------------------------------

    simulation = run_drift_simulation(
        spill_lat=spill_lat,
        spill_lon=spill_lon,
        spill_time=spill_time,
        duration_hours=duration_hours,
    )

    # -----------------------------------
    # 6. Extract particle positions
    # -----------------------------------

    particle_positions = (
        extract_final_particle_positions(
            simulation
        )
    )

    # -----------------------------------
    # 7. Create drift summary
    # -----------------------------------

    drift_summary = summarize_drift(
        spill_lat,
        spill_lon,
        particle_positions,
    )

    # -----------------------------------
    # 8 + 9. Calculate scores
    # -----------------------------------

    vessel_scores = []

    for candidate in candidates:

        # Calculate consistency with
        # predicted oil drift
        drift_result = (
            calculate_drift_consistency(
                candidate=candidate,
                ais_records=time_filtered_records,
                drift_summary=drift_summary,
            )
        )

        # Calculate final suspicion score
        score = calculate_vessel_score(
            candidate=candidate,
            spill_time=spill_time,
            max_distance_km=max_distance_km,
            time_window_hours=time_window_hours,
            drift_consistency_score=(
                drift_result[
                    "drift_consistency_score"
                ]
            ),
        )

        # Add extra information
        score["drift_distance_km"] = (
            drift_result[
                "drift_distance_km"
            ]
        )

        vessel_scores.append(score)

    # -----------------------------------
    # 10. Rank vessels
    # -----------------------------------

    vessel_scores.sort(
        key=lambda vessel: vessel[
            "final_score"
        ],
        reverse=True,
    )

    # Add ranking number
    for index, vessel in enumerate(
        vessel_scores,
        start=1,
    ):
        vessel["rank"] = index

    # -----------------------------------
    # Return complete result
    # -----------------------------------

    return {
        "spill": {
            "latitude": spill_lat,
            "longitude": spill_lon,
            "time": spill_time,
        },
        "ais": {
            "total_records": len(
                ais_records
            ),
            "time_filtered_records": len(
                time_filtered_records
            ),
            "nearby_records": len(
                nearby_records
            ),
            "candidate_vessels": candidates,
        },
        "drift": {
            "particle_count": len(
                particle_positions
            ),
            "final_particle_positions": (
                particle_positions
            ),
            "summary": drift_summary,
        },
        "vessel_ranking": vessel_scores,
    }


if __name__ == "__main__":

    data_path = Path(
        "data/raw/ais/synthetic_ais.csv"
    )

    result = run_ais_drift_pipeline(
        ais_file_path=data_path,
        spill_lat=19.0,
        spill_lon=72.0,
        spill_time=datetime(
            2026,
            1,
            1,
            2,
            0,
            0,
        ),
        time_window_hours=1,
        max_distance_km=15,
        duration_hours=6,
    )

    print(
        "\n========== PIPELINE RESULT ==========\n"
    )

    print(
        f"Total AIS records: "
        f"{result['ais']['total_records']}"
    )

    print(
        f"Time filtered records: "
        f"{result['ais']['time_filtered_records']}"
    )

    print(
        f"Nearby records: "
        f"{result['ais']['nearby_records']}"
    )

    print(
        f"Candidate vessels: "
        f"{len(result['ais']['candidate_vessels'])}"
    )

    print(
        f"Drift particles: "
        f"{result['drift']['particle_count']}"
    )

    # -----------------------------------
    # Drift summary
    # -----------------------------------

    summary = result["drift"]["summary"]

    print(
        "\n========== DRIFT SUMMARY ==========\n"
    )

    print(
        f"Particle count: "
        f"{summary['particle_count']}"
    )

    print(
        f"Drift center: "
        f"({summary['center_latitude']}, "
        f"{summary['center_longitude']})"
    )

    print(
        f"Average drift distance: "
        f"{summary['average_distance_km']} km"
    )

    print(
        f"Maximum drift distance: "
        f"{summary['max_distance_km']} km"
    )

    # -----------------------------------
    # Final vessel ranking
    # -----------------------------------

    print(
        "\n========== FINAL VESSEL RANKING ==========\n"
    )

    for vessel in result[
        "vessel_ranking"
    ]:

        print(
            f"Rank #{vessel['rank']}"
        )

        print(
            f"Vessel: "
            f"{vessel['vessel_name']}"
        )

        print(
            f"MMSI: "
            f"{vessel['mmsi']}"
        )

        print(
            f"Distance score: "
            f"{vessel['distance_score']}"
        )

        print(
            f"Time score: "
            f"{vessel['time_score']}"
        )

        print(
            f"Drift score: "
            f"{vessel['drift_score']}"
        )

        print(
            f"Closest drift distance: "
            f"{vessel['drift_distance_km']} km"
        )

        print(
            f"FINAL SUSPICION SCORE: "
            f"{vessel['final_score']}"
        )

        print("-" * 45)

    # -----------------------------------
    # Sample drift particles
    # -----------------------------------

    print(
        "\n========== SAMPLE DRIFT PARTICLES ==========\n"
    )

    for position in (
        result["drift"][
            "final_particle_positions"
        ][:5]
    ):
        print(position)