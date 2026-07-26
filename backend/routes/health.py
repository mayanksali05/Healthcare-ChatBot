from flask import Blueprint, jsonify

from db.mongo import server_info


health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "service": "healthcare-chatbot-backend"
    })


@health_bp.route("/health/db", methods=["GET"])
def health_db():
    """Report MongoDB connectivity.

    Returns 503 when the database is unreachable so the frontend can show a
    disconnected state. The URI is redacted before it leaves the process.
    """

    status = server_info()

    return jsonify(status), 200 if status["connected"] else 503
