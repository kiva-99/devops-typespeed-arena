# app/backend/main.py
"""
TypeSpeed Arena Backend
Flask API server for typing speed trainer.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import datetime

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXTS_FILE = os.getenv("TEXTS_FILE", os.path.join(BASE_DIR, "texts.json"))

results = []


def load_texts():
    """Load typing texts from external JSON file."""
    try:
        with open(TEXTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Texts file not found: {TEXTS_FILE}")
        return []
    except json.JSONDecodeError as error:
        print(f"Invalid JSON in texts file: {error}")
        return []


texts = load_texts()


@app.route("/")
def hello():
    return jsonify({
        "status": "ok",
        "message": "TypeSpeed Arena API is running 🚀",
        "timestamp": datetime.datetime.now().isoformat()
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "typespeed-backend",
        "texts_loaded": len(texts),
        "timestamp": datetime.datetime.now().isoformat()
    })


@app.route("/api/texts", methods=["GET"])
def get_texts():
    return jsonify({
        "success": True,
        "count": len(texts),
        "data": texts
    })


@app.route("/api/results", methods=["POST"])
def save_result():
    data = request.get_json()

    if not data or "wpm" not in data or "accuracy" not in data:
        return jsonify({
            "success": False,
            "error": "Missing required fields: wpm, accuracy"
        }), 400

    result = {
        "id": len(results) + 1,
        "username": data.get("username", "guest"),
        "wpm": data["wpm"],
        "accuracy": data["accuracy"],
        "errors": data.get("errors", 0),
        "text_id": data.get("text_id"),
        "timestamp": datetime.datetime.now().isoformat()
    }

    results.append(result)

    return jsonify({
        "success": True,
        "message": "Result saved!",
        "data": result
    }), 201


@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    top_results = sorted(results, key=lambda x: x["wpm"], reverse=True)[:10]

    return jsonify({
        "success": True,
        "count": len(top_results),
        "data": top_results
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    print(f"🚀 Starting TypeSpeed Arena API on port {port}")
    print(f"📚 Loaded texts: {len(texts)} from {TEXTS_FILE}")

    app.run(host="0.0.0.0", port=port, debug=debug)
