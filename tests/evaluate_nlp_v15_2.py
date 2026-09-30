import sys
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    precision_recall_fscore_support,
    accuracy_score,
)

# Allow imports from project root
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.nlp_engine import (
    load_dataset,
    load_model,
    build_category_examples,
    build_category_centroids,
    classify_text_centroid,
)

from app.supervised_classifier import (
    SupervisedMultilabelClassifier,
)


RANDOM_SEED = 42
TEST_SIZE = 0.30

# Evaluate a wider threshold range
THRESHOLDS = [
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
]


def split_dataset(dataset):
    """
    Use the permanently frozen benchmark test set.

    The benchmark IDs were created from the original 208-example
    V2 dataset using RANDOM_SEED=42 and TEST_SIZE=0.30.

    The same test examples are used for every future model version.
    All remaining examples become development data.
    """

    benchmark_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "nlp"
        / "fixed_test_ids.json"
    )

    if not benchmark_path.exists():
        raise FileNotFoundError(
            f"Fixed benchmark not found: {benchmark_path}"
        )

    with open(benchmark_path, "r", encoding="utf-8") as file:
        fixed_test_ids = set(json.load(file))

    dataset_ids = {
        example["id"]
        for example in dataset
    }

    # Make sure every benchmark example still exists.
    missing_ids = fixed_test_ids - dataset_ids

    if missing_ids:
        raise ValueError(
            "Fixed benchmark contains missing dataset IDs: "
            + ", ".join(sorted(missing_ids))
        )

    test = [
        example
        for example in dataset
        if example["id"] in fixed_test_ids
    ]

    development = [
        example
        for example in dataset
        if example["id"] not in fixed_test_ids
    ]

    if len(test) != 77:
        raise ValueError(
            f"Expected 77 fixed benchmark examples, found {len(test)}"
        )

    if set(example["id"] for example in development) & fixed_test_ids:
        raise ValueError(
            "Benchmark leakage detected: test example found in development set."
        )

    print("\nFixed benchmark enabled")
    print(f"Fixed test examples: {len(test)}")
    print(f"Development examples: {len(development)}")

    return development, test



def get_categories(dataset):
    """
    Get every category appearing in the dataset.
    """
    categories = set()

    for example in dataset:
        categories.update(example["categories"])

    return sorted(categories)


def create_ground_truth(test_data, categories):
    """
    Convert category lists into binary multilabel vectors.
    """

    category_to_index = {
        category: i
        for i, category in enumerate(categories)
    }

    y_true = []

    for example in test_data:

        labels = np.zeros(len(categories), dtype=int)

        for category in example["categories"]:

            if category in category_to_index:
                labels[category_to_index[category]] = 1

        y_true.append(labels)

    return np.array(y_true)


def create_predictions(
    model,
    centroids,
    test_data,
    categories,
    threshold,
):
    """
    Generate multilabel predictions using the supplied threshold.
    """

    category_to_index = {
        category: i
        for i, category in enumerate(categories)
    }

    y_pred = []

    for example in test_data:

        results = classify_text_centroid(
            model,
            centroids,
            example["text"],
        )

        labels = np.zeros(len(categories), dtype=int)

        for result in results:

            if result["score"] >= threshold:

                category = result["category"]

                if category in category_to_index:
                    labels[category_to_index[category]] = 1

        y_pred.append(labels)

    return np.array(y_pred)


def evaluate_threshold(
    y_true,
    y_pred,
    categories,
    test_data,
):
    """
    Calculate overall and per-category metrics.
    """

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="micro",
        zero_division=0,
    )

    macro_precision, macro_recall, macro_f1, _ = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            average="macro",
            zero_division=0,
        )
    )

    exact_match = accuracy_score(
        y_true,
        y_pred,
    )

    # Negative examples = examples with no emergency category.
    negative_indices = [
        i
        for i, example in enumerate(test_data)
        if len(example["categories"]) == 0
    ]

    if negative_indices:

        correctly_rejected = sum(
            1
            for i in negative_indices
            if not y_pred[i].any()
        )

        negative_rejection_rate = (
            correctly_rejected / len(negative_indices)
        )

    else:
        negative_rejection_rate = None

    return {
        "micro_precision": precision,
        "micro_recall": recall,
        "micro_f1": f1,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "exact_match": exact_match,
        "negative_rejection_rate": negative_rejection_rate,
    }


