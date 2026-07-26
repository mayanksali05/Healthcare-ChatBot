from flask import Flask
from flask_cors import CORS

from routes.health import health_bp

# The chat blueprint pulls in the whole RAG stack (ollama, chromadb,
# sentence-transformers, torch). Those are not needed to serve /health or
# /health/db, so a missing dependency must not stop the app from starting -
# otherwise the frontend cannot even report its own connection state. Same
# reasoning as the optional pymongo import in db/mongo.py.
try:

    from routes.chat import chat_bp

    CHAT_AVAILABLE = True

except ImportError as error:

    chat_bp = None

    CHAT_IMPORT_ERROR = str(error)

    CHAT_AVAILABLE = False


app = Flask(__name__)
CORS(
    app,
    expose_headers=["X-Sources"]
)

# Register routes
if CHAT_AVAILABLE:

    app.register_blueprint(chat_bp)

app.register_blueprint(health_bp)


if not CHAT_AVAILABLE:

    @app.route("/chat", methods=["POST"])
    def chat_unavailable():
        """Stand-in so the frontend gets a clear 503 rather than a bare 404."""

        return {
            "error": (
                "Chat is unavailable: the RAG dependencies are not installed "
                f"({CHAT_IMPORT_ERROR}). Run: pip install -r requirements.txt"
            ),
            "sources": []
        }, 503


@app.route("/")
def home():
    return {
        "message": "Healthcare ChatBot Backend Running"
    }


if __name__ == "__main__":
    app.run(debug=True)