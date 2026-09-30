from app.ranking import rank_hospitals


def run_test(title, hospitals):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    ranked = rank_hospitals(hospitals)

    for hospital in ranked:
        print(f"\n#{hospital['ranking']} {hospital['name']}")
        print(f"ETA: {hospital['duration_minutes']} minutes")
        print(f"Available beds: {hospital['available_beds']}")
        print(f"ETA score: {hospital['eta_score']:.3f}")
        print(f"Bed score: {hospital['bed_score']:.3f}")
        print(f"Ranking: #{hospital['ranking']}")
        print(f"Ranking basis: {hospital['ranking_basis']}")


# ============================================================
# TEST 1: Same ETA, different beds
# ============================================================

same_eta = [
    {
        "name": "Hospital A",
        "duration_minutes": 10,
        "available_beds": 5,
    },
    {
        "name": "Hospital B",
        "duration_minutes": 10,
        "available_beds": 20,
    },
]

run_test(
    "Same ETA, different beds",
    same_eta,
)


# ============================================================
# TEST 2: Same beds, different ETA
# ============================================================

same_beds = [
    {
        "name": "Hospital A",
        "duration_minutes": 15,
        "available_beds": 20,
    },
    {
        "name": "Hospital B",
        "duration_minutes": 10,
        "available_beds": 20,
    },
]

run_test(
    "Same beds, different ETA",
    same_beds,
)


# ============================================================
# TEST 3: ETA within tolerance, beds used as tiebreaker
# ============================================================

within_tolerance = [
    {
        "name": "Hospital A",
        "duration_minutes": 10,
        "available_beds": 2,
    },
    {
        "name": "Hospital B",
        "duration_minutes": 11,
        "available_beds": 40,
    },
]

run_test(
    "ETA within 2-minute tolerance, different beds",
    within_tolerance,
)


# ============================================================
# TEST 4: Large ETA difference
# ============================================================

large_eta_difference = [
    {
        "name": "Hospital A",
        "duration_minutes": 5,
        "available_beds": 2,
    },
    {
        "name": "Hospital B",
        "duration_minutes": 30,
        "available_beds": 50,
    },
]

run_test(
    "Large ETA difference",
    large_eta_difference,
)


# ============================================================
# TEST 5: Zero beds
# ============================================================

zero_beds = [
    {
        "name": "Hospital A",
        "duration_minutes": 8,
        "available_beds": 0,
    },
    {
        "name": "Hospital B",
        "duration_minutes": 12,
        "available_beds": 10,
    },
]

run_test(
    "Zero beds versus available beds",
    zero_beds,
)


print("\n" + "=" * 60)
print("RANKING TESTS COMPLETE")
print("=" * 60)