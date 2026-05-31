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
import logging
import sys
import uuid

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXTS_FILE = os.getenv("TEXTS_FILE", os.path.join(BASE_DIR, "texts.json"))
LOG_DIR = os.getenv("LOG_DIR", os.path.join(BASE_DIR, "logs"))
LOG_FILE = os.getenv("LOG_FILE", os.path.join(LOG_DIR, "typespeed-backend.log"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

results = []


class JsonFormatter(logging.Formatter):
    """Format logs as JSON for easier parsing by ELK/Loki."""

    def format(self, record):
        log_record = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "typespeed-backend",
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "event"):
            log_record["event"] = record.event
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "method"):
            log_record["method"] = record.method
        if hasattr(record, "path"):
            log_record["path"] = record.path
        if hasattr(record, "status_code"):
            log_record["status_code"] = record.status_code
        if hasattr(record, "username"):
            log_record["username"] = record.username
        if hasattr(record, "wpm"):
            log_record["wpm"] = record.wpm
        if hasattr(record, "accuracy"):
            log_record["accuracy"] = record.accuracy
        if hasattr(record, "text_id"):
            log_record["text_id"] = record.text_id
        if hasattr(record, "error"):
            log_record["error"] = record.error

        return json.dumps(log_record, ensure_ascii=False)


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("typespeed")
    logger.setLevel(LOG_LEVEL)
    logger.handlers.clear()

    formatter = JsonFormatter()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


def log_event(level, message, **extra):
    logger.log(level, message, extra=extra)


def load_texts():
    """Load typing texts from external JSON file."""
    try:
        with open(TEXTS_FILE, "r", encoding="utf-8") as file:
            loaded_texts = json.load(file)

        log_event(
            logging.INFO,
            "Texts loaded successfully",
            event="texts_loaded",
            text_id="all",
        )
        return loaded_texts

    except FileNotFoundError:
        log_event(
            logging.ERROR,
            "Texts file not found",
            event="texts_file_not_found",
            error=TEXTS_FILE,
        )
        return []

    except json.JSONDecodeError as error:
        log_event(
            logging.ERROR,
            "Invalid JSON in texts file",
            event="texts_json_invalid",
            error=str(error),
        )
        return []


texts = load_texts()


@app.before_request
def before_request():
    request.request_id = str(uuid.uuid4())


@app.after_request
def after_request(response):
    log_event(
        logging.INFO,
        "HTTP request processed",
        event="http_request",
        request_id=getattr(request, "request_id", None),
        method=request.method,
        path=request.path,
        status_code=response.status_code,
    )
    return response


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
    log_event(
        logging.INFO,
        "Texts requested",
        event="texts_requested",
    )

    return jsonify({
        "success": True,
        "count": len(texts),
        "data": texts
    })


@app.route("/api/results", methods=["POST"])
def save_result():
    data = request.get_json()

    if not data or "wpm" not in data or "accuracy" not in data:
        log_event(
            logging.WARNING,
            "Invalid result payload",
            event="invalid_result_payload",
            request_id=getattr(request, "request_id", None),
            error="Missing required fields: wpm, accuracy",
        )

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

    log_event(
        logging.INFO,
        "Typing result saved",
        event="result_saved",
        request_id=getattr(request, "request_id", None),
        username=result["username"],
        wpm=result["wpm"],
        accuracy=result["accuracy"],
        text_id=result["text_id"],
    )

    return jsonify({
        "success": True,
        "message": "Result saved!",
        "data": result
    }), 201


@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    top_results = sorted(results, key=lambda x: x["wpm"], reverse=True)[:10]

    log_event(
        logging.INFO,
        "Leaderboard requested",
        event="leaderboard_requested",
    )

    return jsonify({
        "success": True,
        "count": len(top_results),
        "data": top_results
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    log_event(
        logging.INFO,
        "Starting TypeSpeed Arena API",
        event="app_start",
    )

    app.run(host="0.0.0.0", port=port, debug=debug)
