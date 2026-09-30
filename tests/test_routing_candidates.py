from app.database import find_hospitals_for_routing


PATIENT_LAT = 12.9716
PATIENT_LON = 77.5946


candidates = find_hospitals_for_routing(
    PATIENT_LAT,
    PATIENT_LON,
    limit=20
)


print("\n" + "=" * 70)
print("ROUTING CANDIDATES")
print("=" * 70)

for index, hospital in enumerate(candidates, start=1):
    print(
        f"{index:2}. "
        f"{hospital['name']} | "
        f"{hospital['hospital_type']} | "
        f"{hospital['haversine_distance_km']:.2f} km | "
        f"{hospital['available_beds']}/{hospital['total_beds']} beds"
    )