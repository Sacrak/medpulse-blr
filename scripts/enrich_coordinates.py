"""MedPulse Bengaluru - conservative coordinate enrichment."""
from __future__ import annotations
import argparse, csv, json, re, time, xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
CSV_FILES = [RAW / "bbmp_hospital_list.csv", RAW / "bbmp_maternity_hospitals.csv", RAW / "bbmp_referral_hospitals.csv"]
KML_FILE = RAW / "referral_hospitals.kml"
OUTPUT_FILE = PROCESSED / "bangalore_hospitals_enriched.csv"
CACHE_FILE = PROCESSED / "geocode_cache.json"
USER_AGENT = "MedPulseBengaluru/1.0 (educational project)"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def normalize_name(value: str) -> str:
    value = str(value or "").lower().strip()
    for old, new in {"&":" and ", ".":" ", ",":" ", "-":" ", "/":" "}.items(): value = value.replace(old, new)
    value = re.sub(r"\b(referral|referal|reffrel)\b", " ", value)
    value = re.sub(r"\bhospital\b", " ", value)
    value = re.sub(r"\bmaternity\s+home\b", " maternity ", value)
    value = re.sub(r"\bh\s*c\b", " health centre ", value)
    value = re.sub(r"\bhealth\s+centre\b", " health centre ", value)
    value = re.sub(r"\bu\s*f\s*w\s*c\b", " urban family welfare centre ", value)
    return re.sub(r"\s+", " ", value).strip()

def read_repaired_csv(path: Path) -> pd.DataFrame:
    with path.open("r", encoding="utf-8-sig", newline="") as f: rows = list(csv.reader(f))
    header = rows[0][:9]
    records = [r[:9] for r in rows[1:] if len(r) >= 9]
    df = pd.DataFrame(records, columns=header)
    df["source_file"] = path.name
    return df

def load_bbmp_data() -> pd.DataFrame:
    df = pd.concat([read_repaired_csv(p) for p in CSV_FILES], ignore_index=True)
    for col in df.columns:
        if df[col].dtype == "object": df[col] = df[col].fillna("").astype(str).str.strip()
    df["normalized_name"] = df["Name"].map(normalize_name)
    return df.drop_duplicates(subset=["normalized_name", "Address"], keep="first").reset_index(drop=True)

def parse_kml(path: Path) -> pd.DataFrame:
    ns = {"kml":"http://www.opengis.net/kml/2.2"}
    root = ET.parse(path).getroot(); rows=[]
    for p in root.findall(".//kml:Placemark", ns):
        n=p.find(".//kml:SimpleData[@name='UCHC_HospitalName']",ns)
        c=p.find(".//kml:Point/kml:coordinates",ns)
        if n is None or c is None: continue
        try: lon,lat,*_=map(float,(c.text or "").strip().split(","))
        except ValueError: continue
        rows.append({"kml_name":(n.text or "").strip(),"latitude":lat,"longitude":lon})
    result=pd.DataFrame(rows)
    if not result.empty: result["normalized_kml_name"]=result["kml_name"].map(normalize_name)
    return result

EXPLICIT_ALIASES = {
    "govindrajnagar hc": "govindarajnagar",
    "h siddaiah road hospital": "h siddaiah road",
    "sirsi road maternity home": "sirsi road maternity and",
    "srirampuram referral hospital": "srirampura",
    "banashankari referral hospital": "banashankari",
}

def match_kml(df: pd.DataFrame, kml: pd.DataFrame) -> pd.DataFrame:
    if "latitude" not in df.columns: df["latitude"]=pd.NA
    if "longitude" not in df.columns: df["longitude"]=pd.NA
    if "coordinate_source" not in df.columns: df["coordinate_source"]=""
    if "coordinate_confidence" not in df.columns: df["coordinate_confidence"]=""
    if kml.empty: return df
    by_name={r["normalized_kml_name"]:r for _,r in kml.iterrows()}
    aliases={normalize_name(k):normalize_name(v) for k,v in EXPLICIT_ALIASES.items()}
    for idx,row in df.iterrows():
        candidates=[row["normalized_name"]]
        if row["normalized_name"] in aliases: candidates.append(aliases[row["normalized_name"]])
        for candidate in candidates:
            if candidate in by_name:
                m=by_name[candidate]
                df.at[idx,"latitude"]=m["latitude"]; df.at[idx,"longitude"]=m["longitude"]
                df.at[idx,"coordinate_source"]="BBMP_KML"; df.at[idx,"coordinate_confidence"]="verified"
                break
    return df

def load_cache():
    if not CACHE_FILE.exists(): return {}
    try: return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError,OSError): return {}

def save_cache(cache): CACHE_FILE.write_text(json.dumps(cache,indent=2,ensure_ascii=False),encoding="utf-8")

def geocode_one(query: str, session: requests.Session) -> Optional[dict]:
    r=session.get(NOMINATIM_URL,params={"q":query,"format":"jsonv2","limit":1,"countrycodes":"in"},headers={"User-Agent":USER_AGENT},timeout=15)
    r.raise_for_status(); results=r.json()
    if not results: return None
    x=results[0]
    return {"latitude":float(x["lat"]),"longitude":float(x["lon"]),"display_name":x.get("display_name",""),"osm_type":x.get("osm_type",""),"osm_id":x.get("osm_id","")}

def enrich_with_nominatim(df: pd.DataFrame, enable=False) -> pd.DataFrame:
    if not enable: return df
    cache=load_cache(); session=requests.Session()
    for idx,row in df.iterrows():
        if pd.notna(row.get("latitude")) and pd.notna(row.get("longitude")): continue
        parts=[str(row["Name"]).strip(),str(row.get("Address","")).strip(),"Bengaluru, Karnataka, India"]
        query=", ".join(p for p in parts if p)
        if query in cache: result=cache[query]
        else:
            try: result=geocode_one(query,session)
            except requests.RequestException as exc: print(f"[WARN] {row['Name']}: {exc}"); result=None
            cache[query]=result; save_cache(cache); time.sleep(1.05)
        if result:
            df.at[idx,"latitude"]=result["latitude"]; df.at[idx,"longitude"]=result["longitude"]
            df.at[idx,"coordinate_source"]="NOMINATIM_OSM"; df.at[idx,"coordinate_confidence"]="geocoded"; df.at[idx,"geocoded_query"]=query
    return df

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--geocode",action="store_true"); args=parser.parse_args()
    PROCESSED.mkdir(parents=True,exist_ok=True)
    df=load_bbmp_data(); print(f"Loaded BBMP facilities: {len(df)}")
    if KML_FILE.exists():
        kml=parse_kml(KML_FILE); print(f"Loaded KML coordinates: {len(kml)}"); df=match_kml(df,kml)
    else: print("[WARN] KML not found")
    df=enrich_with_nominatim(df,args.geocode)
    for col in ["coordinate_source","coordinate_confidence","geocoded_query"]:
        if col not in df.columns: df[col]=""
    df["is_routable"]=df["latitude"].notna() & df["longitude"].notna()
    df.to_csv(OUTPUT_FILE,index=False)
    print("\n"+"="*50); print("MEDPULSE COORDINATE ENRICHMENT"); print("="*50)
    print(f"Facilities:                 {len(df)}")
    print(f"Coordinates available:      {int(df['is_routable'].sum())}")
    print(f"Still unresolved:           {int((~df['is_routable']).sum())}")
    print("\nCoordinate sources:"); print(df.loc[df["is_routable"],"coordinate_source"].value_counts())
    print(f"\nOutput: {OUTPUT_FILE}")

if __name__ == "__main__": main()
