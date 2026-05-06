# example_vulnerable.py
import subprocess
import sqlite3
import pickle
import hashlib


def get_user(username: str):
    conn = sqlite3.connect("users.db")
    # SQL injection: f-string interpolation instead of a parameterised query
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return conn.execute(query).fetchone()


def run_report(report_name: str):
    # Command injection: shell=True with user-controlled input
    subprocess.run(f"generate_report {report_name}", shell=True)


def load_session(data: bytes):
    # Insecure deserialization
    return pickle.loads(data)


def hash_password(password: str) -> str:
    # Weak cryptography: MD5 is not suitable for password hashing
    return hashlib.md5(password.encode()).hexdigest()


API_KEY = "sk-prod-abc123secret"  # Hardcoded credential