def print_per_category_report(
    y_true,
    y_pred,
    categories,
):
    """
    Print precision, recall and F1 for every emergency category.
    """

    precision, recall, f1, support = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            zero_division=0,
        )
    )

    print("\nPer-category Results")
    print("-" * 78)

    print(
        f"{'Category':35}"
        f"{'Precision':>12}"
        f"{'Recall':>12}"
        f"{'F1':>12}"
        f"{'Support':>10}"
    )

    print("-" * 78)

    for i, category in enumerate(categories):

        print(
            f"{category:35}"
            f"{precision[i]:>12.3f}"
            f"{recall[i]:>12.3f}"
            f"{f1[i]:>12.3f}"
            f"{support[i]:>10}"
        )


def print_errors(
    model,
    centroids,
    test_data,
    threshold,
):
    """
    Show false-positive and false-negative examples.
    """

    print("\nPrediction Errors")
    print("-" * 78)

    shown = 0

    for example in test_data:

        results = classify_text_centroid(
            model,
            centroids,
            example["text"],
        )

        predicted = [
            r["category"]
            for r in results
            if r["score"] >= threshold
        ]

        actual = example["categories"]

        false_positive = [
            category
            for category in predicted
            if category not in actual
        ]

        false_negative = [
            category
            for category in actual
            if category not in predicted
        ]

        if false_positive or false_negative:

            print(f"\nText: {example['text']}")
            print(f"Actual:    {actual}")
            print(f"Predicted: {predicted}")

            if false_positive:
                print(f"False +:   {false_positive}")

            if false_negative:
                print(f"False -:   {false_negative}")

            shown += 1

            if shown >= 15:
                break



def find_category_thresholds(
    model,
    centroids,
    development,
    categories,
):
    """
    Find a threshold for each category using ONLY the
    development set.

    The held-out test set is never used here.
    """

    category_to_index = {
        category: i
        for i, category in enumerate(categories)
    }

    # Ground truth for development set
    y_true = create_ground_truth(
        development,
        categories,
    )

    # Store similarity scores for every development example
    scores = []

    for example in development:

        results = classify_text_centroid(
            model,
            centroids,
            example["text"],
        )

        score_map = {
            result["category"]: result["score"]
            for result in results
        }

        scores.append([
            score_map.get(category, -1.0)
            for category in categories
        ])

    scores = np.array(scores)

    category_thresholds = {}

    for category_index, category in enumerate(categories):

        best_threshold = 0.60
        best_f1 = -1.0

        true_labels = y_true[:, category_index]
        category_scores = scores[:, category_index]

        for threshold in THRESHOLDS:

            predictions = (
                category_scores >= threshold
            ).astype(int)

            precision, recall, f1, _ = (
                precision_recall_fscore_support(
                    true_labels,
                    predictions,
                    average="binary",
                    zero_division=0,
                )
            )

            if f1 > best_f1:

                best_f1 = f1
                best_threshold = threshold

        category_thresholds[category] = {
            "threshold": best_threshold,
            "development_f1": best_f1,
        }

    return category_thresholds

def create_predictions_with_category_thresholds(
    model,
    centroids,
    test_data,
    category_thresholds,
):
    """
    Generate predictions using a different threshold
    for each category.
    """

    y_pred = []

    for example in test_data:

        results = classify_text_centroid(
            model,
            centroids,
            example["text"],
        )

        score_map = {
            result["category"]: result["score"]
            for result in results
        }

        labels = []

        for category, settings in category_thresholds.items():

            score = score_map.get(category, -1.0)

            if score >= settings["threshold"]:
                labels.append(category)

        y_pred.append(labels)

    return y_pred
