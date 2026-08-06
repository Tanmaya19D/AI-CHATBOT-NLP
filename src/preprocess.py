import re


def preprocess(text: str) -> str:
    """
    Clean user text for training and prediction.

    This version does not require downloaded NLTK datasets,
    making it safer for Render deployment.
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
        "arent": "are not"
    }

    for old_text, new_text in contractions.items():
        text = text.replace(old_text, new_text)

    # Keep letters, numbers and spaces only
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove repeated spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text