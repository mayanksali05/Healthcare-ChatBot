from flask import Blueprint, request, jsonify
import ollama

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        user_message = data.get("message", "")

        response = ollama.chat(
            model="phi3:mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI health education assistant. "
                        "Provide general wellness and nutrition information only. "
                        "Do not diagnose diseases or prescribe medications."
                    )
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        bot_reply = response["message"]["content"]

        return jsonify({
            "reply": bot_reply
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500