from flask import Flask
from flask_cors import CORS

from routes.chat import chat_bp

app = Flask(__name__)
CORS(
    app,
    expose_headers=["X-Sources"]
)

# Register routes
app.register_blueprint(chat_bp)


@app.route("/")
def home():
    return {
        "message": "Healthcare ChatBot Backend Running"
    }


if __name__ == "__main__":
    app.run(debug=True)