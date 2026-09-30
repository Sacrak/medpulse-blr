from app.hospital_capability import (
    get_hospital_facility_level,
    hospital_supports_requirement,
)


test_types = [
    "BBMP Health Centre",
    "BBMP Urban Family Welfare Centre",
    "BBMP Maternity Home",
    "BBMP Referral Hospital",
    "BBMP Referral/UCHC Facility",
]


for hospital_type in test_types:
    level = get_hospital_facility_level(hospital_type)

    print(
        f"{hospital_type} → {level}"
    )


print("\nRequirement tests:")

tests = [
    ("BBMP Health Centre", "PRIMARY"),
    ("BBMP Health Centre", "REFERRAL"),
    ("BBMP Maternity Home", "MATERNITY"),
    ("BBMP Maternity Home", "REFERRAL"),
    ("BBMP Referral Hospital", "REFERRAL"),
    ("BBMP Referral/UCHC Facility", "REFERRAL"),
]


for hospital_type, required_level in tests:
    result = hospital_supports_requirement(
        hospital_type,
        required_level,
    )

    print(
        f"{hospital_type} | "
        f"requires {required_level} → {result}"
    )