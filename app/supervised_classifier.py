import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier


class SupervisedMultilabelClassifier:
    """
    Multilabel classifier operating on multilingual sentence embeddings.

    The embedding model is kept separate from the classifier so that
    the same multilingual encoder can later be replaced or fine-tuned.
    """

    def __init__(self):
        self.classifier = OneVsRestClassifier(
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            )
        )

        self.categories = None

    def fit(self, embeddings, labels, categories):
        """
        Train the One-vs-Rest classifier.

        embeddings:
            numpy array of shape (n_samples, embedding_dim)

        labels:
            binary multilabel matrix of shape
            (n_samples, n_categories)

        categories:
            ordered list of category names
        """

        self.categories = categories

        self.classifier.fit(
            embeddings,
            labels,
        )

    def predict_proba(self, embeddings):
        """
        Return probability estimates for every category.
        """

        return self.classifier.predict_proba(
            embeddings
        )

    def predict(
        self,
        embeddings,
        threshold=0.5,
    ):
        """
        Convert probabilities into multilabel predictions.
        """

        probabilities = self.predict_proba(
            embeddings
        )

        return (
            probabilities >= threshold
        ).astype(int)