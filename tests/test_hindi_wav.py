import os
import wave

import av
from faster_whisper import WhisperModel


AUDIO_FILE = "Recording.m4a"
WAV_FILE = "Recording_clean.wav"


def convert_to_wav():
    print("=" * 60)
    print("CONVERTING M4A → 16 kHz MONO WAV")
    print("=" * 60)

    input_container = av.open(AUDIO_FILE)

    audio_stream = input_container.streams.audio[0]

    resampler = av.AudioResampler(
        format="s16",
        layout="mono",
        rate=16000,
    )

    frames = []

    for frame in input_container.decode(audio_stream):
        converted_frames = resampler.resample(frame)

        if not isinstance(converted_frames, list):
            converted_frames = [converted_frames]

        frames.extend(converted_frames)

    input_container.close()

    with wave.open(WAV_FILE, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit audio
        wav.setframerate(16000)

        for frame in frames:
            wav.writeframes(frame.to_ndarray().tobytes())

    print(f"Created: {WAV_FILE}")


def transcribe(audio_file):
    print("\n" + "=" * 60)
    print(f"TRANSCRIBING: {audio_file}")
    print("=" * 60)

    model = WhisperModel(
        "medium",
        device="cpu",
        compute_type="int8",
    )

    segments, info = model.transcribe(
        audio_file,
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

    print(f"Language: {info.language}")
    print(f"Language probability: {info.language_probability}")
    print(f"Transcription:\n{text}")

    return text


if __name__ == "__main__":
    if not os.path.exists(AUDIO_FILE):
        raise FileNotFoundError(
            f"Could not find {AUDIO_FILE} in the project root."
        )

    convert_to_wav()

    print("\nRunning Whisper on cleaned WAV...")
    transcribe(WAV_FILE)

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)