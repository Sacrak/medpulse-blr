from app.requirements import get_required_facility_level


test_cases = [
    (
        ["TRAUMA", "BLEEDING"],
        "HIGH",
    ),
    (
        ["CARDIAC"],
        "CRITICAL",
    ),
    (
        ["OBSTETRIC"],
        "MEDIUM",
    ),
    (
        ["OBSTETRIC"],
        "CRITICAL",
    ),
    (
        ["FEVER_INFECTION"],
        "LOW",
    ),
]


for categories, severity in test_cases:
    level = get_required_facility_level(
        categories,
        severity
    )

    print(
        f"{categories} | "
        f"{severity} → {level}"
    )