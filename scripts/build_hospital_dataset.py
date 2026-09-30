from pathlib import Path
import pandas as pd
import requests

import xml.etree.ElementTree as ET
import re
# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_FILE = PROCESSED_DIR / "bangalore_hospitals_enriched.csv"


# --------------------------------------------------
# Load raw BBMP datasets
# --------------------------------------------------

def load_raw_datasets():
    files = [
        RAW_DIR / "bbmp_hospital_list.csv",
        RAW_DIR / "bbmp_maternity_hospitals.csv",
        RAW_DIR / "bbmp_referral_hospitals.csv",
    ]

    expected_columns = [
        "Name",
        "Type",
        "Beds",
        "Address",
        "Ward",
        "area covered",
        "Services",
        "Staff",
        "Contact",
    ]

    dataframes = []

    for file in files:
        print(f"Loading: {file.name}")

        try:
            df = pd.read_csv(file)

        except pd.errors.ParserError:
            print("  Inconsistent row lengths detected.")
            print("  Using Python CSV parser.")

            df = pd.read_csv(
                file,
                engine="python",
                header=0,
                names=expected_columns,
                usecols=range(len(expected_columns)),
            )

        # Make sure the column order is consistent
        df = df.iloc[:, :len(expected_columns)]
        df.columns = expected_columns

        df["source_file"] = file.name

        dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True)



