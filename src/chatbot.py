import json
import random
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from src.preprocess import preprocess


# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "chatbot_model.pkl"
VECTORIZER_PATH = BASE_DIR / "models" / "vectorizer.pkl"
ENCODER_PATH = BASE_DIR / "models" / "label_encoder.pkl"
INTENTS_PATH = BASE_DIR / "data" / "intents.json"


# ==========================================================
# LOAD MODEL FILES
# ==========================================================

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)
encoder = joblib.load(ENCODER_PATH)

with open(
    INTENTS_PATH,
    "r",
    encoding="utf-8"
) as file:
    intents_data = json.load(file)


CONFIDENCE_THRESHOLD = 0.25


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def get_intent_by_tag(tag: str) -> dict[str, Any] | None:

    for intent in intents_data["intents"]:

        if intent["tag"] == tag:
            return intent

    return None


def create_fallback_response(
    confidence: float
) -> dict[str, Any]:

    return {
        "response": (
            "I'm not sure I understand that. "
            "Please rephrase your question."
        ),
        "confidence": confidence,
        "intent": "unknown",
        "source_type": "fallback",
        "source_title": "Fallback response",
        "source_url": ""
    }


# ==========================================================
# CHATBOT RESPONSE
# ==========================================================

def get_response(message: str) -> dict[str, Any]:

    processed_message = preprocess(message)

    if not processed_message:

        return {
            "response": "Please enter a valid message.",
            "confidence": 0.0,
            "intent": "invalid_input",
            "source_type": "system",
            "source_title": "Input validation",
            "source_url": ""
        }

    features = vectorizer.transform(
        [processed_message]
    )

    probabilities = model.predict_proba(
        features
    )[0]

    predicted_index = int(
        np.argmax(probabilities)
    )

    confidence = float(
        probabilities[predicted_index]
    )

    predicted_tag = encoder.inverse_transform(
        [predicted_index]
    )[0]

    print("=" * 60)
    print("Original message:", message)
    print("Processed message:", processed_message)
    print("Predicted intent:", predicted_tag)
    print("Confidence:", round(confidence, 4))
    print("=" * 60)

    if confidence < CONFIDENCE_THRESHOLD:
        return create_fallback_response(confidence)

    intent = get_intent_by_tag(predicted_tag)

    if intent is None:
        return create_fallback_response(confidence)

    responses = intent.get("responses", [])

    if not responses:
        return create_fallback_response(confidence)

    sources = intent.get("sources", [])

    if sources:

        source = sources[0]

        source_title = source.get(
            "title",
            "External reference"
        )

        source_url = source.get(
            "url",
            ""
        )

        source_type = "reference"

    else:

        source_title = "Local intents dataset"
        source_url = ""
        source_type = "local_dataset"

    return {
        "response": random.choice(responses),
        "confidence": confidence,
        "intent": predicted_tag,
        "source_type": source_type,
        "source_title": source_title,
        "source_url": source_url
    }