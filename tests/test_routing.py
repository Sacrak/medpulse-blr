from app.routing import get_routes_for_candidates


PATIENT_LAT = 12.9716
PATIENT_LON = 77.5946


def test_get_routes_for_candidates(monkeypatch):
    candidates = [
        {
            "name": "Hospital A",
            "hospital_type": "BBMP Referral Hospital",
            "latitude": 12.95,
            "longitude": 77.58,
            "available_beds": 10,
            "total_beds": 50,
            "haversine_distance_km": 2.5,
        },
        {
            "name": "Hospital B",
            "hospital_type": "BBMP Health Centre",
            "latitude": 12.96,
            "longitude": 77.59,
            "available_beds": 5,
            "total_beds": 20,
            "haversine_distance_km": 3.0,
        },
    ]

    def fake_get_route_details(
        origin_lat,
        origin_lon,
        destination_lat,
        destination_lon,
    ):
        if destination_lat == 12.95:
            return {
                "distance_km": 3.2,
                "duration_minutes": 11.5,
            }

        return {
            "distance_km": 4.1,
            "duration_minutes": 15.0,
        }

    monkeypatch.setattr(
        "app.routing.get_route_details",
        fake_get_route_details,
    )

    routes = get_routes_for_candidates(
        PATIENT_LAT,
        PATIENT_LON,
        candidates,
    )

    assert len(routes) == 2

    assert routes[0]["name"] == "Hospital A"
    assert routes[0]["driving_distance_km"] == 3.2
    assert routes[0]["duration_minutes"] == 11.5

    assert routes[1]["name"] == "Hospital B"
    assert routes[1]["driving_distance_km"] == 4.1
    assert routes[1]["duration_minutes"] == 15.0

    assert routes[0]["available_beds"] == 10
    assert routes[0]["total_beds"] == 50
    assert routes[1]["available_beds"] == 5
    assert routes[1]["total_beds"] == 20


def test_get_routes_skips_failed_hospital(monkeypatch):
    candidates = [
        {
            "name": "Working Hospital",
            "hospital_type": "BBMP Referral Hospital",
            "latitude": 12.95,
            "longitude": 77.58,
            "available_beds": 10,
            "total_beds": 50,
            "haversine_distance_km": 2.5,
        },
        {
            "name": "Failed Hospital",
            "hospital_type": "BBMP Health Centre",
            "latitude": 12.96,
            "longitude": 77.59,
            "available_beds": 5,
            "total_beds": 20,
            "haversine_distance_km": 3.0,
        },
    ]

    def fake_get_route_details(
        origin_lat,
        origin_lon,
        destination_lat,
        destination_lon,
    ):
        if destination_lat == 12.96:
            raise RuntimeError("Simulated routing failure")

        return {
            "distance_km": 3.2,
            "duration_minutes": 11.5,
        }

    monkeypatch.setattr(
        "app.routing.get_route_details",
        fake_get_route_details,
    )

    routes = get_routes_for_candidates(
        PATIENT_LAT,
        PATIENT_LON,
        candidates,
    )

    assert len(routes) == 1
    assert routes[0]["name"] == "Working Hospital"


def test_get_routes_with_no_candidates(monkeypatch):
    def fake_get_route_details(*args, **kwargs):
        raise AssertionError("Routing API should not be called")

    monkeypatch.setattr(
        "app.routing.get_route_details",
        fake_get_route_details,
    )

    routes = get_routes_for_candidates(
        PATIENT_LAT,
        PATIENT_LON,
        [],
    )

    assert routes == []
