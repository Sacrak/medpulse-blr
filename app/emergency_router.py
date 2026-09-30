from app.database import find_hospitals_for_routing
from app.requirements import get_required_facility_level
from app.hospital_capability import hospital_supports_requirement
from app.routing import get_routes_for_candidates
from app.ranking import rank_hospitals


def route_emergency(
    categories,
    severity,
    latitude,
    longitude,
):
    """
    Route an emergency case to suitable hospitals.

    Pipeline:
        categories + severity
        -> required facility level
        -> nearby candidates
        -> facility filtering
        -> bed filtering
        -> Google driving routes
        -> ranking

    This is a prototype routing system and not a medical
    decision-making system.
    """

    # ---------------------------------------------------------
    # 1. Determine required facility level
    # ---------------------------------------------------------

    required_level = get_required_facility_level(
        categories,
        severity,
    )

    # ---------------------------------------------------------
    # 2. Get a broad geographic candidate pool
    # ---------------------------------------------------------

    candidates = find_hospitals_for_routing(
        latitude,
        longitude,
        limit=20,
    )

    # ---------------------------------------------------------
    # 3. Filter by facility compatibility
    # ---------------------------------------------------------

    suitable_hospitals = []

    for hospital in candidates:

        if not hospital_supports_requirement(
            hospital["hospital_type"],
            required_level,
        ):
            continue

        # -----------------------------------------------------
        # 4. Require available beds
        # -----------------------------------------------------

        if hospital["available_beds"] <= 0:
            continue

        suitable_hospitals.append(hospital)

    if not suitable_hospitals:
        return {
            "required_facility": required_level,
            "candidates": [],
        }

    # ---------------------------------------------------------
    # 5. Calculate actual driving routes
    # ---------------------------------------------------------

    routed_hospitals = get_routes_for_candidates(
        latitude,
        longitude,
        suitable_hospitals,
    )

    # ---------------------------------------------------------
    # 6. Rank hospitals
    # ---------------------------------------------------------

    ranked_hospitals = rank_hospitals(
        routed_hospitals
    )

    return {
        "required_facility": required_level,
        "candidates": ranked_hospitals,
    }