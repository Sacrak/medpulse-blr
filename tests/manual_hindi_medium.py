from faster_whisper import WhisperModel


AUDIO_FILE = "Recording.m4a"


print("=" * 60)
print("LOADING WHISPER MEDIUM")
print("=" * 60)

model = WhisperModel(
    "medium",
    device="cpu",
    compute_type="int8",
)

print("Model loaded.")


segments, info = model.transcribe(
    AUDIO_FILE,
    language="hi",
    task="transcribe",
    beam_size=8,
    best_of=8,
    patience=1.0,
    condition_on_previous_text=False,
    vad_filter=True,
    vad_parameters={
        "min_silence_duration_ms": 500
    },
    without_timestamps=True,
    temperature=[0.0, 0.2, 0.4],
)

segments = list(segments)

text = " ".join(
    segment.text.strip()
    for segment in segments
    if segment.text.strip()
)

print("\n" + "=" * 60)
print("MEDIUM MODEL RESULT")
print("=" * 60)

print(f"Language: {info.language}")
print(f"Language probability: {info.language_probability}")
print(f"Transcription:\n{text}")