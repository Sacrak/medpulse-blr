import json
from pathlib import Path

import numpy as np

from app.nlp_engine import load_dataset, load_model
from app.supervised_classifier import SupervisedMultilabelClassifier
from app.severity import determine_severity


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

CATEGORIES = [
    "ABDOMINAL",
    "ALLERGIC_REACTION",
    "ANIMAL_INSECT_BITE",
    "BLEEDING",
    "BURNS",
    "CARDIAC",
    "FEVER_INFECTION",
    "FRACTURE_MUSCULOSKELETAL",
    "NEUROLOGICAL",
    "OBSTETRIC",
    "PEDIATRIC",
    "POISONING",
    "RESPIRATORY",
    "SEIZURE",
    "TRAUMA",
]


THRESHOLDS = {
    "ABDOMINAL": 0.30,
    "ALLERGIC_REACTION": 0.55,
    "ANIMAL_INSECT_BITE": 0.30,
    "BLEEDING": 0.50,
    "BURNS": 0.45,
    "CARDIAC": 0.70,
    "FEVER_INFECTION": 0.50,
    "FRACTURE_MUSCULOSKELETAL": 0.40,
    "NEUROLOGICAL": 0.60,
    "OBSTETRIC": 0.40,
    "PEDIATRIC": 0.30,
    "POISONING": 0.70,
    "RESPIRATORY": 0.55,
    "SEIZURE": 0.30,
    "TRAUMA": 0.45,
}


