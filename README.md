<div align="center">

# MedPulse Bengaluru

### Real-Time Voice-Based Emergency Triage & Hospital Routing System

An AI-assisted emergency routing platform that transforms emergency text or voice input into structured triage information and identifies suitable hospitals using facility capability, bed availability, and real-world driving ETA.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![PyTorch](https://img.shields.io/badge/PyTorch-ML-EE4C2C?logo=pytorch)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikit-learn)
![Google Routes](https://img.shields.io/badge/Google-Routes%20API-4285F4?logo=googlemaps)
![Pytest](https://img.shields.io/badge/Testing-Pytest-0A9EDC?logo=pytest)

</div>

---

## Overview

MedPulse Bengaluru is an AI-assisted emergency routing system designed to help users identify appropriate hospital options during an emergency.

The system accepts either **text or voice input**, extracts emergency categories using a multilabel NLP pipeline, estimates severity, determines the required hospital facility level, filters suitable hospitals, calculates real-world driving routes, and ranks the resulting hospitals.

> **Important:** MedPulse is an academic and software-engineering prototype. It is not a medical diagnosis system and does not replace professional medical judgment.

---

## Key Capabilities

| Capability | Implementation |
|---|---|
| Voice Input | Faster-Whisper |
| Emergency Classification | Sentence Transformers + Logistic Regression |
| Multilabel Detection | 15 emergency categories |
| Severity Estimation | Rule-based severity engine |
| Hospital Filtering | Facility capability + bed availability |
| Route Calculation | Google Routes API |
| Hospital Ranking | ETA-first + bed availability tiebreaker |
| User Location | Browser Geolocation API |
| Backend | FastAPI |
| Database | SQLite |
| Testing | Pytest |

---

## System Architecture

```text
                         +----------------+
                         |      User      |
                         +-------+--------+
                                 |
                    +------------+------------+
                    |                         |
              Text Input                 Voice Input
                    |                         |
                    |                  Faster-Whisper
                    |                         |
                    +------------+------------+
                                 |
                                 v
                     +-----------------------+
                     |    NLP Classification |
                     | Sentence Transformer  |
                     | + Logistic Regression  |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Emergency Categories  |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Severity Estimation   |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Required Facility     |
                     | Level Determination   |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Hospital Filtering    |
                     | - Facility Capability |
                     | - Bed Availability    |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     |   Google Routes API   |
                     | - Driving Distance    |
                     | - Estimated ETA       |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     |   Hospital Ranking    |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     |    Final Results      |
                     +-----------------------+
```

---

## Features

- Voice-based emergency input using speech recognition
- Multilabel NLP classification of emergency categories
- Emergency severity estimation
- Hospital facility-capability filtering
- Bed-availability filtering
- Real-world driving distance and ETA using Google Routes API
- ETA-first hospital ranking with bed availability as a tiebreaker
- Browser-based user location for routing
- Automated tests and NLP benchmark evaluation

---

## NLP Pipeline

MedPulse uses a multilabel NLP pipeline to identify emergency-related categories from user input.

### Supported Emergency Categories

The system currently supports 15 emergency categories:

- `ABDOMINAL`
- `ALLERGIC_REACTION`
- `ANIMAL_INSECT_BITE`
- `BLEEDING`
- `BURNS`
- `CARDIAC`
- `FEVER_INFECTION`
- `FRACTURE_MUSCULOSKELETAL`
- `NEUROLOGICAL`
- `OBSTETRIC`
- `PEDIATRIC`
- `POISONING`
- `RESPIRATORY`
- `SEIZURE`
- `TRAUMA`

### Model Pipeline

```text
Emergency Text
      |
      v
Sentence Transformer
(paraphrase-multilingual-MiniLM-L12-v2)
      |
      v
Text Embeddings
      |
      v
One-vs-Rest Logistic Regression
      |
      v
Multilabel Emergency Categories
```

The classifier is designed to support multiple categories for a single emergency description when the input provides evidence for more than one category.

---

## Emergency Routing Pipeline

After identifying the emergency categories and severity, MedPulse determines the facility level required for the case and filters hospitals accordingly.

```text
Emergency Categories + Severity
              |
              v
     Required Facility Level
              |
              v
     Nearby Hospital Search
              |
              v
     Facility Capability Filter
              |
              v
       Bed Availability Filter
              |
              v
       Google Driving Routes
              |
              +-- Driving Distance
              |
              +-- Estimated Travel Time
              |
              v
       Hospital Ranking
              |
              v
        Ranked Hospitals
```

### Hospital Filtering

Hospitals are filtered based on:

- Required facility level
- Hospital facility capability
- Available beds
- Driving route availability

### Hospital Ranking

Hospitals are primarily ranked using estimated driving time.

When hospitals have ETAs within a two-minute tolerance, available bed capacity is used as a tiebreaker.

The system uses the Google Routes API to calculate real-world driving distance and estimated travel time between the user's browser location and candidate hospitals.

---

## NLP Benchmark Results

The NLP classifier was evaluated on a fixed held-out test set containing **77 examples across 15 emergency categories**.

| Metric | Score |
|---|---:|
| Micro Precision | **0.8527** |
| Micro Recall | **0.9649** |
| Micro F1 | **0.9053** |
| Macro Precision | **0.8838** |
| Macro Recall | **0.9757** |
| Macro F1 | **0.9221** |
| Exact Match | **0.7532** |

The evaluation uses a multilabel setup, where an input can belong to multiple emergency categories.

The benchmark also includes category-level evaluation and error analysis to identify cases where the model produces additional or missing categories.

---

## Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- SQLite

### Machine Learning / NLP

- PyTorch
- Transformers
- Sentence Transformers
- Scikit-learn
- Faster-Whisper

### Frontend

- HTML
- CSS
- JavaScript
- Browser Geolocation API

### Routing

- Google Routes API

### Testing

- Pytest

---

## Project Structure

```text
medpulse-blr/
│
├── app/
│   ├── __init__.py
│   ├── audio.py
│   ├── database.py
│   ├── emergency_router.py
│   ├── hospital_capability.py
│   ├── main.py
│   ├── nlp_engine.py
│   ├── ranking.py
│   ├── requirements.py
│   ├── routing.py
│   ├── severity.py
│   ├── supervised_classifier.py
│   └── triage.py
│
├── data/
│   ├── hospitals.csv
│   ├── nlp/
│   │   ├── emergency_examples.json
│   │   └── fixed_test_ids.json
│   ├── processed/
│   └── raw/
│
├── scripts/
│   ├── add_nlp_examples.py
│   ├── add_v11_hard_negatives.py
│   ├── add_v6_examples.py
│   ├── audit_coordinates.py
│   ├── build_hospital_dataset.py
│   ├── create_fixed_benchmark.py
│   ├── enrich_coordinates.py
│   ├── inspect_uphc.py
│   ├── load_hospitals.py
│   ├── seed_simulated_beds.py
│   └── verify_hospital_coordinates.py
│
├── templates/
│   └── index.html
│
├── tests/
│   ├── analyze_nlp_scores.py
│   ├── evaluate_nlp.py
│   ├── evaluate_nlp_v15.py
│   ├── evaluate_nlp_v15_1.py
│   ├── evaluate_nlp_v15_2.py
│   ├── evaluate_nlp_v15_3.py
│   ├── evaluate_nlp_v15_4.py
│   ├── test_audio.py
│   ├── test_emergency_router.py
│   ├── test_full_pipeline.py
│   ├── test_hindi_asr.py
│   ├── test_hindi_medium.py
│   ├── test_hindi_wav.py
│   ├── test_hospital_capability.py
│   ├── test_ranking.py
│   ├── test_requirements.py
│   ├── test_routing.py
│   ├── test_routing_candidates.py
│   └── test_severity.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Installation and Setup

### Prerequisites

- Python 3.11+
- Git
- Google Maps Routes API key

### 1. Clone the Repository

```bash
git clone https://github.com/Sacrak/medpulse-blr.git
cd medpulse-blr
```

### 2. Create a Virtual Environment

On Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Google Routes API

The application uses the Google Routes API to calculate driving distance and estimated travel time.

Set your API key as an environment variable:

```powershell
$env:GOOGLE_MAPS_API_KEY="YOUR_API_KEY"
```

Do not place the actual API key inside the source code or commit it to GitHub.

### 5. Run the Application

Start the FastAPI development server:

```powershell
uvicorn app.main:app --reload
```

The application will be available on the local development server shown by Uvicorn.

---

## Testing

The project includes automated tests covering major components of the system, including:

- Audio processing
- NLP evaluation
- Severity estimation
- Hospital capability filtering
- Hospital ranking
- Routing
- Emergency routing
- End-to-end pipeline behavior

Run the test suite with:

```powershell
pytest
```

---

## Data and Hospital Availability

The hospital dataset contains hospital information used for routing and facility filtering.

> **Important:** Hospital bed availability in the current prototype is **simulated data** and is not connected to a live hospital occupancy system.

The routing system uses hospital coordinates available in the project dataset and Google Routes API for driving distance and estimated travel time.

---

## Security

API credentials are not stored in the source code.

The Google Maps API key is supplied through the:

```text
GOOGLE_MAPS_API_KEY
```

environment variable.

The repository also uses `.gitignore` rules to prevent local environment files, databases, credentials, temporary files, and testing recordings from being committed.

---

## Limitations

MedPulse Bengaluru is currently a prototype and has several limitations:

- Hospital bed availability is simulated rather than obtained from a live hospital information system.
- Google Routes API usage depends on API credentials, quota, and network connectivity.
- Browser geolocation requires user permission.
- NLP performance depends on the quality and coverage of the available dataset.
- Speech recognition performance can vary depending on audio quality, background noise, accent, and language.
- Hospital information requires periodic validation and updating.
- The system provides emergency routing assistance and does not perform medical diagnosis.

---

## Future Improvements

Potential future improvements include:

- Integration with real-time hospital bed availability systems
- Larger and more diverse emergency NLP datasets
- Improved multilingual emergency speech recognition
- Improved handling of ambiguous emergency descriptions
- Real-time traffic-aware routing
- Integration with additional hospital and emergency-service data sources
- Continuous model evaluation and monitoring
- Production-grade authentication, logging, and observability
- Containerized deployment and CI/CD automation

---

## Disclaimer

MedPulse Bengaluru is an academic and software-engineering prototype.

It is intended to demonstrate the integration of:

**Speech Recognition → NLP → Severity Estimation → Hospital Filtering → Routing → Ranking**

It should not be used as a substitute for professional medical advice, emergency services, or clinical decision-making.

---

<div align="center">

### MedPulse Bengaluru

**AI-Assisted Emergency Triage & Hospital Routing**

Built as an academic software-engineering project.

</div>