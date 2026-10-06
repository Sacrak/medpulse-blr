from app.emergency_router import route_emergency


PATIENT_LAT = 12.9716
PATIENT_LON = 77.5946


def test_route_emergency_filters_and_ranks_hospitals(monkeypatch):
    candidates = [
        {
            "name": "Referral Hospital",
            "hospital_type": "BBMP Referral Hospital",
            "latitude": 12.95,
            "longitude": 77.58,
            "available_beds": 10,
            "total_beds": 50,
            "haversine_distance_km": 2.0,
        },
        {
            "name": "Primary Hospital",
            "hospital_type": "BBMP Health Centre",
            "latitude": 12.96,
            "longitude": 77.59,
            "available_beds": 8,
            "total_beds": 20,
            "haversine_distance_km": 3.0,
        },
        {
            "name": "No Bed Hospital",
            "hospital_type": "BBMP Referral Hospital",
            "latitude": 12.97,
            "longitude": 77.60,
            "available_beds": 0,
            "total_beds": 40,
            "haversine_distance_km": 1.5,
        },
    ]

    routed_hospitals = [
        {
            **candidates[0],
            "driving_distance_km": 3.2,
            "duration_minutes": 11.5,
        }
    ]

    ranked_hospitals = [
        {
            **routed_hospitals[0],
            "ranking": 1,
            "ranking_basis": "Lowest ETA",
        }
    ]

    monkeypatch.setattr(
        "app.emergency_router.find_hospitals_for_routing",
        lambda latitude, longitude, limit: candidates,
    )

    def fake_hospital_supports_requirement(
        hospital_type,
        required_level,
    ):
        return hospital_type == "BBMP Referral Hospital"

    monkeypatch.setattr(
        "app.emergency_router.hospital_supports_requirement",
        fake_hospital_supports_requirement,
    )

    captured_routing_candidates = []

    def fake_get_routes_for_candidates(
        latitude,
        longitude,
        suitable_hospitals,
    ):
        captured_routing_candidates.extend(suitable_hospitals)
        return routed_hospitals

    monkeypatch.setattr(
        "app.emergency_router.get_routes_for_candidates",
        fake_get_routes_for_candidates,
    )

    captured_ranking_input = []

    def fake_rank_hospitals(hospitals):
        captured_ranking_input.extend(hospitals)
        return ranked_hospitals

    monkeypatch.setattr(
        "app.emergency_router.rank_hospitals",
        fake_rank_hospitals,
    )

    result = route_emergency(
        categories=["TRAUMA", "BLEEDING"],
        severity="HIGH",
        latitude=PATIENT_LAT,
        longitude=PATIENT_LON,
    )

    assert result["required_facility"] == "REFERRAL"
    assert result["candidates"] == ranked_hospitals

    assert len(captured_routing_candidates) == 1
    assert captured_routing_candidates[0]["name"] == "Referral Hospital"

    assert len(captured_ranking_input) == 1
    assert captured_ranking_input[0]["name"] == "Referral Hospital"


def test_route_emergency_returns_empty_when_no_suitable_hospitals(
    monkeypatch,
):
    candidates = [
        {
            "name": "Primary Hospital",
            "hospital_type": "BBMP Health Centre",
            "latitude": 12.95,
            "longitude": 77.58,
            "available_beds": 10,
            "total_beds": 50,
            "haversine_distance_km": 2.0,
        },
        {
            "name": "Empty Referral Hospital",
            "hospital_type": "BBMP Referral Hospital",
            "latitude": 12.96,
            "longitude": 77.59,
            "available_beds": 0,
            "total_beds": 40,
            "haversine_distance_km": 2.5,
        },
    ]

    monkeypatch.setattr(
        "app.emergency_router.find_hospitals_for_routing",
        lambda latitude, longitude, limit: candidates,
    )

    def fake_hospital_supports_requirement(
        hospital_type,
        required_level,
    ):
        return hospital_type == "BBMP Referral Hospital"

    monkeypatch.setattr(
        "app.emergency_router.hospital_supports_requirement",
        fake_hospital_supports_requirement,
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "Routing/ranking should not be called when no suitable hospitals exist"
        )

    monkeypatch.setattr(
        "app.emergency_router.get_routes_for_candidates",
        fail_if_called,
    )

    monkeypatch.setattr(
        "app.emergency_router.rank_hospitals",
        fail_if_called,
    )

    result = route_emergency(
        categories=["TRAUMA"],
        severity="HIGH",
        latitude=PATIENT_LAT,
        longitude=PATIENT_LON,
    )

    assert result == {
        "required_facility": "REFERRAL",
        "candidates": [],
    }


def test_route_emergency_requires_available_beds(monkeypatch):
    candidates = [
        {
            "name": "Available Referral Hospital",
            "hospital_type": "BBMP Referral Hospital",
            "latitude": 12.95,
            "longitude": 77.58,
            "available_beds": 5,
            "total_beds": 50,
            "haversine_distance_km": 2.0,
        },
        {
            "name": "Full Referral Hospital",
            "hospital_type": "BBMP Referral Hospital",
            "latitude": 12.96,
            "longitude": 77.59,
            "available_beds": 0,
            "total_beds": 50,
            "haversine_distance_km": 2.5,
        },
    ]

    monkeypatch.setattr(
        "app.emergency_router.find_hospitals_for_routing",
        lambda latitude, longitude, limit: candidates,
    )

    monkeypatch.setattr(
        "app.emergency_router.hospital_supports_requirement",
        lambda hospital_type, required_level: True,
    )

    captured_candidates = []

    def fake_get_routes_for_candidates(
        latitude,
        longitude,
        suitable_hospitals,
    ):
        captured_candidates.extend(suitable_hospitals)
        return []

    monkeypatch.setattr(
        "app.emergency_router.get_routes_for_candidates",
        fake_get_routes_for_candidates,
    )

    monkeypatch.setattr(
        "app.emergency_router.rank_hospitals",
        lambda hospitals: hospitals,
    )

    result = route_emergency(
        categories=["TRAUMA"],
        severity="HIGH",
        latitude=PATIENT_LAT,
        longitude=PATIENT_LON,
    )

    assert len(captured_candidates) == 1
    assert captured_candidates[0]["name"] == "Available Referral Hospital"

    assert result["required_facility"] == "REFERRAL"
    assert result["candidates"] == []
