def get_hospital_facility_level(hospital_type):
    """
    Convert the hospital Type from the dataset
    into the prototype facility level.
    """

    if hospital_type == "BBMP Maternity Home":
        return "MATERNITY"

    if hospital_type in {
        "BBMP Referral Hospital",
        "BBMP Referral/UCHC Facility",
    }:
        return "REFERRAL"

    if hospital_type in {
        "BBMP Health Centre",
        "BBMP Urban Family Welfare Centre",
    }:
        return "PRIMARY"

    return None


def hospital_supports_requirement(hospital_type, required_level):
    """
    Check whether a hospital meets the minimum
    facility level required by the triage result.
    """

    hospital_level = get_hospital_facility_level(
        hospital_type
    )

    if hospital_level is None:
        return False

    if required_level == "PRIMARY":
        return hospital_level in {
            "PRIMARY",
            "MATERNITY",
            "REFERRAL",
        }

    if required_level == "MATERNITY":
        return hospital_level in {
            "MATERNITY",
            "REFERRAL",
        }

    if required_level == "REFERRAL":
        return hospital_level == "REFERRAL"

    return False