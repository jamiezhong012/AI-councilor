import os
from flask import Flask, request, redirect
from openai import OpenAI

"""ai councilor.py

Reorganized: imports -> config/constants -> helpers -> routes -> entrypoint.
Behavior preserved: routes and response handling remain the same.
"""

# --- Configuration / Constants -------------------------------------------------
# NOTE: original code contained a hardcoded API key. Keeping it here to preserve
# behavior exactly as requested when reorganizing. Consider switching to an
# environment variable for safety when ready.
OPENAI_API_KEY = "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"

FILE_AI = "ai councilor.html"
FILE_ABOUT = "about.html"
FILE_ANSWER = "answer.html"
FILE_MATH = "math.html"
FILE_NOTES = "notes.html"

# --- Client / App Init --------------------------------------------------------
client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)


# --- Helpers ------------------------------------------------------------------
def read_file(path):
    """Return file contents, ignoring minor encoding errors."""
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text_from_response(response):
    """Robustly extract assistant text from different SDK response shapes."""
    try:
        if hasattr(response, "choices") and response.choices:
            choice = response.choices[0]
            if isinstance(choice, dict):
                msg = choice.get("message") or {}
                return msg.get("content") or choice.get("text") or str(choice)
            else:
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    return choice.message.content
                elif hasattr(choice, "text"):
                    return choice.text
                else:
                    return str(choice)
        return str(response)
    except Exception:
        return "Sorry, I couldn't generate an answer right now."


# --- Routes -------------------------------------------------------------------
@app.route("/")
def home():
    """Serve the AI counselor main page."""
    # Serve the AI counselor page at root
    return read_file(FILE_AI)


@app.route("/about")
def about():
    """Serve the about page."""
    return read_file(FILE_ABOUT)


@app.route('/about.html')
def about_html():
    """Legacy path: serve the same about page when /about.html is requested."""
    return read_file(FILE_ABOUT)


@app.route('/style.css')
def style_css():
    """Serve the stylesheet file to avoid 404s when the browser requests /style.css."""
    try:
        return read_file('style.css')
    except FileNotFoundError:
        return "", 404


@app.route("/ask")
def ask():
    """Handle a question query and return the rendered answer page."""
    question = request.args.get("question", "")

    html = read_file(FILE_ANSWER)
    html = html.replace("QUESTION_HERE", question)

    # Safe, non-abusive system prompt (kept equivalent to original wording)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional college counselor. Provide concise, respectful, and actionable advice "
                    "tailored to the user's question. Avoid insults, harassment, and inappropriate content."
                ),
            },
            {"role": "user", "content": question},
        ],
        max_tokens=800,
    )

    answer = extract_text_from_response(response)
    html = html.replace("ANSWER_HERE", answer)
    return html


@app.route('/math')
def math_page():
    """Serve the math tools page."""
    return read_file(FILE_MATH)


@app.route('/math.html')
def math_html():
    """Legacy path: serve the math page when /math.html is requested."""
    return read_file(FILE_MATH)


@app.route('/notes')
def notes_page():
    """Serve the notes page."""
    return read_file(FILE_NOTES)


@app.route('/notes.html')
def notes_html():
    """Legacy path: serve the notes page when /notes.html is requested."""
    return read_file(FILE_NOTES)


# --- Entrypoint ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5500)
