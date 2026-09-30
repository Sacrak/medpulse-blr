import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "bangalore_hospitals_enriched.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "coordinate_audit.csv"
)


def create_audit_file():
    df = pd.read_csv(INPUT_FILE)

    routable = df[df["is_routable"] == True].copy()

    audit = routable[
        [
            "Name",
            "Type",
            "Address",
            "latitude",
            "longitude",
            "coordinate_source",
            "coordinate_confidence",
        ]
    ].copy()

    audit["independent_latitude"] = pd.NA
    audit["independent_longitude"] = pd.NA
    audit["independent_source"] = pd.NA
    audit["coordinate_difference_km"] = pd.NA
    audit["verification_status"] = "pending"

    audit.to_csv(OUTPUT_FILE, index=False)

    print(f"Created coordinate audit for {len(audit)} facilities.")
    print(f"Saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    create_audit_file()
    