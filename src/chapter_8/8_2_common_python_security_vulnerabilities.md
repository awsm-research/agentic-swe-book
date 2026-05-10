## 8.2 Common Python Security Vulnerabilities

Five vulnerability classes recur consistently in Python codebases — and appear with measurable frequency in the code that AI assistants generate for them.

### 8.2.1 SQL Injection (CWE-89)

SQL injection occurs when untrusted input is incorporated directly into a SQL query, allowing attackers to alter the query's logic.

```python
# VULNERABLE: String concatenation in SQL
def get_user_by_name_bad(name: str) -> dict | None:
    query = f"SELECT * FROM users WHERE name = '{name}'"
    # If name = "'; DROP TABLE users; --"
    # Query becomes: SELECT * FROM users WHERE name = ''; DROP TABLE users; --'
    return db.execute(query).fetchone()


# SAFE: Parameterised query
def get_user_by_name(name: str) -> dict | None:
    query = "SELECT * FROM users WHERE name = %s"
    return db.execute(query, (name,)).fetchone()
```

**Rule**: Never concatenate user input into a SQL string. Always use parameterised queries or an ORM.

### 8.2.2 Command Injection (CWE-78)

Command injection occurs when user input is passed to a shell command.

```python
import subprocess

# VULNERABLE: Shell=True with user input
def run_analysis_bad(filename: str) -> str:
    result = subprocess.run(
        f"analyze_tool {filename}",
        shell=True,  # DANGEROUS with user input
        capture_output=True,
        text=True,
    )
    return result.stdout


# SAFE: Shell=False with argument list
def run_analysis(filename: str) -> str:
    # Validate filename first
    if not filename.replace("_", "").replace("-", "").replace(".", "").isalnum():
        raise ValueError(f"Invalid filename: {filename}")

    result = subprocess.run(
        ["analyze_tool", filename],  # List form, no shell interpretation
        shell=False,
        capture_output=True,
        text=True,
    )
    return result.stdout
```

**Rule**: Never use `shell=True` with user-controlled input. Use a list of arguments instead.

### 8.2.3 Path Traversal (CWE-22)

Path traversal allows attackers to access files outside the intended directory by using `../` sequences.

```python
import os
from pathlib import Path

UPLOAD_DIR = Path("/app/uploads")

# VULNERABLE: Direct path construction
def read_upload_bad(filename: str) -> bytes:
    path = UPLOAD_DIR / filename  # filename = "../../etc/passwd" would escape!
    with open(path, "rb") as f:
        return f.read()


# SAFE: Resolve and verify the path stays within the intended directory
def read_upload(filename: str) -> bytes:
    requested_path = (UPLOAD_DIR / filename).resolve()

    # is_relative_to checks path hierarchy, not string prefix, avoiding the
    # prefix-collision bug where /app/uploads_secret passes a startswith check
    if not requested_path.is_relative_to(UPLOAD_DIR.resolve()):
        raise PermissionError(f"Access denied: {filename}")

    with open(requested_path, "rb") as f:
        return f.read()
```

### 8.2.4 Insecure Deserialization (CWE-502)

Python's `pickle` module can execute arbitrary code when deserialising untrusted data.

```python
import pickle
import json

# VULNERABLE: Deserialising untrusted pickle data
def load_session_bad(data: bytes) -> dict:
    return pickle.loads(data)  # Arbitrary code execution on untrusted data!


# SAFE: Use JSON for data serialisation
def load_session(data: str) -> dict:
    session = json.loads(data)
    # Validate the structure before returning
    if not isinstance(session, dict):
        raise ValueError("Invalid session data")
    return session
```

**Rule**: Never use `pickle`, `marshal`, or `yaml.load` (without `Loader=yaml.SafeLoader`) on untrusted data.

### 8.2.5 Hardcoded Credentials (CWE-798)

Hardcoded passwords, API keys, and tokens in source code are frequently exposed via public repositories.

```python
import os

# VULNERABLE: Hardcoded credentials
def connect_bad():
    return DatabaseConnection(
        host="db.example.com",
        password="SuperSecret123!",  # Visible in source code, git history
    )


# SAFE: Read from environment variables
def connect():
    password = os.environ.get("DB_PASSWORD")
    if not password:
        raise EnvironmentError("DB_PASSWORD environment variable is not set")
    return DatabaseConnection(host=os.environ["DB_HOST"], password=password)
```

**Rule**: Credentials must never appear in source code. Use environment variables, a secrets manager (AWS Secrets Manager, HashiCorp Vault), or a `.env` file that is excluded from version control.

---