class TriageEngine:

    def __init__(self):
        print("Loading MedPulse NLP model...")

        self.dataset = load_dataset()
        self.model = load_model()

        self.classifier = SupervisedMultilabelClassifier()

        self._train()

        print("Triage engine ready.")

    # -----------------------------------------------------
    # TRAINING
    # -----------------------------------------------------

    def _train(self):

        benchmark_path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "nlp"
            / "fixed_test_ids.json"
        )

        with open(benchmark_path, "r", encoding="utf-8") as file:
            fixed_test_ids = set(json.load(file))

        # Same development/test separation as V15.4
        development = [
            example
            for example in self.dataset
            if example["id"] not in fixed_test_ids
        ]

        texts = [
            example["text"]
            for example in development
        ]

        print(
            f"Training triage classifier on "
            f"{len(texts)} development examples..."
        )

        # Create embeddings
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

        # Create multilabel target matrix
        category_to_index = {
            category: i
            for i, category in enumerate(CATEGORIES)
        }

        labels = np.zeros(
            (len(development), len(CATEGORIES)),
            dtype=int,
        )

        for row, example in enumerate(development):

            for category in example["categories"]:

                if category in category_to_index:
                    labels[
                        row,
                        category_to_index[category]
                    ] = 1

        # Train on ALL development examples.
        # The 77-example benchmark remains completely untouched.
        self.classifier.fit(
            embeddings,
            labels,
            CATEGORIES,
        )

    # -----------------------------------------------------
    # V15.4 DECISION LAYER
    # -----------------------------------------------------

    def _apply_decision_rules(
        self,
        predictions,
        probabilities,
        text,
    ):

        predictions = predictions.copy()

        idx = {
            category: i
            for i, category in enumerate(CATEGORIES)
        }

        def prob(category):
            return probabilities[idx[category]]

        text_lower = text.lower()

        # -------------------------------------------------
        # CRITICAL CONSCIOUSNESS / RESPONSIVENESS RULE
        # -------------------------------------------------

        critical_awareness_terms = [
            # English
            "unconscious",
            "unresponsive",
            "not responding",
            "not responsive",
            "does not respond",
            "not waking up",

            # Hindi
            "बेहोश",
            "होश नहीं",
            "होश में नहीं",
            "जवाब नहीं दे रहा",
            "जवाब नहीं दे रही",
            "जवाब नहीं दे रहे",
            "रेस्पॉंस नहीं कर रहा",
            "रेस्पॉंस नहीं कर रही",
            "रेस्पॉंस नहीं कर रहे",
            "रिस्पॉन्स नहीं कर रहा",
            "रिस्पॉन्स नहीं कर रही",
            "रिस्पॉन्स नहीं कर रहे",
        ]

        if any(
            term in text_lower
            for term in critical_awareness_terms
        ):
            predictions[idx["NEUROLOGICAL"]] = 1

        # -------------------------------------------------
        # V15 CARDIAC RULE
        # -------------------------------------------------

        cardiac_terms = [
            "chest pain",
            "chest tightness",
            "chest pressure",
            "chest feels tight",
            "sweating",
            "heavy sweating",
            "heart pain",
            "heart attack",
            "மார்பு",
            "நெஞ்சு",
            "ఛాతీ",
            "ಎದೆ",
            "നെഞ്ച്",
        ]

        if (
            any(term in text_lower for term in cardiac_terms)
            and 0.60 <= prob("CARDIAC") < 0.70
        ):
            predictions[idx["CARDIAC"]] = 1

        # -------------------------------------------------
        # V15 ALLERGY RULE
        # -------------------------------------------------

        allergy_terms = [
            "hives",
            "swollen",
            "swelling",
            "face became swollen",
            "lip swelling",
            "lips became swollen",
            "throat is closing",
            "throat closing",
            "anaphylaxis",
            "allergic reaction",
        ]

        if (
            any(term in text_lower for term in allergy_terms)
            and 0.30 <= prob("ALLERGIC_REACTION") < 0.55
        ):
            predictions[idx["ALLERGIC_REACTION"]] = 1

        # -------------------------------------------------
        # V15 RESPIRATORY RULE
        # -------------------------------------------------

        respiratory_terms = [
            "difficulty breathing",
            "difficult to breathe",
            "struggling to breathe",
            "shortness of breath",
            "cannot breathe",
            "can't breathe",
            "cannot speak in full sentences",
            "breathing difficulty",
            "trouble breathing",
            "breathlessness",
        ]

        explicit_breathing = any(
            term in text_lower
            for term in respiratory_terms
        )

        if (
            explicit_breathing
            and 0.35 <= prob("RESPIRATORY") < 0.55
        ):
            predictions[idx["RESPIRATORY"]] = 1

        # -------------------------------------------------
        # PEDIATRIC / OBSTETRIC CLEANUP
        # -------------------------------------------------

        pediatric_terms = [
            "my baby",
            "the baby",
            "my child",
            "the child",
            "my son",
            "my daughter",
        ]

        obstetric_terms = [
            "pregnant",
            "pregnancy",
            "labor",
            "labour",
            "contractions",
            "water broke",
            "giving birth",
            "delivery",
            "expecting a baby",
        ]

        # Hindi and common multilingual pediatric references.
        # Pediatric should be enabled by explicit child/baby context,
        # rather than by a weak classifier score alone.
        pediatric_terms.extend([
            # Hindi
            "बच्चा",
            "बच्चे",
            "बच्ची",
            "बच्चों",
            "बेटा",
            "बेटी",
            "शिशु",
            "नवजात",
            "बेबी",
            "बच्चे को",
            "बच्ची को",
            "बेटे को",
            "बेटी को",
            # Common transliterated forms
            "baccha",
            "bachcha",
            "bachche",
            "bachchi",
            "beta",
            "beti",
            "shishu",
            "navjaat",
            "baby",
        ])

        pediatric_context = any(
            term in text_lower
            for term in pediatric_terms
        )

        obstetric_context = any(
            term in text_lower
            for term in obstetric_terms
        )

        # The pediatric label is intentionally conservative:
        # require explicit child/baby context. This prevents a weak
        # pediatric probability from being triggered by unrelated
        # adult emergency wording or noisy ASR.
        if not pediatric_context:
            predictions[idx["PEDIATRIC"]] = 0

        if pediatric_context and not obstetric_context:
            predictions[idx["OBSTETRIC"]] = 0

        # -------------------------------------------------
        # POISONING / RESPIRATORY
        # -------------------------------------------------

        poisoning_terms = [
            "swallowed",
            "overdose",
            "took too many",
            "too many tablets",
            "too many pills",
            "poison",
            "poisoning",
            "medicine by mistake",
        ]

        poisoning_signal = any(
            term in text_lower
            for term in poisoning_terms
        )

        if (
            poisoning_signal
            and not explicit_breathing
            and prob("RESPIRATORY") < 0.70
        ):
            predictions[idx["RESPIRATORY"]] = 0

        # -------------------------------------------------
        # V14 CHEMICAL INHALATION
        # -------------------------------------------------

        inhalation_terms = [
            "inhaled",
            "inhaling",
            "breathed in",
            "breathing it in",
            "chemical fumes",
            "chemical spill",
            "toxic fumes",
            "gas leak",
            "smoke inhalation",
        ]

        inhalation_signal = any(
            term in text_lower
            for term in inhalation_terms
        )

        if (
            inhalation_signal
            and prob("POISONING") >= 0.70
            and prob("RESPIRATORY") >= 0.25
        ):
            predictions[idx["RESPIRATORY"]] = 1

        # -------------------------------------------------
        # V14 NEUROLOGICAL / RESPIRATORY
        # -------------------------------------------------

        speech_terms = [
            "cannot speak",
            "can't speak",
            "cannot speak in full sentences",
            "can't speak in full sentences",
            "unable to speak",
        ]

        speech_signal = any(
            term in text_lower
            for term in speech_terms
        )

        if (
            speech_signal
            and explicit_breathing
            and prob("RESPIRATORY") >= 0.55
            and prob("NEUROLOGICAL") >= 0.60
        ):
            predictions[idx["NEUROLOGICAL"]] = 0

        # -------------------------------------------------
        # V15.1 INGESTION CLEANUP
        # -------------------------------------------------

        ingestion_terms = [
            "swallowed",
            "swallow",
            "overdose",
            "took too many",
            "too many tablets",
            "too many pills",
            "too much medicine",
            "took too much medicine",
            "ate too many pills",
            "medicine by mistake",
            "medication by mistake",
            "दवाइयां खा",
            "दवाइयाँ खा",
            "दवाइयां ली",
            "दवाइयाँ ली",
            "మందులు తీసుకున్నాను",
            "ఎక్కువ మందులు తీసుకున్నాను",
            "మందులు తీసుకున్న",
            "ఎక్కువ మందులు తీసుకున్న",
            "మందులు",
        ]

        ingestion_signal = any(
            term in text_lower
            for term in ingestion_terms
        )

        if (
            ingestion_signal
            and not inhalation_signal
            and not explicit_breathing
            and prob("POISONING") >= 0.70
        ):
            predictions[idx["RESPIRATORY"]] = 0

        # -------------------------------------------------
        # V15.2 BURN / TRAUMA CLEANUP
        # -------------------------------------------------

        # Burns can be genuine trauma, but a burn by itself should not
        # automatically inherit generic TRAUMA or BLEEDING labels from
        # the multilabel classifier. Keep those categories only when the
        # text contains an explicit supporting signal.
        burn_signal = (
            predictions[idx["BURNS"]] == 1
        )

        explicit_bleeding_terms = [
            "bleeding",
            "bleed",
            "blood",
            "blood loss",
            "losing blood",
            "blood is coming",
            "blood is flowing",
        ]

        explicit_trauma_terms = [
            "accident",
            "crash",
            "collision",
            "road accident",
            "bike accident",
            "car accident",
            "hit by",
            "hit me",
            "was hit",
            "impact",
            "explosion",
            "blast",
            "electrical accident",
            "fire accident",
            "caught fire",
        ]

        explicit_bleeding = any(
            term in text_lower
            for term in explicit_bleeding_terms
        )

        explicit_burn_trauma = any(
            term in text_lower
            for term in explicit_trauma_terms
        )

        if burn_signal:
            if not explicit_bleeding:
                predictions[idx["BLEEDING"]] = 0

            if not explicit_burn_trauma:
                predictions[idx["TRAUMA"]] = 0

        # -------------------------------------------------
        # V15.2 SNAKE BITE
        # -------------------------------------------------

        snake_bite_terms = [
            "snake bite",
            "snakebite",
            "snake bit",
            "bitten by a snake",
            "a snake bit me",
        ]

        snake_bite_signal = any(
            term in text_lower
            for term in snake_bite_terms
        )

        if snake_bite_signal:
            # A snake bite belongs to the dedicated animal/insect
            # bite category. Do not automatically relabel it as
            # POISONING, because that creates a misleading extra
            # category and can make severity depend on a false
            # positive poisoning prediction.
            predictions[idx["ANIMAL_INSECT_BITE"]] = 1
            predictions[idx["POISONING"]] = 0

            # Swelling alone after a snake bite should not create an
            # ALLERGIC_REACTION label. Keep allergy only when the text
            # explicitly describes an allergic/anaphylactic reaction.
            explicit_allergy_terms = [
                "allergic reaction",
                "anaphylaxis",
                "hives",
                "throat is closing",
                "throat closing",
                "lip swelling",
                "lips became swollen",
            ]

            if not any(
                term in text_lower
                for term in explicit_allergy_terms
            ):
                predictions[idx["ALLERGIC_REACTION"]] = 0

            # Keep the dedicated bite category instead of adding a
            # generic trauma label solely because a bite occurred.
            predictions[idx["TRAUMA"]] = 0

        # -------------------------------------------------
        # V15.3 SEIZURE
        # -------------------------------------------------

        seizure_terms = [
            "jerking movements",
            "cannot control",
            "convulsing",
            "convulsion",
            "convulsions",
            "seizure",
            "seizing",
        ]

        if any(
            term in text_lower
            for term in seizure_terms
        ):
            predictions[idx["SEIZURE"]] = 1

        if (
            predictions[idx["SEIZURE"]] == 1
            and any(
                term in text_lower
                for term in [
                    "convulsing",
                    "convulsion",
                    "convulsions",
                ]
            )
        ):
            predictions[idx["NEUROLOGICAL"]] = 0

        # -------------------------------------------------
        # V15.4 OBSTETRIC SIGNAL
        # -------------------------------------------------

        explicit_obstetric_terms = [
            "water broke",
            "waters broke",
            "my water broke",
            "her water broke",
            "water has broken",
            "waters have broken",
        ]

        if any(
            term in text_lower
            for term in explicit_obstetric_terms
        ):
            predictions[idx["OBSTETRIC"]] = 1
            predictions[idx["SEIZURE"]] = 0

        return predictions

    # -----------------------------------------------------
    # PUBLIC PREDICTION FUNCTION
    # -----------------------------------------------------

    def predict(self, text):

        if not text or not text.strip():

            categories = []
            scores = {
                category: 0.0
                for category in CATEGORIES
            }

            return {
                "text": text,
                "categories": categories,
                "scores": scores,
                "severity": "LOW",
            }

        embedding = self.model.encode(
            [text],
            convert_to_numpy=True,
        )

        probabilities = (
            self.classifier.predict_proba(embedding)[0]
        )

        predictions = np.array([
            int(
                probabilities[i]
                >= THRESHOLDS[category]
            )
            for i, category in enumerate(CATEGORIES)
        ])

        predictions = self._apply_decision_rules(
            predictions,
            probabilities,
            text,
        )

        categories = [
            category
            for category, value
            in zip(CATEGORIES, predictions)
            if value == 1
        ]

        scores = {
            category: float(probabilities[i])
            for i, category in enumerate(CATEGORIES)
        }

        severity = determine_severity(
            categories,
            text,
        )

        return {
            "text": text,
            "categories": categories,
            "scores": scores,
            "severity": severity,
        }


# ---------------------------------------------------------
# SIMPLE MANUAL TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    engine = TriageEngine()

    result = engine.predict(
        "I met with a bike accident and my leg is bleeding badly"
    )

    print("\nTriage result:")
    print("Text:", result["text"])
    print("Categories:", result["categories"])
    print("Severity:", result["severity"])

    print("\nScores:")

    for category, score in sorted(
        result["scores"].items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        print(f"{category:<32} {score:.4f}")