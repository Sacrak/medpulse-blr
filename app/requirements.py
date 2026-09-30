FACILITY_LEVELS = {
    "PRIMARY": 1,
    "MATERNITY": 2,
    "REFERRAL": 3,
}


def get_required_facility_level(categories, severity):
    """
    Determine the minimum facility level required
    for a triage case.

    This is a prototype routing rule, not a medical diagnosis.
    """

    categories = set(categories)

    # Obstetric emergencies need maternity or referral facilities.
    if "OBSTETRIC" in categories:
        if severity in {"HIGH", "CRITICAL"}:
            return "REFERRAL"
        return "MATERNITY"

    # Serious trauma/bleeding cases should be routed
    # toward referral-level facilities.
    if categories.intersection({
        "TRAUMA",
        "BLEEDING",
        "CARDIAC",
        "RESPIRATORY",
        "NEUROLOGICAL",
        "SEIZURE",
        "POISONING",
        "BURNS",
        "FRACTURE_MUSCULOSKELETAL",
    }):
        if severity in {"HIGH", "CRITICAL"}:
            return "REFERRAL"

    # Medium cases can generally use primary-level facilities
    # in this prototype.
    if severity == "MEDIUM":
        return "PRIMARY"

    # Low-severity cases use primary-level facilities.
    if severity == "LOW":
        return "PRIMARY"

    # Conservative fallback for HIGH/CRITICAL cases.
    if severity in {"HIGH", "CRITICAL"}:
        return "REFERRAL"

    return "PRIMARY"