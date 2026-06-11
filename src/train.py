import json
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

from src.preprocess import preprocess

with open("data/intents.json", "r") as file:
    data = json.load(file)

texts = []
labels = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        texts.append(preprocess(pattern))
        labels.append(intent["tag"])
        pattern = preprocess(pattern)

        texts.append(pattern)
        labels.append(intent["tag"])

vectorizer = TfidfVectorizer(
    ngram_range=(1, 2)
)

X = vectorizer.fit_transform(texts)

encoder = LabelEncoder()
y = encoder.fit_transform(labels)

model = LogisticRegression(
    max_iter=1000
)

model.fit(X, y)

joblib.dump(model, "models/chatbot_model.pkl")
joblib.dump(vectorizer, "models/vectorizer.pkl")
joblib.dump(encoder, "models/label_encoder.pkl")

print("Model trained successfully!")