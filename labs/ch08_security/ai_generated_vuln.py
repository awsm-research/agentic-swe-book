"""AI-generated examples from Section 8.4: a benign prompt produces vulnerable code.

Example 1 — SQL injection from a "get user task history" prompt.
Example 2 — RCE-prone Flask config from a "make debugging easier" prompt.

Both `db` and `app` are intentionally undefined; these snippets exist for
illustration of the AI-generated patterns described in Chapter 8 §8.4.
"""


# --- Example 1: typical AI-generated SQL response (CWE-89) ---

def get_task_history(username: str) -> list[dict]:
    query = f"SELECT * FROM tasks WHERE assigned_to = '{username}'"
    return db.execute(query).fetchall()


# Corrected version:
def get_task_history_safe(username: str) -> list[dict]:
    return db.execute(
        "SELECT * FROM tasks WHERE assigned_to = %s", (username,)
    ).fetchall()


# --- Example 2: typical AI-generated Flask "easier debugging" response ---
# Vulnerable: debug=True + host=0.0.0.0 → unauthenticated RCE
#
#     if __name__ == "__main__":
#         app.run(debug=True, host="0.0.0.0", port=5000)
#
# Safe: gate debug on env var, bind to localhost
#
#     import os
#     if __name__ == "__main__":
#         debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
#         app.run(debug=debug, host="127.0.0.1", port=5000)
