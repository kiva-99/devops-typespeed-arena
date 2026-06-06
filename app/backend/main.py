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
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXTS_FILE = os.getenv("TEXTS_FILE", os.path.join(BASE_DIR, "texts.json"))
LOG_DIR = os.getenv("LOG_DIR", os.path.join(BASE_DIR, "logs"))
LOG_FILE = os.getenv("LOG_FILE", os.path.join(LOG_DIR, "typespeed-backend.log"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

DATABASE_URL = os.getenv("DATABASE_URL")
results_memory_fallback = []


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

        for field in [
            "event",
            "request_id",
            "method",
            "path",
            "status_code",
            "username",
            "wpm",
            "accuracy",
            "text_id",
            "error",
        ]:
            if hasattr(record, field):
                log_record[field] = getattr(record, field)

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


def get_db_connection():
    if not DATABASE_URL:
        return None

    return psycopg2.connect(DATABASE_URL)


def is_database_enabled():
    return bool(DATABASE_URL)


def init_db():
    if not is_database_enabled():
        log_event(
            logging.WARNING,
            "DATABASE_URL is not set, using in-memory fallback",
            event="database_disabled",
        )
        return

    create_results_table_sql = """
    CREATE TABLE IF NOT EXISTS results (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) NOT NULL,
        wpm INTEGER NOT NULL,
        accuracy NUMERIC(5,2) NOT NULL,
        errors INTEGER NOT NULL DEFAULT 0,
        text_id VARCHAR(100),
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_results_table_sql)
            conn.commit()

        log_event(
            logging.INFO,
            "Database initialized successfully",
            event="database_initialized",
        )

    except Exception as error:
        log_event(
            logging.ERROR,
            "Database initialization failed",
            event="database_initialization_failed",
            error=str(error),
        )


def check_database():
    if not is_database_enabled():
        return "disabled"

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
        return "connected"

    except Exception as error:
        log_event(
            logging.ERROR,
            "Database healthcheck failed",
            event="database_healthcheck_failed",
            error=str(error),
        )
        return "error"


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
init_db()


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
    database_status = check_database()

    return jsonify({
        "status": "healthy",
        "service": "typespeed-backend",
        "database": database_status,
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

    username = data.get("username", "guest")
    wpm = int(data["wpm"])
    accuracy = float(data["accuracy"])
    errors = int(data.get("errors", 0))
    text_id = data.get("text_id")

    if is_database_enabled():
        try:
            insert_sql = """
            INSERT INTO results (username, wpm, accuracy, errors, text_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, username, wpm, accuracy, errors, text_id, created_at;
            """

            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(insert_sql, (username, wpm, accuracy, errors, text_id))
                    saved_result = cursor.fetchone()
                conn.commit()

            result = {
                "id": saved_result["id"],
                "username": saved_result["username"],
                "wpm": saved_result["wpm"],
                "accuracy": float(saved_result["accuracy"]),
                "errors": saved_result["errors"],
                "text_id": saved_result["text_id"],
                "timestamp": saved_result["created_at"].isoformat(),
            }

        except Exception as error:
            log_event(
                logging.ERROR,
                "Failed to save result to database",
                event="result_save_failed",
                request_id=getattr(request, "request_id", None),
                username=username,
                wpm=wpm,
                accuracy=accuracy,
                text_id=text_id,
                error=str(error),
            )

            return jsonify({
                "success": False,
                "error": "Failed to save result"
            }), 500

    else:
        result = {
            "id": len(results_memory_fallback) + 1,
            "username": username,
            "wpm": wpm,
            "accuracy": accuracy,
            "errors": errors,
            "text_id": text_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
        results_memory_fallback.append(result)

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
    if is_database_enabled():
        try:
            select_sql = """
            SELECT id, username, wpm, accuracy, errors, text_id, created_at
            FROM results
            ORDER BY wpm DESC, accuracy DESC, created_at ASC
            LIMIT 10;
            """

            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(select_sql)
                    rows = cursor.fetchall()

            top_results = [
                {
                    "id": row["id"],
                    "username": row["username"],
                    "wpm": row["wpm"],
                    "accuracy": float(row["accuracy"]),
                    "errors": row["errors"],
                    "text_id": row["text_id"],
                    "timestamp": row["created_at"].isoformat(),
                }
                for row in rows
            ]

        except Exception as error:
            log_event(
                logging.ERROR,
                "Failed to load leaderboard from database",
                event="leaderboard_load_failed",
                error=str(error),
            )

            return jsonify({
                "success": False,
                "error": "Failed to load leaderboard"
            }), 500

    else:
        top_results = sorted(
            results_memory_fallback,
            key=lambda x: (x["wpm"], x["accuracy"]),
            reverse=True
        )[:10]

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
