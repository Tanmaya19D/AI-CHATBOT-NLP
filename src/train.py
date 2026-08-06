import json
from collections import Counter
from pathlib import Path

import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

from src.preprocess import preprocess


# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INTENTS_PATH = BASE_DIR / "data" / "intents.json"
MODELS_DIR = BASE_DIR / "models"

MODEL_PATH = MODELS_DIR / "chatbot_model.pkl"
VECTORIZER_PATH = MODELS_DIR / "vectorizer.pkl"
ENCODER_PATH = MODELS_DIR / "label_encoder.pkl"


# ==========================================================
# VALIDATION
# ==========================================================

def validate_intents(data: dict) -> None:
    """
    Validate the structure of intents.json before training.
    """

    if "intents" not in data:
        raise ValueError(
            "intents.json must contain an 'intents' list."
        )

    if not isinstance(data["intents"], list):
        raise ValueError(
            "'intents' must be a list."
        )

    tags = []

    for index, intent in enumerate(data["intents"], start=1):

        if not isinstance(intent, dict):
            raise ValueError(
                f"Intent number {index} must be an object."
            )

        tag = intent.get("tag")
        patterns = intent.get("patterns")
        responses = intent.get("responses")

        if not tag:
            raise ValueError(
                f"Intent number {index} has no tag."
            )

        if not isinstance(patterns, list) or not patterns:
            raise ValueError(
                f"Intent '{tag}' has no patterns."
            )

        if not isinstance(responses, list) or not responses:
            raise ValueError(
                f"Intent '{tag}' has no responses."
            )

        tags.append(tag)

    duplicate_tags = [
        tag
        for tag, count in Counter(tags).items()
        if count > 1
    ]

    if duplicate_tags:
        raise ValueError(
            f"Duplicate intent tags found: {duplicate_tags}"
        )


# ==========================================================
# MODEL TRAINING
# ==========================================================

def train_model() -> None:

    with open(
        INTENTS_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    validate_intents(data)

    texts = []
    labels = []

    pattern_counts = Counter()

    for intent in data["intents"]:

        tag = intent["tag"]

        # Avoid duplicate patterns within the same intent
        unique_patterns = set()

        for pattern in intent["patterns"]:

            cleaned_pattern = preprocess(pattern)

            if not cleaned_pattern:
                continue

            if cleaned_pattern in unique_patterns:
                continue

            texts.append(cleaned_pattern)
            labels.append(tag)

            unique_patterns.add(cleaned_pattern)
            pattern_counts[tag] += 1

    if not texts:
        raise ValueError(
            "No valid training patterns were found."
        )

    # Unigrams and bigrams improve short-text classification
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        lowercase=False,
        sublinear_tf=True,
        strip_accents="unicode"
    )

    X = vectorizer.fit_transform(texts)

    encoder = LabelEncoder()
    y = encoder.fit_transform(labels)

    model = LogisticRegression(
        max_iter=3000,
        class_weight="balanced",
        random_state=42,
        C=3.0
    )

    model.fit(X, y)

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    joblib.dump(
        vectorizer,
        VECTORIZER_PATH
    )

    joblib.dump(
        encoder,
        ENCODER_PATH
    )

    print("=" * 60)
    print("Model trained successfully!")
    print(f"Training patterns: {len(texts)}")
    print(f"Number of intents: {len(encoder.classes_)}")
    print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")
    print("=" * 60)

    print("\nPatterns per intent:")

    for tag in sorted(pattern_counts):
        print(f"{tag}: {pattern_counts[tag]}")


if __name__ == "__main__":
    train_model()