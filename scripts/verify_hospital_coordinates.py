import os
import math
import time
import requests
import pandas as pd
import re


INPUT_FILE = "data/processed/bangalore_hospitals_enriched.csv"
OUTPUT_FILE = "data/processed/google_coordinate_audit.csv"

GOOGLE_API_URL = "https://places.googleapis.com/v1/places:searchText"

HEALTHCARE_TYPES = {
    "hospital",
    "general_hospital",
    "medical_center",
    "medical_clinic",
}
def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate straight-line distance between two coordinates."""

    R = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(a))


def search_google_places(name, latitude, longitude):
    """Search Google Places near the BBMP coordinate."""

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GOOGLE_MAPS_API_KEY environment variable is not set."
        )

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "places.displayName,"
            "places.formattedAddress,"
            "places.location,"
            "places.primaryType"
        ),
    }

    payload = {
        "textQuery": name,
        "pageSize": 5,
        "locationBias": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": 3000.0,
            }
        },
        "regionCode": "IN",
    }
    last_error = None

    for attempt in range(3):
        try:
            response = requests.post(
                GOOGLE_API_URL,
                headers=headers,
                json=payload,
                timeout=15,
            )

            response.raise_for_status()

            return response.json().get("places", [])

        except requests.RequestException as e:
            last_error = e

            if attempt < 2:
                wait_time = 2 ** attempt
                print(
                    f"  Request failed. "
                    f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)

    raise RuntimeError(
        f"Google Places request failed after 3 attempts: {last_error}"
    )
    

    response.raise_for_status()

    return response.json().get("places", [])
def normalize_name(name):
    """Normalize a facility name for conservative name comparison."""

    name = str(name).lower()

    # Remove punctuation
    name = re.sub(r"[^a-z0-9\s]", " ", name)

    # Normalize common healthcare abbreviations
    replacements = {
        "h c": "health centre",
        "hc": "health centre",
        "ufwc": "health centre",
        "uphc": "health centre",
        "health center": "health centre",
        "reffrel": "referral",
        "refferal": "referral",
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    # Collapse repeated spaces
    name = re.sub(r"\s+", " ", name).strip()

    return name
def names_correspond(bbmp_name, google_name):
    """
    Check whether the Google name meaningfully corresponds
    to the BBMP facility name.
    """

    bbmp = normalize_name(bbmp_name)
    google = normalize_name(google_name)

    bbmp_tokens = set(bbmp.split())
    google_tokens = set(google.split())

    # Ignore generic healthcare words when comparing identity.
    generic = {
        "health",
        "centre",
        "center",
        "hospital",
        "home",
        "government",
        "urban",
        "primary",
        "medical",
        "healthcare",
    }

    bbmp_specific = bbmp_tokens - generic
    google_specific = google_tokens - generic

    if not bbmp_specific:
        return False

    # Require at least one meaningful facility/location token
    # to appear in both names.
    overlap = bbmp_specific.intersection(google_specific)

    return len(overlap) >= 1

def main():

    print("Loading hospital dataset...")

    df = pd.read_csv(INPUT_FILE)

# Only verify facilities that currently have usable coordinates
# and are marked as routable by our dataset-building pipeline.
    df = df[df["is_routable"] == True].copy()
    '''
    FAILED_FACILITIES = {
        "A. D. Halli H.C.",
        "Anjanappa Garden H.C.",
        "Audugodi H.C.",
        "Bapujinagar H.C.",
        "Bhuvaneshwari Nagar H.C.",
        "K. G. Halli H.C.",
        "Kodihalli H.C.",
        "Koramangala H.C.",
        "Mathikere H.C.",
        "Murphy Town H.C.",
        "Pantharpalya H.C.",
        "Taskar Town H.C.",
        "R. C. Pura UFWC",
        "Shanthinagar UFWC",
        "H. Siddaiah Road Hospital",
        "Srirampuram Referral Hospital",
        "Banashankari Referral Hospital",
        "Halsuru reffrel hospital",
    }
        
    df = df[df["Name"].isin(FAILED_FACILITIES)].copy()
    '''

    results = []
    

    print(f"Facilities to verify: {len(df)}")

    for index, row in df.iterrows():

        name = str(row["Name"])
        bbmp_lat = float(row["latitude"])
        bbmp_lon = float(row["longitude"])

        print(
            f"[{index + 1}/{len(df)}] "
            f"Searching: {name}"
        )

        try:

            places = search_google_places(
                name,
                bbmp_lat,
                bbmp_lon,
            )

            if not places:

                results.append({
                    "name": name,
                    "bbmp_latitude": bbmp_lat,
                    "bbmp_longitude": bbmp_lon,
                    "google_name": "",
                    "google_address": "",
                    "google_type": "",
                    "google_latitude": "",
                    "google_longitude": "",
                    "coordinate_difference_km": "",
                    "verification_status": "NO_MATCH",
                })

                continue

            # Keep all returned candidates in the audit.
            for rank, place in enumerate(places, start=1):

                google_name = (
                    place.get("displayName", {})
                    .get("text", "")
                )

                google_address = place.get(
                    "formattedAddress",
                    ""
                )

                google_type = place.get(
                    "primaryType",
                    ""
                )

                location = place.get("location", {})

                google_lat = location.get("latitude")
                google_lon = location.get("longitude")

                if google_lat is not None and google_lon is not None:

                    difference = haversine_km(
                        bbmp_lat,
                        bbmp_lon,
                        google_lat,
                        google_lon,
                    )

                else:
                    difference = ""

                # We deliberately do NOT automatically call
                # this verified.
                name_match = names_correspond(
                    name,
                    google_name,
                )

                if (
                    google_lat is not None
                    and google_lon is not None
                    and difference <= 0.5
                    and google_type in HEALTHCARE_TYPES
                    and name_match
                ):
                    status = "POSSIBLE_MATCH"
                else:
                    status = "NEEDS_REVIEW"
                
                

                results.append({
                    "name": name,
                    "bbmp_latitude": bbmp_lat,
                    "bbmp_longitude": bbmp_lon,
                    "google_rank": rank,
                    "google_name": google_name,
                    "google_address": google_address,
                    "google_type": google_type,
                    "google_latitude": google_lat,
                    "google_longitude": google_lon,
                    "coordinate_difference_km": difference,
                    "verification_status": status,
                })

        except Exception as e:

            results.append({
                "name": name,
                "bbmp_latitude": bbmp_lat,
                "bbmp_longitude": bbmp_lon,
                "google_name": "",
                "google_address": "",
                "google_type": "",
                "google_latitude": "",
                "google_longitude": "",
                "coordinate_difference_km": "",
                "verification_status": f"ERROR: {e}",
            })

        # Small delay so we don't hammer the API.
        time.sleep(0.2)

    audit_df = pd.DataFrame(results)

    audit_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    verification = (

        audit_df
        .groupby("name")
        .apply(
            lambda group: (
                "google_corroborated"
                if any(
                    (group["verification_status"] == "POSSIBLE_MATCH")
                    & (group["google_name"].str.len() > 0)
                )
                else "needs_review"
            
            )
        )
        .reset_index(name="coordinate_verification")
    )
    verification.to_csv(
        "data/processed/coordinate_verification.csv",
        index=False,
    )
    print()
    print("=" * 60)
    print("AUDIT COMPLETE")
    print("=" * 60)
    print(f"Output: {OUTPUT_FILE}")
    print()
    print(
        audit_df["verification_status"]
        .value_counts()
        .to_string()
    )


if __name__ == "__main__":
    main()