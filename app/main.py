from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
)

from fastapi.responses import HTMLResponse

from pydantic import BaseModel

import os
import shutil
import tempfile

from app.triage import TriageEngine
from app.emergency_router import route_emergency
from app.audio import AudioTranscriber


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="MedPulse Bengaluru",
    description="AI-assisted emergency triage and hospital routing system",
    version="1.0.0",
)


# ============================================================
# LOAD MODELS
# ============================================================

print("\nLoading MedPulse models...")

triage_engine = TriageEngine()

audio_transcriber = AudioTranscriber(
    model_size="medium"
)

print("MedPulse models ready.")


# ============================================================
# REQUEST MODEL
# ============================================================

class TriageRequest(BaseModel):

    text: str

    latitude: float

    longitude: float


# ============================================================
# RESPONSE FORMATTER
# ============================================================

def format_hospital(hospital):

    return {

        "rank": hospital["ranking"],

        "name": hospital["name"],

        "facility": hospital["hospital_type"],

        "address": hospital["address"],

        "latitude": hospital["latitude"],

        "longitude": hospital["longitude"],

        "available_beds": hospital["available_beds"],

        "total_beds": hospital["total_beds"],

        "driving_distance_km": round(
            hospital["driving_distance_km"],
            2,
        ),

        "eta_minutes": round(
            hospital["duration_minutes"],
            1,
        ),

        "ranking_basis": hospital[
            "ranking_basis"
        ],
    }


def format_hospitals(hospitals):

    return [
        format_hospital(hospital)
        for hospital in hospitals
    ]


# ============================================================
# FRONTEND
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse,
)
def frontend():

    template_path = os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
        "templates",
        "index.html",
    )

    if not os.path.exists(template_path):

        raise HTTPException(
            status_code=500,
            detail="Frontend template not found.",
        )

    with open(
        template_path,
        "r",
        encoding="utf-8",
    ) as file:

        return file.read()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# TEXT TRIAGE
# ============================================================

@app.post("/triage")
def triage_emergency(
    request: TriageRequest,
):

    result = triage_engine.predict(
        request.text
    )

    categories = result[
        "categories"
    ]

    severity = result[
        "severity"
    ]

    routing = route_emergency(
        categories=categories,
        severity=severity,
        latitude=request.latitude,
        longitude=request.longitude,
    )

    return {

        "text": result["text"],

        "categories": categories,

        "severity": severity,

        "required_facility":
            routing[
                "required_facility"
            ],

        "hospitals":
            format_hospitals(
                routing["candidates"]
            ),
    }


# ============================================================
# AUDIO TRIAGE
# ============================================================

@app.post("/triage/audio")
async def triage_audio(
    latitude: float,
    longitude: float,
    file: UploadFile = File(...),
):

    # --------------------------------------------------------
    # Validate uploaded file
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No audio file provided",
        )


    allowed_extensions = {

        ".wav",
        ".mp3",
        ".m4a",
        ".ogg",
        ".flac",
        ".webm",

    }


    extension = os.path.splitext(
        file.filename
    )[1].lower()


    if extension not in allowed_extensions:

        raise HTTPException(

            status_code=400,

            detail=(
                "Unsupported audio format. "
                "Supported formats: "
                ".wav, .mp3, .m4a, .ogg, "
                ".flac, .webm"
            ),

        )


    temp_path = None


    try:

        # ----------------------------------------------------
        # Save uploaded audio temporarily
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(

            delete=False,

            suffix=extension,

        ) as temp_file:

            temp_path = temp_file.name

            shutil.copyfileobj(
                file.file,
                temp_file,
            )


        # ----------------------------------------------------
        # Whisper transcription
        # ----------------------------------------------------

        audio_result = (
            audio_transcriber.transcribe(
                temp_path
            )
        )


        text = audio_result[
            "text"
        ]


        if not text.strip():

            raise HTTPException(

                status_code=400,

                detail=(
                    "Could not extract speech "
                    "from audio"
                ),

            )


        # ----------------------------------------------------
        # NLP triage
        # ----------------------------------------------------

        triage_result = (
            triage_engine.predict(
                text
            )
        )


        categories = (
            triage_result[
                "categories"
            ]
        )


        severity = (
            triage_result[
                "severity"
            ]
        )


        # ----------------------------------------------------
        # Emergency routing
        # ----------------------------------------------------

        routing = route_emergency(

            categories=categories,

            severity=severity,

            latitude=latitude,

            longitude=longitude,

        )


        # ----------------------------------------------------
        # Final response
        # ----------------------------------------------------

        return {

            "filename":
                file.filename,

            "transcription":
                text,

            "language":
                audio_result[
                    "language"
                ],

            "language_probability":
                round(
                    audio_result[
                        "language_probability"
                    ],
                    4,
                ),

            "asr_reliable":
                audio_result.get(
                    "asr_reliable"
                ),

            "asr_quality_score":
                audio_result.get(
                    "asr_quality_score"
                ),

            "asr_quality_reason":
                audio_result.get(
                    "asr_quality_reason"
                ),

            "categories":
                categories,

            "severity":
                severity,

            "required_facility":
                routing[
                    "required_facility"
                ],

            "hospitals":
                format_hospitals(
                    routing[
                        "candidates"
                    ]
                ),
        }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                f"Audio triage failed: {str(e)}"
            ),

        )


    finally:

        # ----------------------------------------------------
        # Delete temporary audio
        # ----------------------------------------------------

        if (
            temp_path
            and os.path.exists(temp_path)
        ):

            os.remove(
                temp_path
            )