import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "bangalore_hospitals_enriched.csv"
DB_PATH = PROJECT_ROOT / "data" / "medpulse.db"


def load_hospitals():
    df = pd.read_csv(CSV_PATH)

    # Only facilities with verified coordinates
    routable = df[df["is_routable"] == True].copy()

    connection = sqlite3.connect(DB_PATH)

    # Avoid duplicate records if the loader is run again
    connection.execute("DELETE FROM hospitals")

    for _, row in routable.iterrows():
        total_beds = int(row["Beds"]) if pd.notna(row["Beds"]) else 0

        connection.execute(
            """
            INSERT INTO hospitals (
                name,
                hospital_type,
                address,
                latitude,
                longitude,
                available_beds,
                total_beds,
                coordinate_source,
                coordinate_confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["Name"],
                row["Type"],
                row["Address"],
                float(row["latitude"]),
                float(row["longitude"]),
                total_beds,
                total_beds,
                row["coordinate_source"],
                row["coordinate_confidence"],
            ),
        )

    connection.commit()

    count = connection.execute(
        "SELECT COUNT(*) FROM hospitals"
    ).fetchone()[0]

    connection.close()

    print(f"Loaded {count} routable facilities into SQLite.")


if __name__ == "__main__":
    load_hospitals()