from app.database import find_hospitals_for_routing


PATIENT_LAT = 12.9716
PATIENT_LON = 77.5946


def test_find_hospitals_for_routing():
    candidates = find_hospitals_for_routing(
        PATIENT_LAT,
        PATIENT_LON,
        limit=20,
    )

    assert candidates
    assert len(candidates) <= 20

    required_fields = {
        "name",
        "hospital_type",
        "latitude",
        "longitude",
        "haversine_distance_km",
        "available_beds",
        "total_beds",
    }

    for hospital in candidates:
        assert required_fields.issubset(hospital.keys())

        assert hospital["name"]
        assert hospital["hospital_type"]

        assert hospital["latitude"] is not None
        assert hospital["longitude"] is not None

        assert hospital["haversine_distance_km"] >= 0

        assert hospital["available_beds"] >= 0
        assert hospital["total_beds"] >= 0
        assert hospital["available_beds"] <= hospital["total_beds"]


def test_routing_candidates_are_distance_ordered():
    candidates = find_hospitals_for_routing(
        PATIENT_LAT,
        PATIENT_LON,
        limit=20,
    )

    distances = [
        hospital["haversine_distance_km"]
        for hospital in candidates
    ]

    assert distances == sorted(distances)


def test_routing_candidate_limit():
    candidates = find_hospitals_for_routing(
        PATIENT_LAT,
        PATIENT_LON,
        limit=5,
    )

    assert len(candidates) <= 5
