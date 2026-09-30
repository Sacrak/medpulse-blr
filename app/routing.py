import os
import time
import requests


ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"


def get_route_details(origin_lat, origin_lon, destination_lat, destination_lon):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        raise RuntimeError("GOOGLE_MAPS_API_KEY is not set")

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration",
    }

    payload = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": origin_lat,
                    "longitude": origin_lon,
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": destination_lat,
                    "longitude": destination_lon,
                }
            }
        },
        "travelMode": "DRIVE",
    }

    for attempt in range(3):
        try:
            response = requests.post(
                ROUTES_URL,
                headers=headers,
                json=payload,
                timeout=15,
            )
            
            # Retry temporary server/rate-limit errors.
            if response.status_code in (429, 500, 502, 503, 504):
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
            if response.status_code != 200:
                print("\nGoogle Routes API response:")
                print(response.text)
        
            response.raise_for_status()

            data = response.json()

            if not data.get("routes"):
                raise RuntimeError("No route found")

            route = data["routes"][0]

            distance_km = route["distanceMeters"] / 1000
            duration_seconds = float(route["duration"].rstrip("s"))
            duration_minutes = duration_seconds / 60

            return {
                "distance_km": distance_km,
                "duration_minutes": duration_minutes,
            }

        except requests.RequestException as e:
            if attempt == 2:
                raise RuntimeError(
                    f"Google Routes request failed: {e}"
                ) from e

            time.sleep(2 ** attempt)

    raise RuntimeError("Unable to calculate route")




def get_routes_for_candidates(
    origin_lat,
    origin_lon,
    candidates
):
    """
    Calculate Google driving distance and ETA
    for each shortlisted hospital.

    If routing fails for one hospital, skip that hospital
    and continue routing the remaining candidates.
    """

    results = []

    for hospital in candidates:
        try:
            route = get_route_details(
                origin_lat,
                origin_lon,
                hospital["latitude"],
                hospital["longitude"]
            )

            results.append({
                **hospital,
                "driving_distance_km": route["distance_km"],
                "duration_minutes": route["duration_minutes"],
            })

        except Exception as e:
            print(
                f"\nSkipping {hospital['name']} "
                f"because route calculation failed: {e}"
            )
            continue

    return results

