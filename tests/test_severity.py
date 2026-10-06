import pytest

from app.severity import determine_severity


@pytest.mark.parametrize(
    "categories, text, expected_severity",
    [
        (
            ["TRAUMA", "BLEEDING"],
            "I had a bike accident and I am bleeding heavily",
            "HIGH",
        ),
        (
            ["CARDIAC"],
            "I have severe chest pain",
            "HIGH",
        ),
        (
            ["RESPIRATORY"],
            "I cannot breathe",
            "CRITICAL",
        ),
        (
            ["OBSTETRIC"],
            "My water broke and I need help",
            "HIGH",
        ),
        (
            ["FEVER_INFECTION"],
            "I have a mild fever",
            "LOW",
        ),
    ],
)
def test_determine_severity(categories, text, expected_severity):
    severity = determine_severity(categories, text)

    assert severity == expected_severity
