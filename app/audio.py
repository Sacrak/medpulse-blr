from faster_whisper import WhisperModel


class AudioTranscriber:
    def __init__(self, model_size="medium"):
        print(f"Loading Whisper model: {model_size}")

        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
        )

        print("Whisper model ready.")

    def _calculate_quality(self, text, segments, language_probability):
        """
        Estimate whether the ASR output looks reliable enough
        to pass downstream to the NLP triage system.

        This is an engineering quality check, NOT a medical
        confidence score.
        """

        text = text.strip()

        if not text:
            return {
                "reliable": False,
                "score": 0.0,
                "reason": "Empty transcription",
            }

        words = text.split()

        if len(words) < 2:
            return {
                "reliable": False,
                "score": 0.2,
                "reason": "Transcription is too short",
            }

        # --------------------------------------------------
        # 1. Language confidence
        # --------------------------------------------------

        language_score = min(
            max(float(language_probability), 0.0),
            1.0,
        )

        # --------------------------------------------------
        # 2. Repetition detection
        # --------------------------------------------------

        normalized_words = [
            word.strip(".,!?;:()[]{}\"'")
            for word in words
        ]

        normalized_words = [
            word for word in normalized_words
            if word
        ]

        if normalized_words:
            unique_ratio = (
                len(set(normalized_words))
                / len(normalized_words)
            )
        else:
            unique_ratio = 0.0

        # Strong indication of hallucinated/repeated text.
        if len(normalized_words) >= 6 and unique_ratio < 0.4:
            return {
                "reliable": False,
                "score": 0.25,
                "reason": "Excessive word repetition",
            }

        # --------------------------------------------------
        # 3. Segment-level quality
        # --------------------------------------------------

        segment_count = len(segments)

        if segment_count == 0:
            return {
                "reliable": False,
                "score": 0.1,
                "reason": "No speech segments detected",
            }

        # --------------------------------------------------
        # 4. Combined engineering score
        # --------------------------------------------------

        score = (
            0.65 * language_score
            + 0.25 * unique_ratio
            + 0.10 * min(segment_count / 3.0, 1.0)
        )

        score = round(score, 3)

        # We intentionally use a conservative threshold.
        reliable = score >= 0.60

        if reliable:
            reason = "ASR output passed quality checks"
        else:
            reason = "ASR confidence/quality is low"

        return {
            "reliable": reliable,
            "score": score,
            "reason": reason,
        }

    def transcribe(self, audio_path):
        hotwords = (
            "emergency, ambulance, accident, injury, "
            "bleeding, blood, wound, fracture, broken bone, "
            "chest pain, heart attack, breathing, "
            "cannot breathe, unconscious, seizure, "
            "poisoning, overdose, burn, fever, infection, "
            "pregnancy, pregnant, delivery, pain, "
            "leg, arm, head, stomach, abdomen, "
            "घायल, खून, खून बह रहा, दुर्घटना, "
            "सांस, सांस नहीं आ रही, दर्द, "
            "दिल का दौरा, बेहोश, जहर, जल गया"
        )

        segments, info = self.model.transcribe(
            audio_path,
            language=None,
            task="transcribe",
            beam_size=8,
            best_of=8,
            patience=1.0,

            # Prevent repeated/hallucinated text from being
            # carried between segments.
            condition_on_previous_text=False,

            vad_filter=True,
            vad_parameters={
                "min_silence_duration_ms": 500
            },

            hotwords=hotwords,
            without_timestamps=True,

            temperature=[
                0.0,
                0.2,
                0.4,
            ],
        )

        segments = list(segments)

        text = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()

        quality = self._calculate_quality(
            text=text,
            segments=segments,
            language_probability=info.language_probability,
        )

        return {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability,

            # ASR quality information
            "asr_reliable": quality["reliable"],
            "asr_quality_score": quality["score"],
            "asr_quality_reason": quality["reason"],
        }