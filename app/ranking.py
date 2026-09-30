ETA_TOLERANCE_MINUTES = 2.0


def rank_hospitals(hospitals):
    """
    Rank hospitals using an ETA-first policy.

    Ranking rules:
    1. Lower driving ETA is preferred.
    2. Hospitals whose ETA is within the tolerance window
       are treated as effectively similar.
    3. Within that ETA window, hospitals with more available
       beds are preferred.
    4. Hospitals with zero available beds should normally be
       filtered before this function is called by the emergency
       router.

    eta_score and bed_score are provided for interpretation
    and debugging only. They do not determine the ranking.
    """

    if not hospitals:
        return []

    max_beds = max(
        hospital["available_beds"]
        for hospital in hospitals
    )

    enriched = []

    for hospital in hospitals:

        if max_beds == 0:
            bed_score = 0.0
        else:
            bed_score = (
                hospital["available_beds"] / max_beds
            )

        enriched.append({
            **hospital,
            "bed_score": bed_score,
        })

    # --------------------------------------------------------
    # Initial ordering by ETA
    # --------------------------------------------------------

    enriched.sort(
        key=lambda hospital: (
            hospital["duration_minutes"],
            -hospital["available_beds"],
        )
    )

    ranked = []

    i = 0

    while i < len(enriched):

        base_eta = enriched[i]["duration_minutes"]

        group = [enriched[i]]

        j = i + 1

        while j < len(enriched):

            eta_difference = (
                enriched[j]["duration_minutes"]
                - base_eta
            )

            if eta_difference >= ETA_TOLERANCE_MINUTES:
                break

            group.append(enriched[j])

            j += 1

        # ----------------------------------------------------
        # Determine ranking basis for this group
        # ----------------------------------------------------

        if len(group) > 1:

            # These hospitals have sufficiently similar ETAs,
            # so available beds become the tiebreaker.

            group.sort(
                key=lambda hospital: hospital["available_beds"],
                reverse=True,
            )

            group_basis = (
                "ETA within tolerance; "
                "bed availability used as tiebreaker"
            )

        else:

            group_basis = "Lowest ETA"

        # Store the basis on every hospital before extending
        # the ranked list.

        for hospital in group:
            hospital["ranking_basis"] = group_basis

        ranked.extend(group)

        i = j

    # --------------------------------------------------------
    # Add display/debug information
    # --------------------------------------------------------

    for index, hospital in enumerate(ranked):

        hospital["ranking"] = index + 1

        hospital["eta_score"] = max(
            0.0,
            1.0 - (
                hospital["duration_minutes"] / 30.0
            ),
        )

    return ranked