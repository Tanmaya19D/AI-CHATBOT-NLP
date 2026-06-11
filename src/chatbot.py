import json
import random
import joblib

from src.preprocess import preprocess


# Load trained files
model = joblib.load("models/chatbot_model.pkl")
vectorizer = joblib.load("models/vectorizer.pkl")
encoder = joblib.load("models/label_encoder.pkl")

# Load intents
with open("data/intents.json", "r") as file:
    intents = json.load(file)


def get_response(message):

    processed_message = preprocess(message)

    X = vectorizer.transform([processed_message])

    probs = model.predict_proba(X)
    confidence = max(probs[0])

    prediction = model.predict(X)
    tag = encoder.inverse_transform(prediction)[0]

    print("=" * 40)
    print("User:", processed_message)
    print("Predicted Tag:", tag)
    print("Confidence:", confidence)
    print("=" * 40)

    # If confidence is low, use Gemini
    if confidence < 0.35:
        return (
        "I'm not sure I understand that. Can you rephrase it?",
        confidence
    )

    # Otherwise use intent responses
    for intent in intents["intents"]:

        if intent["tag"] == tag:

            return (
                random.choice(intent["responses"]),
                confidence
            )

    return (
        "Sorry, I don't understand that.",
        confidence
    )