# --------------------------------------------------
# Normalize hospital names
# --------------------------------------------------
def normalize_name(name):
    if pd.isna(name):
        return ""

    name = str(name).lower()

    replacements = {
        ".": "",
        ",": "",
        "-": " ",
        "/": " ",
        "&": " and ",
        "referal": "referral",
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    # Remove repeated whitespace
    name = " ".join(name.split())

    return name


# --------------------------------------------------
# Load coordinates from BBMP KML
# --------------------------------------------------

def load_kml_coordinates():
    kml_file = RAW_DIR / "referral_hospitals.kml"

    tree = ET.parse(kml_file)
    root = tree.getroot()

    namespace = {
        "kml": "http://www.opengis.net/kml/2.2"
    }

    coordinates = []

    for placemark in root.findall(".//kml:Placemark", namespace):

        # Hospital name is stored inside ExtendedData/SimpleData
        name_element = placemark.find(
            ".//kml:SimpleData[@name='UCHC_HospitalName']",
            namespace
        )

        # Coordinates are stored inside Point/coordinates
        coordinate_element = placemark.find(
            ".//kml:Point/kml:coordinates",
            namespace
        )

        if name_element is None or coordinate_element is None:
            continue

        name = name_element.text.strip()
        raw_coordinates = coordinate_element.text.strip()

        # KML format:
        # longitude,latitude,altitude
        parts = raw_coordinates.split(",")

        if len(parts) < 2:
            continue

        longitude = float(parts[0])
        latitude = float(parts[1])

        coordinates.append({
            "name": name,
            "normalized_name": normalize_name(name),
            "latitude": latitude,
            "longitude": longitude,
        })

    print(f"KML coordinate records: {len(coordinates)}")

    return coordinates


# --------------------------------------------------
# Apply controlled KML matches
# --------------------------------------------------

def apply_kml_coordinates(df):

    kml_records = load_kml_coordinates()

    # Explicit, verified mappings.
    # These are intentionally NOT fuzzy matches.
    verified_matches = {
        "banashankari referral hospital":
            "banashankari referral hospital",

        "h siddaiah road hospital":
            "h siddaiah road referral hospital",

        "sirsi road maternity home":
            "sirsi road maternity home and referral hospital",

        "srirampuram referral hospital":
            "srirampura referral hospital",

        "govindrajnagar hc":
            "govindarajnagar referral hospital",
    }

    kml_lookup = {
        record["normalized_name"]: record
        for record in kml_records
    }

    matched = 0

    for index, row in df.iterrows():

        hospital_name = row["normalized_name"]

        # Direct match
        kml_record = kml_lookup.get(hospital_name)

        # Controlled alias match
        if kml_record is None:
            target = verified_matches.get(hospital_name)

            if target:
                kml_record = kml_lookup.get(target)

        if kml_record is None:
            continue

        df.at[index, "latitude"] = kml_record["latitude"]
        df.at[index, "longitude"] = kml_record["longitude"]

        df.at[index, "coordinate_source"] = "BBMP_KML"
        df.at[index, "coordinate_confidence"] = "high"
        df.at[index, "geocoded_query"] = kml_record["name"]
        df.at[index, "is_routable"] = True

        matched += 1

    # --------------------------------------------------
    # Add verified referral facilities that are present
    # in the KML but absent from the original BBMP CSV.
    # --------------------------------------------------

    existing_names = set(df["normalized_name"])

    additional_facilities = {
        "halsuru reffrel hospital",
        "uchc kengeri",
    }

    added = 0

    for record in kml_records:

        if record["normalized_name"] not in additional_facilities:
            continue

        if record["normalized_name"] in existing_names:
            continue

        new_record = {
            column: pd.NA
            for column in df.columns
        }

        new_record["Name"] = record["name"]
        new_record["Type"] = "BBMP Referral/UCHC Facility"
        new_record["source_file"] = "referral_hospitals.kml"
        new_record["normalized_name"] = record["normalized_name"]

        new_record["latitude"] = record["latitude"]
        new_record["longitude"] = record["longitude"]

        new_record["coordinate_source"] = "BBMP_KML"
        new_record["coordinate_confidence"] = "high"
        new_record["geocoded_query"] = record["name"]
        new_record["is_routable"] = True

        df = pd.concat(
            [df, pd.DataFrame([new_record])],
            ignore_index=True
        )

        existing_names.add(record["normalized_name"])
        added += 1

    print(f"KML hospitals matched: {matched}")
    print(f"Additional KML referral facilities added: {added}")

    return df

# --------------------------------------------------
# Apply exact UPHC KML matches
# --------------------------------------------------

def load_uphc_coordinates():
    kml_file = RAW_DIR / "uphc_hospitals.kml"

    tree = ET.parse(kml_file)
    root = tree.getroot()

    namespace = {
        "kml": "http://www.opengis.net/kml/2.2"
    }

    coordinates = []

    for placemark in root.findall(".//kml:Placemark", namespace):

        data = {
            element.attrib["name"]: (element.text or "").strip()
            for element in placemark.findall(
                ".//kml:SimpleData",
                namespace
            )
        }

        name = data.get("UPHC")

        coordinate_element = placemark.find(
            ".//kml:Point/kml:coordinates",
            namespace
        )

        if not name or coordinate_element is None:
            continue

        raw_coordinates = coordinate_element.text.strip()
        parts = raw_coordinates.split(",")

        if len(parts) < 2:
            continue

        longitude = float(parts[0])
        latitude = float(parts[1])

        coordinates.append({
            "name": name,
            "normalized_name": normalize_name(name),
            "latitude": latitude,
            "longitude": longitude,
        })

    print(f"UPHC coordinate records: {len(coordinates)}")

    return coordinates


def apply_uphc_coordinates(df):

    uphc_records = load_uphc_coordinates()

    # Exact normalized-name matches verified manually.
    # No fuzzy matching is performed here.
    verified_matches = {
        # Exact normalized matches
        "a d halli hc": "a d halli uphc",
        "anjanappa garden hc": "anjanappa garden uphc",
        "avalahalli hc": "avalahalli uphc",
        "bhuvaneshwari nagar hc": "uphc bhuvaneshwari nagar",
        "gangondanahalli hc": "gangondanahalli uphc",
        "k g halli hc": "kghalli uphc",
        "kodihalli hc": "uphc kodihalli",
        "koramangala hc": "koramangala uphc",
        "murphy town hc": "uphc murphy town",
        "old byappanahalli hc": "uphc old byappanahalli",
        "sulthan palya hc": "uphc sulthan palya",
        "vidyapeeta hc": "vidyapeeta uphc",
        "banashankari ufwc": "banashankari ufwc",

    # Manually verified aliases
        "audugodi hc": "adugodi uphc",
        "bapujinagar hc": "bapujinagar uhpc",
        "kumaraswami layout h c": "kumaraswamylayout uphc",
        "mathikere hc": "matthikere uphc",
        "moodalapalya hc": "moodalpalya uphc",
        "pantharpalya hc": "pantharapalya uphc",
        "shankar nagar h c": "shankarnagar uphc",
        "taskar town hc": "tasker town uphc",
        "thavarekere h c": "thavarekere uphc",
        "yarabnagar h c": "yarab nagar uphc",

        "r c pura ufwc": "rc pura uphc",
        "shanthinagar ufwc": "uphc shanthinagara",
        "jayanagar ufwc": "jayanagara uphc",
        "yeshwanthpura ufwc": "yashavanthpur uphc",
        "magadi road ufwc": "magadi road uphc",
        "manvarthpet ufwc": "manvarthpete uphc",
    }

    uphc_lookup = {
        record["normalized_name"]: record
        for record in uphc_records
    }

    matched = 0

    for index, row in df.iterrows():

        # Do not overwrite coordinates obtained
        # from the higher-priority referral KML.
        if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):
            continue

        hospital_name = row["normalized_name"]

        target = verified_matches.get(hospital_name)

        if target is None:
            continue

        uphc_record = uphc_lookup.get(target)

        if uphc_record is None:
            continue

        df.at[index, "latitude"] = uphc_record["latitude"]
        df.at[index, "longitude"] = uphc_record["longitude"]

        df.at[index, "coordinate_source"] = "BBMP_UPHC_KML"
        df.at[index, "coordinate_confidence"] = "high"
        df.at[index, "geocoded_query"] = uphc_record["name"]
        df.at[index, "is_routable"] = True

        matched += 1

    print(f"UPHC hospitals matched: {matched}")

    return df
