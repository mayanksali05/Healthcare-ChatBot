from flask import Blueprint, request, jsonify
import ollama

from rag.retriever import retrieve_context

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json()

        user_message = data.get("message", "")

        # Retrieve relevant context
        retrieval_result = retrieve_context(user_message)

        retrieved_context = retrieval_result["context"]

        sources = retrieval_result["sources"]

        # Create grounded prompt
        prompt = f"""
        You are a healthcare education assistant.

        STRICT RULES:
        - Use ONLY the provided context.
        - Do NOT add outside knowledge.
        - Do NOT make assumptions.
        - If information is missing, say:
        "I do not have enough trusted information."
        - Keep answers short and factual.

Healthcare Context:
{retrieved_context}

User Question:
{user_message}
"""

        response = ollama.chat(
            model="phi3:mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "num_predict": 120,
                "temperature": 0.3
            }
        )

        bot_reply = response["message"]["content"]

        return jsonify({
            "reply": bot_reply,
            "sources": sources
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500