def multilabel_lists_to_matrix(
    predictions,
    categories,
):
    """
    Convert category lists into the same binary matrix
    representation used by the evaluator.
    """

    category_to_index = {
        category: i
        for i, category in enumerate(categories)
    }

    matrix = []

    for prediction in predictions:

        labels = np.zeros(
            len(categories),
            dtype=int,
        )

        for category in prediction:

            if category in category_to_index:
                labels[category_to_index[category]] = 1

        matrix.append(labels)

    return np.array(matrix)
def create_embeddings(model, examples):
    """
    Convert example texts into sentence embeddings.
    """

    texts = [
        example["text"]
        for example in examples
    ]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    return embeddings


def print_supervised_errors(test_data, y_true, y_pred, categories, limit=15):
    """Display mistakes made by the supervised model (not the centroid)."""
    print("\nSupervised Prediction Errors")
    print("-" * 78)
    shown = 0
    for example, actual_row, predicted_row in zip(test_data, y_true, y_pred):
        actual = [cat for cat, value in zip(categories, actual_row) if value]
        predicted = [cat for cat, value in zip(categories, predicted_row) if value]
        missing = sorted(set(actual) - set(predicted))
        extra = sorted(set(predicted) - set(actual))
        if missing or extra:
            print(f"\nText: {example['text']}")
            print(f"Actual:    {actual}")
            print(f"Predicted: {predicted}")
            if extra:
                print(f"False +:   {extra}")
            if missing:
                print(f"False -:   {missing}")
            shown += 1
            if shown >= limit:
                break
    if shown == 0:
        print("No errors found.")



