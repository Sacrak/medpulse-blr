import json
import random
from pathlib import Path


DATASET_PATH = Path("data/nlp/emergency_examples.json")
OUTPUT_PATH = Path("data/nlp/fixed_test_ids.json")

RANDOM_SEED = 42
TEST_SIZE = 0.30


def create_fixed_test_set(dataset):
    """
    Reproduce the original V2 category-aware split
    using ONLY the first 208 examples.
    """

    # V2 dataset
    v2_dataset = [
        example
        for example in dataset
        if int(example["id"].split("_")[1]) <= 208
    ]

    if len(v2_dataset) != 208:
        raise ValueError(
            f"Expected 208 V2 examples, found {len(v2_dataset)}"
        )

    random.seed(RANDOM_SEED)

    category_examples = {}

    for example in v2_dataset:
        for category in example["categories"]:
            category_examples.setdefault(category, []).append(example)

    negative_examples = [
        example
        for example in v2_dataset
        if not example["categories"]
    ]

    test = []
    already_assigned_test = set()

    # Same category-aware procedure used by the evaluator
    for category, examples in category_examples.items():

        examples = examples.copy()
        random.shuffle(examples)

        test_count = max(
            1,
            round(len(examples) * TEST_SIZE)
        )

        category_test = examples[:test_count]

        for example in category_test:

            example_id = example["id"]

            if example_id not in already_assigned_test:
                test.append(example)
                already_assigned_test.add(example_id)

    # Add negative examples
    negative_test_count = max(
        1,
        round(len(negative_examples) * TEST_SIZE)
    )

    random.shuffle(negative_examples)

    negative_test = negative_examples[:negative_test_count]

    test = [
        example
        for example in test
        if example["categories"]
    ]

    test.extend(negative_test)

    test_ids = [
        example["id"]
        for example in test
    ]

    return test_ids


def main():

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    test_ids = create_fixed_test_set(dataset)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(
            test_ids,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Fixed benchmark examples: {len(test_ids)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()