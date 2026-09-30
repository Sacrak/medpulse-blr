from app.database import find_nearest_hospitals
from app.routing import get_routes_for_candidates


# Temporary test location: central Bengaluru
PATIENT_LAT = 12.9716
PATIENT_LON = 77.5946


print("\nFinding nearby hospitals...")

candidates = find_nearest_hospitals(
    PATIENT_LAT,
    PATIENT_LON,
    limit=5
)

print(f"Found {len(candidates)} nearby hospitals.\n")

for hospital in candidates:
    print(
        f"{hospital['name']} | "
        f"{hospital['available_beds']}/{hospital['total_beds']} beds | "
        f"{hospital['haversine_distance_km']:.2f} km"
    )


# Keep only hospitals with available beds
candidates_with_beds = [
    hospital
    for hospital in candidates
    if hospital["available_beds"] > 0
]


print("\nCalculating Google driving routes...")

routes = get_routes_for_candidates(
    PATIENT_LAT,
    PATIENT_LON,
    candidates_with_beds
)


print("\n" + "=" * 70)
print("ROUTING RESULTS")
print("=" * 70)

for hospital in routes:
    print(f"\nHospital: {hospital['name']}")

    print(
        f"Available beds: "
        f"{hospital['available_beds']}/{hospital['total_beds']}"
    )

    print(
        f"Driving distance: "
        f"{hospital['driving_distance_km']:.2f} km"
    )

    print(
        f"ETA: "
        f"{hospital['duration_minutes']:.1f} minutes"
    )

    