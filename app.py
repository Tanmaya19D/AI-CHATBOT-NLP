from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)

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

from src.auth import (
    create_users_table,
    register_user,
    login_user
)

app = Flask(__name__)

app.secret_key = "chatbot_secret_key_2026"

create_database()
create_users_table()


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        success = register_user(
            username,
            email,
            password
        )

        if success:
            return redirect("/login")

        return "Username or Email already exists"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user_id = login_user(
            username,
            password
        )

        if user_id:

            session["user_id"] = user_id
            session["username"] = username

            return redirect("/")

        return "Invalid Username or Password"

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "index.html"
    )


@app.route("/chat", methods=["POST"])
def chat():

    if "user_id" not in session:
        return "Please login first"

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

    if "user_id" not in session:
        return redirect("/login")

    chats = get_all_chats()

    return render_template(
        "history.html",
        chats=chats
    )


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

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