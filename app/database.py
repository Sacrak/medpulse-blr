import sqlite3
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2
from urllib.parse import quote_plus


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "medpulse.db"


def get_connection():
    connection = sqlite3.connect(
        DB_PATH,
        timeout=10,
        check_same_thread=False
    )

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            hospital_type TEXT,
            address TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            available_beds INTEGER NOT NULL DEFAULT 0
                CHECK (available_beds >= 0),
            total_beds INTEGER NOT NULL DEFAULT 0
                CHECK (total_beds >= 0),
            coordinate_source TEXT,
            coordinate_confidence TEXT,
            bed_data_source TEXT NOT NULL DEFAULT 'simulated'
        )
    """)

    connection.commit()
    connection.close()



def haversine_distance(latitude, longitude, hospital_lat, hospital_lon):
    earth_radius_km = 6371.0

    lat1 = radians(latitude)
    lon1 = radians(longitude)
    lat2 = radians(hospital_lat)
    lon2 = radians(hospital_lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius_km * c


def find_nearest_hospital(latitude, longitude):
    connection = get_connection()

    hospitals = connection.execute("""
        SELECT
            id,
            name,
            hospital_type,
            address,
            latitude,
            longitude
        FROM hospitals
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
    """).fetchall()

    connection.close()

    if not hospitals:
        return None

    nearest = None
    shortest_distance = float("inf")

    for hospital in hospitals:
        hospital_id, name, hospital_type, address, h_lat, h_lon = hospital

        distance = haversine_distance(
            latitude,
            longitude,
            h_lat,
            h_lon
        )

    

        if distance < shortest_distance:
            shortest_distance = distance
            nearest = {
                "id": hospital_id,
                "name": name,
                "hospital_type": hospital_type,
                "address": address,
                "latitude": h_lat,
                "longitude": h_lon,
                "distance_km": distance,
                "google_maps_url": create_google_maps_link(h_lat, h_lon),
            }

    return nearest
def find_nearest_hospitals(latitude, longitude, limit=5):
    """
    Return the closest hospitals by straight-line distance.

    This is only the first-stage filter.
    Google Routes will later calculate actual driving distance/ETA
    for these candidates.
    """
    conn = get_connection()

    hospitals = conn.execute("""
        SELECT
            id,
            name,
            hospital_type,
            address,
            latitude,
            longitude,
            available_beds,
            total_beds,
            bed_data_source
        FROM hospitals
    """).fetchall()

    conn.close()

    candidates = []

    for hospital in hospitals:
        (
            hospital_id,
            name,
            hospital_type,
            address,
            h_lat,
            h_lon,
            available_beds,
            total_beds,
            bed_data_source
        ) = hospital
        

        distance = haversine_distance(
            latitude,
            longitude,
            h_lat,
            h_lon
        )

        candidates.append({
            "id": hospital_id,
            "name": name,
            "hospital_type": hospital_type,
            "address": address,
            "latitude": h_lat,
            "longitude": h_lon,
            "haversine_distance_km": distance,
            "available_beds": available_beds,
            "total_beds": total_beds,
            "bed_data_source": bed_data_source,
        })

    candidates.sort(key=lambda x: x["haversine_distance_km"])

    return candidates[:limit]



def find_hospitals_for_routing(latitude, longitude, limit=20):
    """
    Return a broader set of nearby hospitals for the routing layer.

    The routing layer will later filter these hospitals based on
    facility level, bed availability, and emergency requirements.
    """

    conn = get_connection()

    hospitals = conn.execute("""
        SELECT
            id,
            name,
            hospital_type,
            address,
            latitude,
            longitude,
            available_beds,
            total_beds,
            bed_data_source
        FROM hospitals
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
    """).fetchall()

    conn.close()

    candidates = []

    for hospital in hospitals:
        (
            hospital_id,
            name,
            hospital_type,
            address,
            h_lat,
            h_lon,
            available_beds,
            total_beds,
            bed_data_source
        ) = hospital

        distance = haversine_distance(
            latitude,
            longitude,
            h_lat,
            h_lon
        )

        candidates.append({
            "id": hospital_id,
            "name": name,
            "hospital_type": hospital_type,
            "address": address,
            "latitude": h_lat,
            "longitude": h_lon,
            "haversine_distance_km": distance,
            "available_beds": available_beds,
            "total_beds": total_beds,
            "bed_data_source": bed_data_source,
        })

    candidates.sort(
        key=lambda x: x["haversine_distance_km"]
    )

    return candidates[:limit]



def create_google_maps_link(latitude, longitude):
    destination = f"{latitude},{longitude}"

    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&destination={quote_plus(destination)}"
        "&travelmode=driving"
    )

if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at: {DB_PATH}")