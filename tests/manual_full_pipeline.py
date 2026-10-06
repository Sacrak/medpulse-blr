from app.audio import AudioTranscriber
from app.triage import TriageEngine
from app.emergency_router import route_emergency


PATIENT_LAT = 12.9716
PATIENT_LON = 77.5946
AUDIO_FILE = "Recording.m4a"


print("=" * 60)
print("MEDPULSE FULL EMERGENCY PIPELINE")
print("=" * 60)


# ============================================================
# 1. AUDIO TRANSCRIPTION
# ============================================================

print("\n[1] Transcribing audio...")

transcriber = AudioTranscriber(model_size="medium")

audio_result = transcriber.transcribe(AUDIO_FILE)

text = audio_result["text"]

print("Transcribed text:", text)
print("Language:", audio_result["language"])
print(
    "Language probability:",
    round(audio_result["language_probability"], 4)
)


# ============================================================
# 2. NLP TRIAGE
# ============================================================

print("\n[2] Running NLP triage...")

triage = TriageEngine()

triage_result = triage.predict(text)

categories = triage_result["categories"]
scores = triage_result["scores"]
severity = triage_result["severity"]

print("Categories:", categories)
print("Severity:", severity)

print("\nTop detected categories:")

for category, score in sorted(
    scores.items(),
    key=lambda x: x[1],
    reverse=True
)[:5]:

    print(
        f"{category:<32} {score:.4f}"
    )


# ============================================================
# 3. HOSPITAL ROUTING
# ============================================================

print("\n[3] Finding suitable hospitals...")

routing_result = route_emergency(
    categories=categories,
    severity=severity,
    latitude=PATIENT_LAT,
    longitude=PATIENT_LON,
)

print(
    "Required facility:",
    routing_result["required_facility"]
)


# ============================================================
# 4. RANKED HOSPITALS
# ============================================================

print("\n[4] Ranked hospitals")

hospitals = routing_result["candidates"]

if not hospitals:

    print("No suitable hospitals found.")

else:

    for hospital in hospitals:

        print(
            f"\n#{hospital['ranking']} "
            f"{hospital['name']}"
        )

        print(
            "Type:",
            hospital["hospital_type"]
        )

        print(
            "Beds:",
            f"{hospital['available_beds']}/"
            f"{hospital['total_beds']}"
        )

        print(
            "Driving distance:",
            f"{hospital['driving_distance_km']:.2f} km"
        )

        print(
            "ETA:",
            f"{hospital['duration_minutes']:.1f} minutes"
        )

        print(
            "Ranking basis:",
            hospital["ranking_basis"]
        )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("PIPELINE COMPLETE")
print("=" * 60)