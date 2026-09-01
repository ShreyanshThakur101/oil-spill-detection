from datetime import datetime

from app.scoring.vessel_scoring import calculate_vessel_score


candidate = {
    "mmsi": "111000111",
    "vessel_name": "Suspect_Vessel_A",
    "nearby_points": 4,
    "closest_distance_km": 0.0,
    "closest_time": datetime(2026, 1, 1, 2, 0, 0),
}


spill_time = datetime(2026, 1, 1, 2, 0, 0)


result = calculate_vessel_score(
    candidate=candidate,
    spill_time=spill_time,
    max_distance_km=15,
    time_window_hours=1,
)


print("========== VESSEL SCORE ==========\n")

for key, value in result.items():
    print(f"{key}: {value}")