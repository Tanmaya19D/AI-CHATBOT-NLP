import os
from functools import wraps

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from markupsafe import escape

from src.auth import (
    create_users_table,
    login_user,
    register_user
)

from src.chatbot import get_response

from src.database import (
    create_database,
    get_all_chats,
    get_chat_count,
    get_recent_chats,
    get_sentiment_count,
    save_chat
)

from src.sentiment import get_sentiment


app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "development-secret-key-change-this"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.environ.get("RENDER") == "true"
)


create_database()
create_users_table()


def login_required(route_function):

    @wraps(route_function)
    def protected_route(*args, **kwargs):

        if "user_id" not in session:
            return redirect(
                url_for("login")
            )

        return route_function(
            *args,
            **kwargs
        )

    return protected_route


@app.route("/register", methods=["GET", "POST"])
def register():

    if "user_id" in session:
        return redirect(
            url_for("home")
        )

    error = None
    success_message = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not username:
            error = "Username is required."

        elif len(username) < 3:
            error = (
                "Username must contain at least "
                "3 characters."
            )

        elif not email:
            error = "Email is required."

        elif "@" not in email or "." not in email:
            error = "Enter a valid email address."

        elif len(password) < 6:
            error = (
                "Password must contain at least "
                "6 characters."
            )

        elif password != confirm_password:
            error = "Passwords do not match."

        else:
            registered = register_user(
                username,
                email,
                password
            )

            if registered:
                success_message = (
                    "Account created successfully. "
                    "You can now log in."
                )

            else:
                error = (
                    "That username or email "
                    "already exists."
                )

    return render_template(
        "register.html",
        error=error,
        success_message=success_message
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(
            url_for("home")
        )

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:
            error = (
                "Username and password "
                "are required."
            )

        else:
            user_id = login_user(
                username,
                password
            )

            if user_id is not None:
                session.clear()

                session["user_id"] = int(user_id)
                session["username"] = username

                return redirect(
                    url_for("home")
                )

            error = (
                "Invalid username or password. "
                "Create a new account first."
            )

    return render_template(
        "login.html",
        error=error
    )


@app.route("/logout")
@login_required
def logout():
    session.clear()

    return redirect(
        url_for("login")
    )


@app.route("/")
@login_required
def home():
    return render_template(
        "index.html",
        username=session.get("username")
    )


@app.route("/chat", methods=["POST"])
@login_required
def chat():

    message = request.form.get(
        "message",
        ""
    ).strip()

    if not message:
        return "Please enter a message.", 400

    result = get_response(message)

    sentiment = get_sentiment(message)

    response_text = escape(
        result.get(
            "response",
            "No response was generated."
        )
    )

    intent = escape(
        result.get(
            "intent",
            "unknown"
        )
    )

    confidence = float(
        result.get(
            "confidence",
            0.0
        )
    )

    source_title = escape(
        result.get(
            "source_title",
            "Local intents dataset"
        )
    )

    source_url = str(
        result.get(
            "source_url",
            ""
        )
    ).strip()

    source_type = escape(
        result.get(
            "source_type",
            "local_dataset"
        )
    )

    if source_url.startswith(
        ("https://", "http://")
    ):
        safe_source_url = escape(
            source_url
        )

        source_display = (
            f'<a href="{safe_source_url}" '
            f'target="_blank" '
            f'rel="noopener noreferrer">'
            f'{source_title}'
            f'</a>'
        )

    else:
        source_display = str(
            source_title
        )

    final_response = (
        '<div class="bot-answer">'
        f'{response_text}'
        '</div>'

        '<div class="response-details">'
        f'<strong>Intent:</strong> '
        f'{intent}<br>'

        f'<strong>Sentiment:</strong> '
        f'{escape(sentiment)}<br>'

        f'<strong>Confidence:</strong> '
        f'{confidence:.2f}<br>'

        f'<strong>Source:</strong> '
        f'{source_display}<br>'

        f'<strong>Source type:</strong> '
        f'{source_type}'
        '</div>'
    )

    save_chat(
        message,
        final_response,
        sentiment
    )

    return final_response


@app.route("/history")
@login_required
def history():

    chats = get_all_chats()

    return render_template(
        "history.html",
        chats=chats,
        username=session.get("username")
    )


@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html",

        total_chats=get_chat_count(),

        positive=get_sentiment_count(
            "Positive"
        ),

        neutral=get_sentiment_count(
            "Neutral"
        ),

        negative=get_sentiment_count(
            "Negative"
        ),

        recent_chats=get_recent_chats(),

        username=session.get("username")
    )


@app.route("/health")
def health():
    return {
        "status": "ok",
        "message": "AI Chatbot is running"
    }


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        ),
        debug=False
    )