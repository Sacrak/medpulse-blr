import json
from pathlib import Path

import torch
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "nlp"
    / "emergency_examples.json"
)


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def load_model():
    return SentenceTransformer(MODEL_NAME)


def build_category_examples(dataset):
    category_examples = {}

    for example in dataset:
        for category in example["categories"]:
            category_examples.setdefault(category, []).append(
                example["text"]
            )

    return category_examples


# ---------------------------------------------------------
# OLD BASELINE
# ---------------------------------------------------------

def build_category_embeddings(model, category_examples):
    category_embeddings = {}

    for category, examples in category_examples.items():
        embeddings = model.encode(
            examples,
            convert_to_tensor=True
        )

        category_embeddings[category] = embeddings

    return category_embeddings


def classify_text(model, category_embeddings, text):
    query_embedding = model.encode(
        text,
        convert_to_tensor=True
    )

    results = []

    for category, embeddings in category_embeddings.items():
        similarities = model.similarity(
            query_embedding,
            embeddings
        )

        best_score = similarities.max().item()

        results.append({
            "category": category,
            "score": best_score
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results


# ---------------------------------------------------------
# NEW CENTROID APPROACH
# ---------------------------------------------------------

def build_category_centroids(model, category_examples):
    category_centroids = {}

    for category, examples in category_examples.items():

        embeddings = model.encode(
            examples,
            convert_to_tensor=True
        )

        # Average all example embeddings
        centroid = embeddings.mean(dim=0)

        # Normalize the centroid
        centroid = torch.nn.functional.normalize(
            centroid,
            p=2,
            dim=0
        )

        category_centroids[category] = centroid

    return category_centroids


def classify_text_centroid(
    model,
    category_centroids,
    text
):
    query_embedding = model.encode(
        text,
        convert_to_tensor=True
    )

    # Normalize query embedding
    query_embedding = torch.nn.functional.normalize(
        query_embedding,
        p=2,
        dim=0
    )

    results = []

    for category, centroid in category_centroids.items():

        score = torch.nn.functional.cosine_similarity(
            query_embedding,
            centroid,
            dim=0
        ).item()

        results.append({
            "category": category,
            "score": score
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    dataset = load_dataset()
    model = load_model()

    category_examples = build_category_examples(
        dataset
    )

    category_centroids = build_category_centroids(
        model,
        category_examples
    )

    test_text = (
        "I fell from my bike and my leg is bleeding badly"
    )

    results = classify_text_centroid(
        model,
        category_centroids,
        test_text
    )

    print("\nInput:")
    print(test_text)

    print("\nCentroid similarity scores:")

    for result in results:
        print(
            f"{result['category']:30s}"
            f"{result['score']:.4f}"
        )