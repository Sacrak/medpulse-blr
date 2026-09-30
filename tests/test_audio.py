from app.audio import AudioTranscriber
from app.triage import TriageEngine


audio_path = "Recording.mp4"


# -----------------------------------------
# Load models
# -----------------------------------------

print("\nLoading audio transcriber...")

transcriber = AudioTranscriber(
    model_size="medium"
)

print("Audio transcriber ready.")


print("\nLoading triage engine...")

triage = TriageEngine()

print("Triage engine ready.")


# -----------------------------------------
# Audio → Text
# -----------------------------------------

result = transcriber.transcribe(audio_path)

text = result["text"]


print("\n" + "=" * 60)
print("WHISPER RESULT")
print("=" * 60)

print("Text:", text)
print("Language:", result["language"])
print(
    "Language probability:",
    result["language_probability"]
)

print(
    "ASR reliable:",
    result.get("asr_reliable")
)

print(
    "ASR quality score:",
    result.get("asr_quality_score")
)

print(
    "ASR quality reason:",
    result.get("asr_quality_reason")
)


# -----------------------------------------
# Text → Triage
# -----------------------------------------

triage_result = triage.predict(text)


print("\n" + "=" * 60)
print("TRIAGE RESULT")
print("=" * 60)

print("Categories:")

if triage_result["categories"]:
    for category in triage_result["categories"]:
        print(" -", category)
else:
    print(" - None")


print("\nSeverity:")
print(" -", triage_result["severity"])


print("\nScores:")

for category, score in sorted(
    triage_result["scores"].items(),
    key=lambda x: x[1],
    reverse=True,
):
    print(f"{category:<32} {score:.4f}")


# -----------------------------------------
# Final summary
# -----------------------------------------

print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)

print("Transcription:", text)
print("Language:", result["language"])
print("ASR reliable:", result.get("asr_reliable"))
print("ASR quality:", result.get("asr_quality_score"))
print("Categories:", triage_result["categories"])
print("Severity:", triage_result["severity"])