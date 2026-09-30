from app.emergency_router import route_emergency


PATIENT_LAT = 12.9716
PATIENT_LON = 77.5946

CATEGORIES = [
    "TRAUMA",
    "BLEEDING",
]

SEVERITY = "HIGH"


print("=" * 70)
print("MEDPULSE EMERGENCY ROUTING")
print("=" * 70)

print("\nCategories:", CATEGORIES)
print("Severity:", SEVERITY)


# ============================================================
# ROUTE EMERGENCY
# ============================================================

result = route_emergency(
    categories=CATEGORIES,
    severity=SEVERITY,
    latitude=PATIENT_LAT,
    longitude=PATIENT_LON,
)


# ============================================================
# REQUIRED FACILITY
# ============================================================

print(
    "Required facility:",
    result["required_facility"]
)


# ============================================================
# RANKED HOSPITALS
# ============================================================

print("\nRanked hospitals:")

hospitals = result["candidates"]

if not hospitals:

    print("No suitable hospitals found.")

else:

    for hospital in hospitals:

        print(
            f"\n#{hospital['ranking']} "
            f"{hospital['name']}"
        )

        print(
            "Type:",
            hospital["hospital_type"]
        )

        print(
            "Available beds:",
            f"{hospital['available_beds']}/"
            f"{hospital['total_beds']}"
        )

        print(
            "Driving distance:",
            f"{hospital['driving_distance_km']:.2f} km"
        )

        print(
            "ETA:",
            f"{hospital['duration_minutes']:.1f} minutes"
        )

        print(
            "Ranking basis:",
            hospital["ranking_basis"]
        )


print("\n" + "=" * 70)
print("EMERGENCY ROUTING TEST COMPLETE")
print("=" * 70)