# --------------------------------------------------
# Prepare hospital dataset
# --------------------------------------------------

def prepare_dataset(df):

    # Normalize hospital names
    df["normalized_name"] = df["Name"].apply(normalize_name)

    # Remove exact duplicate records
    df = df.drop_duplicates(
        subset=["normalized_name", "Address"]
    ).copy()

    # Add coordinate fields
    df["latitude"] = pd.NA
    df["longitude"] = pd.NA

    df["coordinate_source"] = pd.NA
    df["coordinate_confidence"] = pd.NA
    df["geocoded_query"] = pd.NA

    # Initially nobody is routable
    df["is_routable"] = False

    return df

# --------------------------------------------------
# Test Nominatim geocoding
# --------------------------------------------------

def geocode_with_nominatim(name, address):
    query = f"{name}, {address}, Bengaluru, Karnataka, India"

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query,
        "format": "json",
        "limit": 1,
    }

    headers = {
        "User-Agent": "MedPulse-Bengaluru/1.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=10,
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        return None

    result = results[0]

    return {
        "query": query,
        "latitude": float(result["lat"]),
        "longitude": float(result["lon"]),
        "display_name": result["display_name"],
    }
# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    

    print("Loading raw hospital datasets...\n")

    df = load_raw_datasets()

    print(f"\nRaw records: {len(df)}")
    df = prepare_dataset(df)

    print(f"Records after deduplication: {len(df)}")

    df = apply_kml_coordinates(df)

    print(
        f"Routable hospitals after Referral KML: "
        f"{df['is_routable'].sum()}"
    )

    df = apply_uphc_coordinates(df)

    print(
        f"Routable hospitals after UPHC KML: "
        f"{df['is_routable'].sum()}"
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved processed dataset:")
    print(OUTPUT_FILE)



    
if __name__ == "__main__":
    main()