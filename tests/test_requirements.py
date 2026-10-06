import pytest

from app.requirements import get_required_facility_level


@pytest.mark.parametrize(
    "categories, severity, expected_facility",
    [
        (
            ["TRAUMA", "BLEEDING"],
            "HIGH",
            "REFERRAL",
        ),
        (
            ["CARDIAC"],
            "CRITICAL",
            "REFERRAL",
        ),
        (
            ["OBSTETRIC"],
            "MEDIUM",
            "MATERNITY",
        ),
        (
            ["OBSTETRIC"],
            "CRITICAL",
            "REFERRAL",
        ),
        (
            ["FEVER_INFECTION"],
            "LOW",
            "PRIMARY",
        ),
    ],
)
def test_required_facility_level(
    categories,
    severity,
    expected_facility,
):
    facility = get_required_facility_level(
        categories,
        severity,
    )

    assert facility == expected_facility
