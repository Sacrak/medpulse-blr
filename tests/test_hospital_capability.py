import pytest

from app.hospital_capability import (
    get_hospital_facility_level,
    hospital_supports_requirement,
)


@pytest.mark.parametrize(
    "hospital_type, expected_level",
    [
        ("BBMP Health Centre", "PRIMARY"),
        ("BBMP Urban Family Welfare Centre", "PRIMARY"),
        ("BBMP Maternity Home", "MATERNITY"),
        ("BBMP Referral Hospital", "REFERRAL"),
        ("BBMP Referral/UCHC Facility", "REFERRAL"),
    ],
)
def test_get_hospital_facility_level(
    hospital_type,
    expected_level,
):
    level = get_hospital_facility_level(hospital_type)

    assert level == expected_level


@pytest.mark.parametrize(
    "hospital_type, required_level, expected_result",
    [
        ("BBMP Health Centre", "PRIMARY", True),
        ("BBMP Health Centre", "REFERRAL", False),
        ("BBMP Maternity Home", "MATERNITY", True),
        ("BBMP Maternity Home", "REFERRAL", False),
        ("BBMP Referral Hospital", "REFERRAL", True),
        ("BBMP Referral/UCHC Facility", "REFERRAL", True),
    ],
)
def test_hospital_supports_requirement(
    hospital_type,
    required_level,
    expected_result,
):
    result = hospital_supports_requirement(
        hospital_type,
        required_level,
    )

    assert result == expected_result
