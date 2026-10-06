import pytest

from app.ranking import rank_hospitals


@pytest.mark.parametrize(
    "hospitals, expected_order, expected_basis",
    [
        (
            [
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
            ],
            ["Hospital B", "Hospital A"],
            "ETA within tolerance; bed availability used as tiebreaker",
        ),
        (
            [
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
            ],
            ["Hospital B", "Hospital A"],
            "Lowest ETA",
        ),
        (
            [
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
            ],
            ["Hospital B", "Hospital A"],
            "ETA within tolerance; bed availability used as tiebreaker",
        ),
        (
            [
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
            ],
            ["Hospital A", "Hospital B"],
            "Lowest ETA",
        ),
        (
            [
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
            ],
            ["Hospital A", "Hospital B"],
            "Lowest ETA",
        ),
    ],
)
def test_hospital_ranking(
    hospitals,
    expected_order,
    expected_basis,
):
    ranked = rank_hospitals(hospitals)

    actual_order = [hospital["name"] for hospital in ranked]

    assert actual_order == expected_order

    assert ranked[0]["ranking"] == 1
    assert ranked[1]["ranking"] == 2

    assert all(
        hospital["ranking_basis"] == expected_basis
        for hospital in ranked
    )
