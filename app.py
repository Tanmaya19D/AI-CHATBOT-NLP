from flask import Flask, render_template, request

from src.chatbot import get_response
from src.sentiment import get_sentiment

from src.database import (
    create_database,
    save_chat,
    get_all_chats,
    get_chat_count,
    get_sentiment_count,
    get_recent_chats
)

app = Flask(__name__)

create_database()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    message = request.form["message"]

    response, confidence = get_response(message)

    sentiment = get_sentiment(message)

    final_response = (
        f"{response}<br>"
        f"Sentiment: {sentiment}<br>"
        f"Confidence: {confidence:.2f}"
    )

    save_chat(
        message,
        final_response,
        sentiment
    )

    return final_response


@app.route("/history")
def history():

    chats = get_all_chats()

    return render_template(
        "history.html",
        chats=chats
    )


@app.route("/dashboard")
def dashboard():

    recent_chats = get_recent_chats()

    return render_template(
        "dashboard.html",
        total_chats=get_chat_count(),
        positive=get_sentiment_count("Positive"),
        neutral=get_sentiment_count("Neutral"),
        negative=get_sentiment_count("Negative"),
        recent_chats=recent_chats
    )


if __name__ == "__main__":
    app.run(debug=True)