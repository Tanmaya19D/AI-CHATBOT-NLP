import re
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download("stopwords")
nltk.download("wordnet")

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))


import re

def preprocess(text):

    text = text.lower()

    text = text.replace("i'm", "i am")
    text = text.replace("im", "i am")

    text = re.sub(r"[^a-zA-Z\s]", "", text)

    return text