import re

from nltk.stem import WordNetLemmatizer


lemmatizer = WordNetLemmatizer()


def preprocess(text: str) -> str:
    """
    Clean and normalize text before training or prediction.
    The same function must be used in train.py and chatbot.py.
    """

    if not isinstance(text, str):
        return ""

    text = text.lower().strip()

    contractions = {
        "i'm": "i am",
        "im": "i am",
        "what's": "what is",
        "whats": "what is",
        "can't": "cannot",
        "cant": "cannot",
        "don't": "do not",
        "dont": "do not",
        "doesn't": "does not",
        "doesnt": "does not",
        "won't": "will not",
        "wont": "will not",
        "isn't": "is not",
        "isnt": "is not",
        "aren't": "are not",
        "arent": "are not",
        "couldn't": "could not",
        "couldnt": "could not",
        "wouldn't": "would not",
        "wouldnt": "would not"
    }

    for old_text, new_text in contractions.items():
        text = text.replace(old_text, new_text)

    # Keep letters, numbers and spaces only
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove repeated spaces
    text = re.sub(r"\s+", " ", text).strip()

    words = text.split()

    lemmatized_words = [
        lemmatizer.lemmatize(word)
        for word in words
    ]

    return " ".join(lemmatized_words)