from flask import Blueprint, request, jsonify
import ollama
import json 

from rag.retriever import retrieve_context

from utils.memory import (
    add_message,
    get_recent_messages
)
from safety.query_classifier import classify_query
from flask import Response

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json()

        user_message = data.get("message", "")
        add_message("user", user_message)
        query_type = classify_query(user_message)

        # Emergency query handling
        if query_type == "emergency":

            return jsonify({
                "reply": (
                    "This may be a medical emergency. "
                    "Please contact emergency services "
                    "or a licensed healthcare professional immediately."
                ),
                "sources": []
            })


        # Diagnosis prevention
        if query_type == "diagnosis":

            return jsonify({
                "reply": (
                    "I cannot diagnose medical conditions. "
                    "Please consult a licensed healthcare professional."
                ),
                "sources": []
            })


        # Medication safety
        if query_type == "medication":

            return jsonify({
                "reply": (
                    "I cannot provide medication dosage advice. "
                    "Please consult a doctor or pharmacist."
                ),
                "sources": []
            })

        # Retrieve relevant context
        retrieval_result = retrieve_context(user_message)

        retrieved_context = retrieval_result["context"]

        sources = retrieval_result["sources"]

        # No relevant context found
        if not retrieved_context.strip():

            return jsonify({
                "reply": "I do not have enough trusted information.",
                "sources": []
            })
        
        recent_messages = get_recent_messages()

        conversation_context = ""

        for msg in recent_messages:

            conversation_context += (
                f"{msg['role']}: {msg['content']}\n"
            )

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

        FORMAT RULES:
        - Keep response concise.
        - Use simple language.
        - Use bullet points when appropriate.
        - Structure response clearly.

        CONVERSATION HISTORY:
        {conversation_context}

        Healthcare Context:
        {retrieved_context}

        User Question:
        {user_message}

        ANSWER FORMAT:

        ## Summary
        Short explanation.

        ## Key Points
        - Point 1
        - Point 2
        - Point 3

        ## Important Note
        Short healthcare caution if relevant.
        """

        def generate_stream():

            stream = ollama.chat(
                model="phi3:mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                stream=True,
                options={
                    "num_predict": 120,
                    "temperature": 0.3
                }
            )

            full_response = ""

            for chunk in stream:

                content = chunk["message"]["content"]

                full_response += content

                yield content

            add_message("assistant", full_response)


        response = Response(
            generate_stream(),
            content_type="text/plain"
        )

        response.headers["X-Sources"] = json.dumps(sources)

        return response

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500