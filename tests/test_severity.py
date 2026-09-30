from app.severity import determine_severity


test_cases = [
    (
        ["TRAUMA", "BLEEDING"],
        "I had a bike accident and I am bleeding heavily",
    ),
    (
        ["CARDIAC"],
        "I have severe chest pain",
    ),
    (
        ["RESPIRATORY"],
        "I cannot breathe",
    ),
    (
        ["OBSTETRIC"],
        "My water broke and I need help",
    ),
    (
        ["FEVER_INFECTION"],
        "I have a mild fever",
    ),
]


for categories, text in test_cases:

    severity = determine_severity(
        categories,
        text,
    )

    print(
        f"{categories} | "
        f"{text} → {severity}"
    )