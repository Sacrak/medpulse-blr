def determine_severity(categories, text):
    """
    Determine an operational triage severity.

    This is a prototype routing rule and is NOT a medical diagnosis.

    Severity uses:
    1. Critical emergency phrases
    2. Structured NLP category combinations
    3. Explicit high-risk phrases
    4. Serious-category counts
    """

    categories = set(categories)
    text = (text or "").lower().strip()

    # =========================================================
    # CRITICAL EMERGENCY INDICATORS
    # =========================================================

    critical_terms = [
        "not breathing",
        "stopped breathing",
        "unconscious",
        "unresponsive",
        "not responding",
        "not responsive",
        "does not respond",
        "not waking up",
        "cardiac arrest",
        "heart stopped",
        "cannot breathe",
        "can't breathe",

        "बेहोश",
        "होश नहीं",
        "होश में नहीं",
        "जवाब नहीं दे रहा",
        "जवाब नहीं दे रही",
        "जवाब नहीं दे रहे",
        "रेस्पॉंस नहीं कर रहा",
        "रेस्पॉंस नहीं कर रही",
        "रेस्पॉंस नहीं कर रहे",
        "रिस्पॉन्स नहीं कर रहा",
        "रिस्पॉन्स नहीं कर रही",
        "रिस्पॉन्स नहीं कर रहे",
        "सांस नहीं आ रही",
        "साँस नहीं आ रही",
        "सांस नहीं ले रहा",
        "साँस नहीं ले रहा",
        "सांस नहीं ले रही",
        "साँस नहीं ले रही",
    ]

    # =========================================================
    # HIGH-RISK EMERGENCY INDICATORS
    # =========================================================

    high_terms = [
        "severe chest pain",
        "crushing chest pain",
        "pressure in my chest",
        "severe pressure in my chest",

        "massive bleeding",
        "heavy bleeding",
        "bleeding heavily",
        "heavy blood loss",
        "blood loss",
        "bleeding badly",

        "severe injury",
        "serious injury",
        "severe pain",
        "deep wound",
        "deep cut",
        "fractured",
        "broken bone",
        "major accident",
        "bike accident",
        "car accident",
        "road accident",

        "seizure",
        "convulsing",

        "poisoning",
        "overdose",
        "swallowed poison",
        "ingested poison",
        "swallowed a large amount",
        "swallowed chemical",
        "swallowed cleaning chemical",
        "drank cleaning chemical",
        "ingested chemical",
        "chemical ingestion",
        "chemical exposure",

        "burned badly",
        "badly burned",
        "severe burn",

        # Snake / venomous animal bite
        "snake bite",
        "snakebite",
        "snake bit",
        "bitten by a snake",
        "a snake bit me",

        "बहुत ज्यादा खून",
        "बहुत ज़्यादा खून",
        "बहुत खून बह",
        "ज्यादा खून बह",
        "तेज सीने में दर्द",
        "सीने में बहुत दर्द",
        "बहुत तेज दर्द",
        "गंभीर चोट",
        "हड्डी टूट",
        "दौरा",
        "जहर",
        "जहर खा",
        "बहुत बुरी तरह जल",
        "बड़ा एक्सीडेंट",
        "अक्सीडेंट",
        "एक्सीडेंट",
    ]

    # =========================================================
    # OBSTETRIC EMERGENCY INDICATORS
    # =========================================================

    obstetric_terms = [
        "water broke",
        "waters broke",
        "water has broken",
        "waters have broken",
        "heavy bleeding during pregnancy",
        "pregnant and bleeding",
        "pregnant and having heavy bleeding",
        "pregnancy bleeding",
        "पानी टूट गया",
        "पानी निकल रहा",
        "प्रेग्नेंट और ब्लीडिंग",
        "गर्भावस्था में खून",
        "गर्भवती और खून",
    ]

    # =========================================================
    # 1. CRITICAL TAKES ABSOLUTE PRECEDENCE
    # =========================================================

    if any(term in text for term in critical_terms):
        return "CRITICAL"

    # =========================================================
    # 2. CATEGORY-AWARE HIGH-RISK RULES
    # =========================================================

    if "OBSTETRIC" in categories and "BLEEDING" in categories:
        return "HIGH"

    if (
        "TRAUMA" in categories
        and "FRACTURE_MUSCULOSKELETAL" in categories
    ):
        return "HIGH"

    if "POISONING" in categories:
        return "HIGH"

    # =========================================================
    # 3. EXPLICIT HIGH-RISK TEXT
    # =========================================================

    if any(term in text for term in high_terms):
        return "HIGH"

    # =========================================================
    # 4. SERIOUS EMERGENCY CATEGORIES
    # =========================================================

    serious_categories = {
        "CARDIAC",
        "BLEEDING",
        "TRAUMA",
        "SEIZURE",
        "POISONING",
        "RESPIRATORY",
        "NEUROLOGICAL",
    }

    serious_count = len(categories.intersection(serious_categories))

    # =========================================================
    # 5. MULTIPLE SERIOUS CATEGORIES
    # =========================================================

    if serious_count >= 2:
        return "HIGH"

    # =========================================================
    # 6. OBSTETRIC CASE
    # =========================================================

    if "OBSTETRIC" in categories:
        if any(term in text for term in obstetric_terms):
            return "HIGH"
        return "MEDIUM"

    # =========================================================
    # 7. ONE SERIOUS CATEGORY
    # =========================================================

    if serious_count == 1:
        return "MEDIUM"

    # =========================================================
    # 8. DEFAULT
    # =========================================================

    return "LOW"