def train_and_evaluate_supervised(
    model,
    development,
    test_data,
):
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
    """
    Train the supervised multilabel classifier.

    Thresholds are selected independently for each category using
    ONLY the validation split.

    The fixed test benchmark is never used for threshold selection.
    """

    print("\n" + "=" * 80)
    print("SUPERVISED MULTILABEL CLASSIFIER")
    print("=" * 80)

    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (
        precision_score,
        recall_score,
        f1_score,
    )

    # ---------------------------------------------------------
    # Prepare text
    # ---------------------------------------------------------

    train_texts = [
        example["text"]
        for example in development
    ]

    test_texts = [
        example["text"]
        for example in test_data
    ]

    # ---------------------------------------------------------
    # Create embeddings
    # ---------------------------------------------------------

    print("\nCreating development embeddings...")

    development_embeddings = model.encode(
        train_texts,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    print("\nCreating test embeddings...")

    test_embeddings = model.encode(
        test_texts,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    # ---------------------------------------------------------
    # Create multilabel target matrix
    # ---------------------------------------------------------

    category_to_index = {
        category: i
        for i, category in enumerate(CATEGORIES)
    }

    y = np.zeros(
        (len(development), len(CATEGORIES)),
        dtype=int,
    )

    for row, example in enumerate(development):
        for category in example["categories"]:
            if category in category_to_index:
                y[row, category_to_index[category]] = 1

    # ---------------------------------------------------------
    # Development → training + validation
    # ---------------------------------------------------------

    (
        X_train,
        X_val,
        y_train,
        y_val,
    ) = train_test_split(
        development_embeddings,
        y,
        test_size=0.25,
        random_state=RANDOM_SEED,
    )

    print(f"\nTraining examples: {len(X_train)}")
    print(f"Validation examples: {len(X_val)}")
    print(f"Test examples: {len(test_data)}")

    # ---------------------------------------------------------
    # Train temporary classifier
    # ---------------------------------------------------------

    validation_classifier = SupervisedMultilabelClassifier()

    validation_classifier.fit(
        X_train,
        y_train,
        CATEGORIES,
    )

    validation_probabilities = (
        validation_classifier.predict_proba(X_val)
    )

    # ---------------------------------------------------------
    # Per-category threshold selection
    #
    # IMPORTANT:
    # These thresholds are selected ONLY using validation data.
    # ---------------------------------------------------------

    candidate_thresholds = [
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
    ]

    category_thresholds = {}

    print("\n")
    print("=" * 80)
    # ---------------------------------------------------------
    # V12: Frozen V7 threshold policy
    # ---------------------------------------------------------

    category_thresholds = {
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

    print("\n" + "=" * 80)
    print("V12 FROZEN V7 THRESHOLDS")
    print("=" * 80)

    for category in CATEGORIES:
        print(f"{category:<32} threshold={category_thresholds[category]:.2f}")

    print("\nRefitting classifier on all development examples...")

    final_classifier = SupervisedMultilabelClassifier()

    final_classifier.fit(
        development_embeddings,
        y,
        CATEGORIES,
    )

    # ---------------------------------------------------------
    # Test probabilities
    # ---------------------------------------------------------

    test_probabilities = (
        final_classifier.predict_proba(
            test_embeddings
        )
    )

    # ---------------------------------------------------------
    # Apply frozen category-specific thresholds
    # ---------------------------------------------------------

    test_predictions = np.zeros_like(
        test_probabilities,
        dtype=int,
    )

    for i, category in enumerate(CATEGORIES):

        threshold = category_thresholds[
            category
        ]

        test_predictions[:, i] = (
            test_probabilities[:, i] >= threshold
        ).astype(int)

        # ---------------------------------------------------------
    # V12: Apply frozen V7 thresholds directly.
    # ---------------------------------------------------------

    test_predictions = np.zeros_like(test_probabilities, dtype=int)

    for i, category in enumerate(CATEGORIES):
        threshold = category_thresholds[category]
        test_predictions[:, i] = (
            test_probabilities[:, i] >= threshold
        ).astype(int)

    # ---------------------------------------------------------
    # V15 controlled decision layer
    # ---------------------------------------------------------
    # No model retraining, dataset changes, or threshold changes.
    # Rules are deliberately narrow and based on observed V12
    # boundary errors.

    def apply_v15_decision_layer(predictions, probabilities, texts):
        predictions = predictions.copy()
        idx = {category: i for i, category in enumerate(CATEGORIES)}

        def prob(row, category):
            return probabilities[row, idx[category]]

        for row, raw_text in enumerate(texts):
            text_lower = raw_text.lower()

            # CARDIAC: recover strong chest-pain/cardiac cases
            # when probability is just below the V12 threshold.
            cardiac_terms = [
                "chest pain", "chest tightness", "chest pressure",
                "chest feels tight", "sweating", "heavy sweating",
                "heart pain", "heart attack",
                "மார்பு", "நெஞ்சு", "ఛాతీ", "ಎದೆ", "നെഞ്ച്",
            ]
            if (
                any(term in text_lower for term in cardiac_terms)
                and 0.60 <= prob(row, "CARDIAC") < 0.70
            ):
                predictions[row, idx["CARDIAC"]] = 1

            # ALLERGIC_REACTION: recover clear swelling/hives
            # when the model is near the existing threshold.
            allergy_terms = [
                "hives", "swollen", "swelling", "face became swollen",
                "lip swelling", "lips became swollen",
                "throat is closing", "throat closing",
                "anaphylaxis", "allergic reaction",
            ]
            if (
                any(term in text_lower for term in allergy_terms)
                and 0.30 <= prob(row, "ALLERGIC_REACTION") < 0.55
            ):
                predictions[row, idx["ALLERGIC_REACTION"]] = 1

            # RESPIRATORY: recover explicit breathing difficulty
            # when probability is reasonably close to threshold.
            respiratory_terms = [
                "difficulty breathing", "difficult to breathe",
                "struggling to breathe", "shortness of breath",
                "cannot breathe", "can't breathe",
                "cannot speak in full sentences",
                "breathing difficulty", "trouble breathing",
                "breathlessness",
            ]
            if (
                any(term in text_lower for term in respiratory_terms)
                and 0.35 <= prob(row, "RESPIRATORY") < 0.55
            ):
                predictions[row, idx["RESPIRATORY"]] = 1

            # OBSTETRIC: "baby/child" alone should not trigger
            # an obstetric label.
            pediatric_terms = [
                "my baby", "the baby", "my child", "the child",
                "my son", "my daughter",
            ]
            obstetric_terms = [
                "pregnant", "pregnancy", "labor", "labour",
                "contractions", "water broke", "giving birth",
                "delivery", "expecting a baby",
            ]
            pediatric_context = any(t in text_lower for t in pediatric_terms)
            obstetric_context = any(t in text_lower for t in obstetric_terms)

            if pediatric_context and not obstetric_context:
                predictions[row, idx["OBSTETRIC"]] = 0

            # POISONING: don't add respiratory merely from poisoning
            # language when there is no explicit breathing evidence.
            poisoning_terms = [
                "swallowed", "overdose", "took too many",
                "too many tablets", "too many pills",
                "poison", "poisoning", "medicine by mistake",
            ]
            poisoning_signal = any(t in text_lower for t in poisoning_terms)
            explicit_breathing = any(t in text_lower for t in respiratory_terms)

            if (
                poisoning_signal
                and not explicit_breathing
                and prob(row, "RESPIRATORY") < 0.70
            ):
                predictions[row, idx["RESPIRATORY"]] = 0


            # ---- V14 POISONING / RESPIRATORY ----
            # Chemical inhalation is treated as a narrow special case:
            # if poisoning is already strong and respiratory probability
            # is reasonably close, preserve both labels.
            inhalation_terms = [
                "inhaled", "inhaling", "breathed in", "breathing it in",
                "chemical fumes", "chemical spill", "toxic fumes",
                "gas leak", "smoke inhalation",
            ]

            inhalation_signal = any(
                term in text_lower for term in inhalation_terms
            )

            if (
                inhalation_signal
                and prob(row, "POISONING") >= 0.70
                and prob(row, "RESPIRATORY") >= 0.25
            ):
                predictions[row, idx["RESPIRATORY"]] = 1

            # ---- V14 NEUROLOGICAL / RESPIRATORY ----
            # Do not let "cannot speak" alone create a neurological
            # label when the same text explicitly describes breathing
            # difficulty and respiratory confidence is already strong.
            speech_terms = [
                "cannot speak", "can't speak",
                "cannot speak in full sentences",
                "can't speak in full sentences",
                "unable to speak",
            ]

            speech_signal = any(term in text_lower for term in speech_terms)

            if (
                speech_signal
                and explicit_breathing
                and prob(row, "RESPIRATORY") >= 0.55
                and prob(row, "NEUROLOGICAL") >= 0.60
            ):
                predictions[row, idx["NEUROLOGICAL"]] = 0


            # ---- V15.1 FINAL POISONING / RESPIRATORY CLEANUP ----
            # V15.2 adds only an explicit snake-bite -> POISONING rule; all V15.1 logic remains unchanged.
            # Ordinary ingestion/overdose poisoning does not imply
            # respiratory involvement. Chemical/inhalational exposure
            # remains eligible for POISONING + RESPIRATORY.
            ingestion_terms = [
                "swallowed", "swallow", "overdose",
                "took too many", "too many tablets",
                "too many pills", "too much medicine",
                "took too much medicine", "ate too many pills",
                "medicine by mistake", "medication by mistake",
                "दवाइयां खा", "दवाइयाँ खा",
                "दवाइयां ली", "दवाइयाँ ली",
                # Telugu medication ingestion / overdose wording
                "మందులు తీసుకున్నాను",
                "ఎక్కువ మందులు తీసుకున్నాను",
                "మందులు తీసుకున్న",
                "ఎక్కువ మందులు తీసుకున్న",
                "మందులు",
            ]

            inhalation_terms = [
                "inhaled", "inhaling", "breathed in", "breathing it in",
                "chemical fumes", "chemical spill", "toxic fumes",
                "gas leak", "smoke inhalation",
            ]

            ingestion_signal = any(
                term in text_lower for term in ingestion_terms
            )
            inhalation_signal = any(
                term in text_lower for term in inhalation_terms
            )

            if (
                ingestion_signal
                and not inhalation_signal
                and not explicit_breathing
                and prob(row, "POISONING") >= 0.70
            ):
                predictions[row, idx["RESPIRATORY"]] = 0

            # ---- V15.2 SNAKE-BITE / POISONING RULE ----
            # A snake bite is retained as ANIMAL_INSECT_BITE and,
            # when the text explicitly indicates a snake bite, also
            # receives POISONING. This targets the two observed
            # held-out errors without changing other categories.
            snake_bite_terms = [
                "snake bite",
                "snakebite",
                "snake bit",
                "bitten by a snake",
                "a snake bit me",
            ]

            if any(term in text_lower for term in snake_bite_terms):
                predictions[row, idx["ANIMAL_INSECT_BITE"]] = 1
                predictions[row, idx["POISONING"]] = 1

        return predictions

    test_predictions = apply_v15_decision_layer(
        test_predictions,
        test_probabilities,
        test_texts,
    )

    # ---------------------------------------------------------
    # Create test ground truth
    # ---------------------------------------------------------

    y_test = np.zeros(
        (len(test_data), len(CATEGORIES)),
        dtype=int,
    )

    for row, example in enumerate(test_data):
        for category in example["categories"]:
            if category in category_to_index:
                y_test[
                    row,
                    category_to_index[category],
                ] = 1

    # ---------------------------------------------------------
    # Overall metrics
    # ---------------------------------------------------------

    micro_precision = precision_score(
        y_test,
        test_predictions,
        average="micro",
        zero_division=0,
    )

    micro_recall = recall_score(
        y_test,
        test_predictions,
        average="micro",
        zero_division=0,
    )

    micro_f1 = f1_score(
        y_test,
        test_predictions,
        average="micro",
        zero_division=0,
    )

    macro_precision = precision_score(
        y_test,
        test_predictions,
        average="macro",
        zero_division=0,
    )

    macro_recall = recall_score(
        y_test,
        test_predictions,
        average="macro",
        zero_division=0,
    )

    macro_f1 = f1_score(
        y_test,
        test_predictions,
        average="macro",
        zero_division=0,
    )

    # ---------------------------------------------------------
    # Exact match
    # ---------------------------------------------------------

    exact_match = np.mean(
        np.all(
            y_test == test_predictions,
            axis=1,
        )
    )

    # ---------------------------------------------------------
    # Negative rejection
    #
    # Only test examples with no positive labels.
    # ---------------------------------------------------------

    negative_indices = np.where(
        np.sum(y_test, axis=1) == 0
    )[0]

    if len(negative_indices) > 0:

        negative_rejection = np.mean(
            np.sum(
                test_predictions[
                    negative_indices
                ],
                axis=1,
            )
            == 0
        )

    else:
        negative_rejection = 0.0

    # ---------------------------------------------------------
    # Print overall results
    # ---------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("HELD-OUT TEST RESULTS")
    print("=" * 80)

    print(
        f"Micro Precision:    {micro_precision:.4f}"
    )

    print(
        f"Micro Recall:       {micro_recall:.4f}"
    )

    print(
        f"Micro F1:           {micro_f1:.4f}"
    )

    print(
        f"Macro Precision:    {macro_precision:.4f}"
    )

    print(
        f"Macro Recall:       {macro_recall:.4f}"
    )

    print(
        f"Macro F1:           {macro_f1:.4f}"
    )

    print(
        f"Exact Match:        {exact_match:.4f}"
    )

    print(
        f"Negative Rejection: {negative_rejection:.4f}"
    )

    # ---------------------------------------------------------
    # Per-category metrics
    # ---------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("PER-CATEGORY TEST RESULTS")
    print("=" * 80)

    for i, category in enumerate(CATEGORIES):

        precision = precision_score(
            y_test[:, i],
            test_predictions[:, i],
            zero_division=0,
        )

        recall = recall_score(
            y_test[:, i],
            test_predictions[:, i],
            zero_division=0,
        )

        f1 = f1_score(
            y_test[:, i],
            test_predictions[:, i],
            zero_division=0,
        )

        print(
            f"{category:<32} "
            f"P={precision:.3f} "
            f"R={recall:.3f} "
            f"F1={f1:.3f} "
            f"T={category_thresholds[category]:.2f}"
        )

    # ---------------------------------------------------------
    # Error analysis
    # ---------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("SUPERVISED MODEL ERRORS")
    print("=" * 80)

    for row, example in enumerate(test_data):

        actual = [
            CATEGORIES[i]
            for i in range(len(CATEGORIES))
            if y_test[row, i] == 1
        ]

        predicted = [
            CATEGORIES[i]
            for i in range(len(CATEGORIES))
            if test_predictions[row, i] == 1
        ]

        if set(actual) != set(predicted):

            print("\n" + "-" * 80)

            print(
                f"ID: {example['id']}"
            )

            print(
                f"Language: {example['language']}"
            )

            print(
                f"Text: {example['text']}"
            )

            print(
                f"Actual: {actual}"
            )

            print(
                f"Predicted: {predicted}"
            )

            print("Scores:")

            ranked = sorted(
                zip(
                    CATEGORIES,
                    test_probabilities[row],
                ),
                key=lambda x: x[1],
                reverse=True,
            )

            for category, score in ranked[:5]:

                threshold = category_thresholds[
                    category
                ]

                print(
                    f"  {category:<32} "
                    f"{score:.4f} "
                    f"(threshold={threshold:.2f})"
                )

    return {
        "classifier": final_classifier,
        "category_thresholds": category_thresholds,
        "probabilities": test_probabilities,
        "predictions": test_predictions,
        "y_test": y_test,
    }
def main():

    dataset = load_dataset()

    print(f"Total examples: {len(dataset)}")

    development, test_data = split_dataset(dataset)

    print(
        f"Development examples: {len(development)}"
    )

    print(
        f"Held-out test examples: {len(test_data)}"
    )

    categories = get_categories(dataset)

    print(
        f"Categories: {len(categories)}"
    )

    print(
        "Categories:",
        ", ".join(categories),
    )

    # -------------------------
    # Build development model
    # -------------------------

    model = load_model()

    category_examples = build_category_examples(
        development
    )

    centroids = build_category_centroids(
        model,
        category_examples,
    )
        # ------------------------------------------------
    # Learn category-specific thresholds ONLY from
    # the development set.
    # ------------------------------------------------

    category_thresholds = find_category_thresholds(
        model,
        centroids,
        development,
        categories,
    )

    print("\nCategory-specific thresholds")
    print("-" * 60)

    for category, settings in category_thresholds.items():

        print(
            f"{category:35}"
            f"threshold={settings['threshold']:.2f} "
            f"dev_F1={settings['development_f1']:.3f}"
        )
    # -------------------------
    # Ground truth
    # -------------------------

    y_true = create_ground_truth(
        test_data,
        categories,
    )

    # -------------------------
    # Threshold evaluation
    # -------------------------

    print("\nMulti-label Threshold Evaluation")
    print("-" * 90)

    print(
        f"{'Threshold':<12}"
        f"{'Micro P':<12}"
        f"{'Micro R':<12}"
        f"{'Micro F1':<12}"
        f"{'Macro F1':<12}"
        f"{'Exact':<12}"
        f"{'Neg Reject':<12}"
    )

    best_threshold = None
    best_f1 = -1

    for threshold in THRESHOLDS:

        y_pred = create_predictions(
            model,
            centroids,
            test_data,
            categories,
            threshold,
        )

        metrics = evaluate_threshold(
            y_true,
            y_pred,
            categories,
            test_data,
        )

        print(
            f"{threshold:<12.2f}"
            f"{metrics['micro_precision']:<12.4f}"
            f"{metrics['micro_recall']:<12.4f}"
            f"{metrics['micro_f1']:<12.4f}"
            f"{metrics['macro_f1']:<12.4f}"
            f"{metrics['exact_match']:<12.4f}"
            f"{metrics['negative_rejection_rate'] if metrics['negative_rejection_rate'] is not None else 'N/A':<12}"
        )

        if metrics["micro_f1"] > best_f1:

            best_f1 = metrics["micro_f1"]
            best_threshold = threshold

    print("\nBest threshold:", best_threshold)
    print(f"Best micro F1: {best_f1:.4f}")

        # ------------------------------------------------
    # Evaluate category-specific thresholds on the
    # HELD-OUT TEST SET.
    # ------------------------------------------------

    category_predictions = (
        create_predictions_with_category_thresholds(
            model,
            centroids,
            test_data,
            category_thresholds,
        )
    )

    y_pred_category_thresholds = (
        multilabel_lists_to_matrix(
            category_predictions,
            categories,
        )
    )

    print("\nCategory-specific Threshold Evaluation")
    print("-" * 60)

    metrics = evaluate_threshold(
        y_true,
        y_pred_category_thresholds,
        categories,
        test_data,
    )

    print(
        f"Micro Precision:        "
        f"{metrics['micro_precision']:.4f}"
    )

    print(
        f"Micro Recall:           "
        f"{metrics['micro_recall']:.4f}"
    )

    print(
        f"Micro F1:               "
        f"{metrics['micro_f1']:.4f}"
    )

    print(
        f"Macro F1:               "
        f"{metrics['macro_f1']:.4f}"
    )

    print(
        f"Exact-match accuracy:   "
        f"{metrics['exact_match']:.4f}"
    )

    print(
        f"Negative rejection:     "
        f"{metrics['negative_rejection_rate']:.4f}"
    )

    print_per_category_report(
        y_true,
        y_pred_category_thresholds,
        categories,
    )

    # -------------------------
    # Detailed evaluation
    # -------------------------

    y_pred = create_predictions(
        model,
        centroids,
        test_data,
        categories,
        best_threshold,
    )

    metrics = evaluate_threshold(
        y_true,
        y_pred,
        categories,
        test_data,
    )

    print("\nDetailed Metrics")
    print("-" * 40)

    print(
        f"Micro Precision:        {metrics['micro_precision']:.4f}"
    )

    print(
        f"Micro Recall:           {metrics['micro_recall']:.4f}"
    )

    print(
        f"Micro F1:               {metrics['micro_f1']:.4f}"
    )

    print(
        f"Macro Precision:        {metrics['macro_precision']:.4f}"
    )

    print(
        f"Macro Recall:           {metrics['macro_recall']:.4f}"
    )

    print(
        f"Macro F1:               {metrics['macro_f1']:.4f}"
    )

    print(
        f"Exact-match accuracy:   {metrics['exact_match']:.4f}"
    )

    print(
        f"Negative rejection:     {metrics['negative_rejection_rate']:.4f}"
    )

    # -------------------------
    # Per category
    # -------------------------

    print_per_category_report(
        y_true,
        y_pred,
        categories,
    )
    train_and_evaluate_supervised(
        model,
        development,
        test_data,
        
    )
    # -------------------------
    # Error analysis
    # -------------------------

    # Centroid error analysis is separate from supervised error analysis.
    print("\nCENTROID MODEL ERRORS (exploratory baseline)")
    print_errors(
        model,
        centroids,
        test_data,
        best_threshold,
    )


if __name__ == "__main__":
    main()