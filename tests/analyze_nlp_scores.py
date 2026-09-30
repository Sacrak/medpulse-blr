import json
import sys
from pathlib import Path

import numpy as np

# Allow imports from project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.nlp_engine import load_dataset, load_model
from app.supervised_classifier import SupervisedMultilabelClassifier


RANDOM_SEED = 42
TEST_SIZE = 0.30

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


def load_fixed_test_ids():
    path = (
        PROJECT_ROOT
        / "data"
        / "nlp"
        / "fixed_test_ids.json"
    )

    with open(path, "r", encoding="utf-8") as f:
        return set(json.load(f))


def create_ground_truth(examples):
    y = np.zeros(
        (len(examples), len(CATEGORIES)),
        dtype=int,
    )

    category_to_index = {
        category: i
        for i, category in enumerate(CATEGORIES)
    }

    for row, example in enumerate(examples):
        for category in example["categories"]:
            if category in category_to_index:
                y[row, category_to_index[category]] = 1

    return y


def print_case(
    example,
    probabilities,
    top_k=5,
):
    print("\n" + "=" * 90)
    print(f"ID: {example['id']}")
    print(f"Language: {example['language']}")
    print(f"Text: {example['text']}")
    print(f"Actual: {example['categories']}")

    ranked = sorted(
        zip(CATEGORIES, probabilities),
        key=lambda x: x[1],
        reverse=True,
    )

    print("\nTop scores:")
    for category, score in ranked[:top_k]:
        print(f"  {category:<32} {score:.4f}")

    print("\nAll scores:")
    for category, score in ranked:
        print(f"  {category:<32} {score:.4f}")


def main():
    dataset = load_dataset()

    print(f"Total examples: {len(dataset)}")

    fixed_test_ids = load_fixed_test_ids()

    test_data = [
        example
        for example in dataset
        if example["id"] in fixed_test_ids
    ]

    development = [
        example
        for example in dataset
        if example["id"] not in fixed_test_ids
    ]

    print(f"Development examples: {len(development)}")
    print(f"Fixed test examples: {len(test_data)}")

    if len(test_data) != 77:
        raise ValueError(
            f"Expected 77 fixed test examples, "
            f"found {len(test_data)}"
        )

    # ---------------------------------------------------------
    # Load embedding model
    # ---------------------------------------------------------

    model = load_model()

    print("\nCreating development embeddings...")

    development_embeddings = model.encode(
        [x["text"] for x in development],
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    print("\nCreating test embeddings...")

    test_embeddings = model.encode(
        [x["text"] for x in test_data],
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    # ---------------------------------------------------------
    # Create multilabel training matrix
    # ---------------------------------------------------------

    y_development = create_ground_truth(
        development
    )

    # ---------------------------------------------------------
    # Train classifier on ALL development examples
    #
    # This mirrors the final V3 refit stage.
    # ---------------------------------------------------------

    classifier = SupervisedMultilabelClassifier()

    classifier.fit(
        development_embeddings,
        y_development,
        CATEGORIES,
    )

    # ---------------------------------------------------------
    # Get raw probability scores
    # ---------------------------------------------------------

    probabilities = classifier.predict_proba(
        test_embeddings
    )

    # ---------------------------------------------------------
    # 1. Print all benchmark cases
    # ---------------------------------------------------------

    print("\n")
    print("=" * 90)
    print("FIXED BENCHMARK SCORE ANALYSIS")
    print("=" * 90)

    for example, scores in zip(
        test_data,
        probabilities,
    ):
        print_case(
            example,
            scores,
            top_k=5,
        )

    # ---------------------------------------------------------
    # 2. Analyze important category boundaries
    # ---------------------------------------------------------

    important_pairs = [
        ("CARDIAC", "RESPIRATORY"),
        ("ALLERGIC_REACTION", "RESPIRATORY"),
        ("POISONING", "RESPIRATORY"),
        ("TRAUMA", "FRACTURE_MUSCULOSKELETAL"),
        ("ABDOMINAL", "CARDIAC"),
        ("BURNS", "ALLERGIC_REACTION"),
    ]

    print("\n")
    print("=" * 90)
    print("CATEGORY SCORE BOUNDARIES")
    print("=" * 90)

    category_to_index = {
        category: i
        for i, category in enumerate(CATEGORIES)
    }

    for category_a, category_b in important_pairs:

        ia = category_to_index[category_a]
        ib = category_to_index[category_b]

        print(
            f"\n{category_a} vs {category_b}"
        )
        print("-" * 70)

        for example, scores in zip(
            test_data,
            probabilities,
        ):
            actual = set(example["categories"])

            if (
                category_a in actual
                or category_b in actual
            ):
                print(
                    f"{example['id']}: "
                    f"{category_a}={scores[ia]:.3f}, "
                    f"{category_b}={scores[ib]:.3f} | "
                    f"actual={example['categories']}"
                )


if __name__ == "__main__":
    main()