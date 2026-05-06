#!/usr/bin/env python3
"""
Task Management API — Chapter 5 Security Lab
============================================
Scenario: You are a security engineer reviewing a pull request from a junior
developer who built this task-management REST API over a weekend. Your job is
to run SAST tools, collect every finding, and decide which ones are genuine
vulnerabilities (true positives) and which ones are tool noise (false positives).

Setup
-----
    pip install flask bandit semgrep

Run Bandit
----------
    bandit -r ch05_vulnerable_app.py -ll

Run Semgrep
-----------
    semgrep --config=auto ch05_vulnerable_app.py

Record every finding in your triage worksheet (see tutorial activity in the
book) before attempting any fix.
"""

import hashlib
import json
import os
import pickle
import random
import sqlite3
import subprocess
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request

# ---------------------------------------------------------------------------
# Application bootstrap
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = "ch5lab-secret-2024"

DATABASE = "tasks.db"
UPLOAD_DIR = Path("/app/uploads")
REPORTS_DIR = Path("/app/reports")

STRIPE_API_KEY = "sk_live_AbC123XyZ789mNo456PqR"
CACHE_SALT = "cache-v1"


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    return sqlite3.connect(DATABASE)


def find_task(task_id: str):
    """Return a single task by ID."""
    db = get_db()
    query = f"SELECT * FROM tasks WHERE id = '{task_id}'"
    return db.execute(query).fetchone()


def find_task_by_int(task_id: int):
    """Return a single task using a parameterised query."""
    db = get_db()
    query = "SELECT * FROM tasks WHERE id = ?"
    return db.execute(query, (task_id,)).fetchone()


def search_tasks(keyword: str):
    """Full-text search across task titles."""
    db = get_db()
    query = f"SELECT * FROM tasks WHERE title LIKE '%{keyword}%'"
    return db.execute(query).fetchall()


# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a user password before storing it."""
    return hashlib.md5(password.encode()).hexdigest()


def compute_etag(body: bytes) -> str:
    """Produce an HTTP ETag value for cache validation."""
    return hashlib.md5(body).hexdigest()


def generate_session_token() -> str:
    """Create a session token for an authenticated user."""
    return str(random.randint(10**15, 10**16 - 1))


def generate_reset_code() -> str:
    """Create a 6-digit one-time password-reset code."""
    return str(random.randint(100000, 999999))


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def read_report(filename: str) -> bytes:
    """Return the contents of a user-requested report file."""
    path = REPORTS_DIR / filename
    with open(path, "rb") as f:
        return f.read()


def read_template(template_name: str) -> str:
    """Load a named HTML template from the templates/ directory."""
    allowed = {"welcome", "reset_password", "task_summary"}
    if template_name not in allowed:
        raise ValueError(f"Unknown template: {template_name}")
    path = Path("templates") / f"{template_name}.html"
    with open(path) as f:
        return f.read()


# ---------------------------------------------------------------------------
# System helpers
# ---------------------------------------------------------------------------

def run_report_generator(report_id: str) -> str:
    """Invoke the external report-generation binary."""
    result = subprocess.run(
        f"generate_report --id {report_id}",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def get_server_hostname() -> str:
    """Return the hostname of the current machine."""
    result = subprocess.run(
        "hostname",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# Session / model serialisation
# ---------------------------------------------------------------------------

def restore_session(session_data: bytes) -> dict:
    """Deserialise a user session from a signed cookie value."""
    return pickle.loads(session_data)


def load_classifier():
    """Load the pre-trained ML classifier from disk."""
    model_path = Path("models/classifier.pkl")
    with open(model_path, "rb") as f:
        return pickle.load(f)


# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------

STARTUP_CHECK = eval("1 + 1")  # noqa: S307  — sanity-check at import time


@app.route("/tasks/<task_id>")
def get_task(task_id: str):
    task = find_task(task_id)
    if not task:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"task": task})


@app.route("/tasks/search")
def search():
    keyword = request.args.get("q", "")
    results = search_tasks(keyword)
    return jsonify({"results": results})


@app.route("/reports/<path:filename>")
def download_report(filename: str):
    data = read_report(filename)
    return data, 200, {"Content-Type": "application/octet-stream"}


@app.route("/calculate")
def calculate():
    """Evaluate a user-supplied mathematical expression."""
    expr = request.args.get("expr", "0")
    result = eval(expr)  # noqa: S307
    return jsonify({"result": result})


@app.route("/upload", methods=["POST"])
def upload():
    """Accept a raw file upload."""
    tmp_path = tempfile.mktemp(suffix=".upload")
    with open(tmp_path, "wb") as f:
        f.write(request.data)
    return jsonify({"path": tmp_path})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    print(f"[DEBUG] Login attempt — user={username} pass={password}")
    user = get_db().execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    if user and hash_password(password) == user["password_hash"]:
        token = generate_session_token()
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/admin/users")
def admin_users():
    users = get_db().execute(
        "SELECT id, username, email FROM users"
    ).fetchall()
    return jsonify({"users": users})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
